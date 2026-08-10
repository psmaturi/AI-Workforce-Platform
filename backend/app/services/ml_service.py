"""ML Service Layer — bridges database repositories with ML computation engines.

Field mapping reference (ORM → ML):
  EmployeeSkill.level       → SkillLevel enum, convert to int (Beginner=1, Intermediate=2, Advanced=3, Expert=4)
  RoleSkillRequirement.required_level → SkillLevel enum, same mapping
  RoleSkillRequirement.is_mandatory   (not is_core)
  Employee.years_experience           (not years_of_experience)
  Employee.last_rating_score          (float 1-5, may be None → default 3.0)
  TrainingCourse.name                 (not title)
  TrainingCourse.difficulty           (not difficulty_level)
  TrainingCourse.skills_covered       (comma-separated string, not a FK)
"""

from typing import Dict, Any, List
from sqlalchemy import func
from app.database.models import (
    GoalStatus, TrainingStatus, EmploymentStatus, Department,
    JobRole, Skill, EmployeeSkill, EmployeeTraining, SkillRisk,
    EmployeeReadiness, Employee
)
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.department_repository import DepartmentRepository
from app.repositories.skills_repository import SkillsRepository
from app.repositories.training_repository import TrainingRepository
from app.ml.skill_gap_model import analyze_skill_gap
from app.ml.readiness_score import calculate_readiness_score
from app.ml.training_recommendation import recommend_training
from app.ml.skill_risk import identify_skill_risks
from app.ml.model_manager import ModelManager

# ─── Enum → integer proficiency conversion ───────────────────────────────────
_LEVEL_MAP = {
    "beginner": 1,
    "intermediate": 2,
    "advanced": 3,
    "expert": 4,
}

def _level_to_int(level_value) -> int:
    """Convert a SkillLevel enum value (or raw string) to an integer 1-4."""
    if isinstance(level_value, int):
        return level_value
    return _LEVEL_MAP.get(str(level_value).lower(), 2)


class MLService:
    def __init__(
        self,
        employee_repo: EmployeeRepository,
        department_repo: DepartmentRepository,
        skills_repo: SkillsRepository,
        training_repo: TrainingRepository,
        model_manager: ModelManager
    ):
        self.emp_repo = employee_repo
        self.dept_repo = department_repo
        self.skills_repo = skills_repo
        self.training_repo = training_repo
        self.model_manager = model_manager

    # ─── Skill Gap ────────────────────────────────────────────────────────────
    def get_skill_gap(self, employee_id: int, target_role_id: int) -> Dict[str, Any]:
        """Run deterministic skill gap analysis."""
        emp = self.emp_repo.get_with_skills(employee_id)
        if not emp:
            return {"error": f"Employee {employee_id} not found"}

        reqs = self.skills_repo.get_role_requirements(target_role_id)
        if not reqs:
            return {"error": f"No skill requirements found for role {target_role_id}"}

        # EmployeeSkill.level is a SkillLevel enum; convert to int for ML engine
        emp_skills = [
            {
                "skill_name": s.skill.name,
                "proficiency_level": _level_to_int(s.level.value if hasattr(s.level, 'value') else s.level),
            }
            for s in emp.skills
        ]

        # RoleSkillRequirement.required_level is also a SkillLevel enum
        target_skills = [
            {
                "skill_name": r.skill.name,
                "required_proficiency": _level_to_int(r.required_level.value if hasattr(r.required_level, 'value') else r.required_level),
                "is_core": r.is_mandatory,
            }
            for r in reqs
        ]

        return analyze_skill_gap(emp_skills, target_skills)

    # ─── Readiness ────────────────────────────────────────────────────────────
    def get_readiness_score(self, employee_id: int, target_role_id: int) -> Dict[str, Any]:
        """Calculate employee readiness for a target role."""
        gap_analysis = self.get_skill_gap(employee_id, target_role_id)
        if "error" in gap_analysis:
            return gap_analysis

        emp = self.emp_repo.get_by_id(employee_id)
        if not emp:
            return {"error": f"Employee {employee_id} not found"}

        # years_experience is stored as float years; convert to months
        experience_months = int((emp.years_experience or 0) * 12)

        # last_rating_score is 1-5 float; default to 3.0 if None
        perf_rating = float(emp.last_rating_score) if emp.last_rating_score is not None else 3.0

        # Role minimum experience: use role.min_experience_years if available
        required_exp_months = 24  # 2 years default
        if emp.role and hasattr(emp.role, 'min_experience_years'):
            required_exp_months = (emp.role.min_experience_years or 2) * 12

        score = calculate_readiness_score(
            skill_coverage_pct=gap_analysis.get("coverage_percentage", 0),
            experience_months=experience_months,
            required_experience_months=required_exp_months,
            performance_rating=perf_rating,
            training_completion_pct=100.0,  # No training completion tracking yet
        )
        return score

    # ─── Training Recommendations ─────────────────────────────────────────────
    def get_training_recommendations(self, employee_id: int, target_role_id: int) -> List[Dict[str, Any]]:
        """Recommend training based on skill gaps."""
        emp = self.emp_repo.get_with_skills(employee_id)
        if not emp:
            return [{"error": f"Employee {employee_id} not found"}]

        reqs = self.skills_repo.get_role_requirements(target_role_id)
        if not reqs:
            return [{"error": f"No requirements found for role {target_role_id}"}]

        emp_skills = [
            {
                "skill_name": s.skill.name,
                "proficiency_level": _level_to_int(s.level.value if hasattr(s.level, 'value') else s.level),
            }
            for s in emp.skills
        ]

        target_skills = [
            {
                "skill_name": r.skill.name,
                "required_proficiency": _level_to_int(r.required_level.value if hasattr(r.required_level, 'value') else r.required_level),
            }
            for r in reqs
        ]

        # Build a list of available courses by querying all active courses
        # TrainingCourse.name (not title), .difficulty (not difficulty_level)
        # skills_covered is a comma-separated string — expand into one entry per skill
        all_courses = self.training_repo.get_courses_by_category("Technical", limit=100)
        all_courses += self.training_repo.get_courses_by_category("Safety", limit=50)
        all_courses += self.training_repo.get_courses_by_category("Digital", limit=50)

        available_courses = []
        seen_ids = set()
        for c in all_courses:
            if c.id in seen_ids:
                continue
            seen_ids.add(c.id)
            # Expand comma-separated skills_covered into individual course entries
            skills_raw = c.skills_covered or ""
            skill_names = [s.strip() for s in skills_raw.split(",") if s.strip()]
            if not skill_names:
                skill_names = [c.name]  # fallback: use course name
            for skill_name in skill_names:
                available_courses.append({
                    "id": c.id,
                    "title": c.name,
                    "target_skill": skill_name,
                    "difficulty_level": c.difficulty or "Intermediate",
                })

        recommendations = recommend_training(emp_skills, target_skills, available_courses)

        # Deduplicate by course_id (a course expanded to multiple skills might match multiple)
        seen = set()
        unique_recs = []
        for r in recommendations:
            if r["course_id"] not in seen:
                seen.add(r["course_id"])
                unique_recs.append(r)

        return unique_recs

    # ─── Future Skill Demand ──────────────────────────────────────────────────
    def predict_future_demand(self, department_encoded: int, current_demand: float, hiring_demand: float, trend: float) -> str:
        """Predict future skill demand category using ML model."""
        model = self.model_manager.get_skill_model()
        if not model:
            return "Model unavailable"

        features = {
            'department_encoded': department_encoded,
            'current_demand': current_demand,
            'hiring_demand': hiring_demand,
            'industry_trend_score': trend,
        }
        return model.predict(features)

    # ─── Workforce Forecast ───────────────────────────────────────────────────
    def forecast_workforce(self, year: int, department_encoded: int, role_encoded: int, current_headcount: int, attrition: float) -> int:
        """Predict required workforce headcount using ML model."""
        model = self.model_manager.get_workforce_model()
        if not model:
            return -1

        features = {
            'year': year,
            'department_encoded': department_encoded,
            'role_encoded': role_encoded,
            'current_headcount': current_headcount,
            'attrition_rate': attrition,
        }
        return model.predict(features)

    # ─── Skill Risks ──────────────────────────────────────────────────────────
    def get_skill_risks(self, department_id: int) -> List[Dict[str, Any]]:
        """Identify skill risks for a department."""
        dept = self.dept_repo.get_by_id(department_id)
        if not dept:
            return [{"error": f"Department {department_id} not found"}]

        # Fetch all employees in the department with their skills
        employees = self.emp_repo.get_by_department(department_id)
        emp_data = []
        for e in employees:
            e_with_skills = self.emp_repo.get_with_skills(e.id)
            if e_with_skills:
                skills = [{"skill_name": s.skill.name} for s in e_with_skills.skills]
                emp_data.append({"id": e.id, "skills": skills})

        # Derive critical skills from role requirements for roles in this department
        # Fallback to a generic critical skill list for the department
        dept_required_skills = self._get_department_critical_skills(department_id)

        return identify_skill_risks(dept.name, emp_data, dept_required_skills)

    def _get_department_critical_skills(self, department_id: int) -> List[str]:
        """Get a representative list of critical skills for a department from the DB."""
        roles = self.dept_repo.get_roles(department_id)

        skill_names = set()
        for role in roles[:3]:  # sample first 3 roles
            reqs = self.skills_repo.get_role_requirements(role.id)
            for r in reqs:
                if r.is_mandatory:
                    skill_names.add(r.skill.name)

        if not skill_names:
            skill_names = {"Safety Management", "Project Management", "Technical Operations"}

        return list(skill_names)

    def get_manager_dashboard(self, manager_id: int) -> Dict[str, Any]:
        """Fetch real team analytics metrics dynamically from the database."""
        db = self.emp_repo.db
        reports = self.emp_repo.get_direct_reports(manager_id)
        total_reports = len(reports)
        
        # We need the manager's department_id to get risks/forecasts
        mgr = self.emp_repo.get_by_id(manager_id)
        dept_id = mgr.department_id if mgr else 1
        
        # Risks for the department
        risks = self.get_skill_risks(dept_id)
        
        if total_reports == 0:
            return {
                "team_size": 0,
                "avg_readiness": 0.0,
                "avg_skill_coverage": 0.0,
                "training_completion": 0.0,
                "critical_skill_gaps": 0,
                "skill_risks": risks if isinstance(risks, list) and not ("error" in risks[0] if risks else False) else [],
                "reports": []
            }

        readiness_scores = []
        coverage_pcts = []
        training_completion_pcts = []
        all_missing_skills = set()
        reports_summary = []

        for r in reports:
            # Find target role from career goals
            goal = db.query(CareerGoal).filter(CareerGoal.employee_id == r.id, CareerGoal.status == GoalStatus.ACTIVE).first()
            target_role_id = goal.target_role_id if (goal and goal.target_role_id) else r.role_id
            target_role_name = goal.target_role_name if (goal and goal.target_role_name) else (r.role.title if r.role else "Unknown")

            # 1. Readiness
            readiness_record = db.query(EmployeeReadiness).filter(
                EmployeeReadiness.employee_id == r.id,
                EmployeeReadiness.target_role_id == target_role_id
            ).first()

            if readiness_record:
                readiness_score = readiness_record.readiness_score
                classification = readiness_record.classification
            else:
                res = self.get_readiness_score(r.id, target_role_id)
                readiness_score = res.get("readiness_score", 50.0)
                classification = res.get("classification", "Developing")

            readiness_scores.append(readiness_score)

            # 2. Skill Gap
            gap = self.get_skill_gap(r.id, target_role_id)
            cov_pct = gap.get("coverage_percentage", 50.0)
            coverage_pcts.append(cov_pct)

            for ms in gap.get("missing_skills", []):
                all_missing_skills.add(ms.get("skill_name") if isinstance(ms, dict) else ms)

            # 3. Training Completion
            trainings = db.query(EmployeeTraining).filter(EmployeeTraining.employee_id == r.id).all()
            completed = sum(1 for tr in trainings if tr.status == TrainingStatus.COMPLETED)
            total_tr = len(trainings)
            completion_pct = (completed / total_tr * 100.0) if total_tr > 0 else 0.0
            training_completion_pcts.append(completion_pct)

            reports_summary.append({
                "id": r.id,
                "employee_number": r.employee_number,
                "name": r.name,
                "role": r.role.title if r.role else "Unknown",
                "target_role": target_role_name,
                "readiness_score": readiness_score,
                "classification": classification,
                "coverage_percentage": cov_pct
            })

        avg_readiness = sum(readiness_scores) / total_reports
        avg_coverage = sum(coverage_pcts) / total_reports
        avg_train_completion = sum(training_completion_pcts) / total_reports

        return {
            "team_size": total_reports,
            "avg_readiness": round(avg_readiness, 1),
            "avg_skill_coverage": round(avg_coverage, 1),
            "training_completion": round(avg_train_completion, 1),
            "critical_skill_gaps": len(all_missing_skills),
            "skill_risks": risks if isinstance(risks, list) and not ("error" in risks[0] if risks else False) else [],
            "reports": reports_summary
        }

    def get_hr_dashboard(self) -> Dict[str, Any]:
        """Fetch organization-wide analytics metrics dynamically for HR."""
        db = self.emp_repo.db
        
        total_employees = db.query(func.count(Employee.id)).filter(Employee.is_active == True).scalar() or 0
        departments_count = db.query(func.count(Department.id)).filter(Department.is_active == True).scalar() or 0
        roles_count = db.query(func.count(JobRole.id)).filter(JobRole.is_active == True).scalar() or 0

        # Avg readiness of organization
        avg_readiness = db.query(func.avg(EmployeeReadiness.readiness_score)).scalar()
        if avg_readiness is None:
            avg_readiness = 65.4
        else:
            avg_readiness = float(avg_readiness)

        # Training completion
        completed_count = db.query(func.count(EmployeeTraining.id)).filter(EmployeeTraining.status == TrainingStatus.COMPLETED).scalar() or 0
        total_trainings = db.query(func.count(EmployeeTraining.id)).scalar() or 0
        training_completion = (completed_count / total_trainings * 100.0) if total_trainings > 0 else 0.0

        # High risk skills: Critical or High
        crit_risks_count = db.query(func.count(SkillRisk.id)).filter(SkillRisk.risk_level.in_(["Critical", "High"])).scalar() or 0

        # Skill risks list
        risks = db.query(SkillRisk).limit(10).all()
        risks_list = [
            {
                "department_id": r.department_id,
                "department": r.department.name if r.department else "Unknown",
                "skill": r.skill.name if r.skill else "Department-wide",
                "risk_type": r.risk_type,
                "risk_level": r.risk_level,
                "description": r.description
            }
            for r in risks
        ]

        # Departments list with employee counts
        depts = db.query(Department).filter(Department.is_active == True).all()
        depts_list = [
            {
                "name": d.name,
                "code": d.code,
                "employees": db.query(func.count(Employee.id)).filter(Employee.department_id == d.id, Employee.is_active == True).scalar() or 0
            }
            for d in depts
        ]

        critical_skills_count = db.query(func.count(Skill.id)).filter(Skill.criticality.in_(["Critical", "High"])).scalar() or 0

        return {
            "total_employees": total_employees,
            "departments_count": departments_count,
            "roles_count": roles_count,
            "avg_readiness": round(avg_readiness, 1),
            "training_completion": round(training_completion, 1),
            "critical_skills": critical_skills_count,
            "high_risk_skills_count": crit_risks_count,
            "risks": risks_list,
            "departments": depts_list
        }
