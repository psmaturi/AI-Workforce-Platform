import csv
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Ensure project root is in PYTHONPATH
sys.path.append(os.getcwd())

from app.database.database import SessionLocal, engine, Base
from app.database.models import (
    Department, JobRole, Skill, Employee, EmployeeSkill,
    TrainingCourse, EmployeeTraining, RoleSkillRequirement,
    PerformanceReview, CareerGoal, SkillLevel, EmploymentStatus,
    TrainingStatus, TrainingMode, PerformanceRating, GoalStatus,
    WorkforceForecast, SkillPrediction, EmployeeReadiness, SkillRisk
)

def parse_date(date_str: str):
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            return datetime.strptime(date_str, "%Y-%m-%d")

def import_data():
    print("Re-creating database schemas...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database schemas re-created successfully.")
    
    db = SessionLocal()
    
    try:
        # 1. Import Departments
        print("\nIngesting Departments...")
        depts_count = 0
        with open("data/raw/departments.csv", mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                dept = Department(
                    id=int(row["id"]),
                    name=row["name"].strip(),
                    code=row["code"].strip(),
                    description=row["description"].strip() or None,
                    head_name=row["head_name"].strip() or None,
                    location=row["location"].strip() or None,
                    is_active=row["is_active"].lower() == "true"
                )
                db.add(dept)
                depts_count += 1
        db.commit()
        print(f"Successfully ingested {depts_count} departments.")

        # 2. Import Job Roles
        print("\nIngesting Job Roles...")
        roles_count = 0
        with open("data/raw/job_roles.csv", mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                role = JobRole(
                    id=int(row["id"]),
                    title=row["title"].strip(),
                    department_id=int(row["department_id"]),
                    grade=int(row["grade"]),
                    track=row["track"].strip(),
                    min_experience_years=int(row["min_experience_years"]),
                    description=row["description"].strip() or None,
                    preferred_certifications=row["preferred_certifications"].strip() or None,
                    is_active=row["is_active"].lower() == "true"
                )
                db.add(role)
                roles_count += 1
        db.commit()
        print(f"Successfully ingested {roles_count} job roles.")

        # 3. Import Skills
        print("\nIngesting Skills...")
        skills_count = 0
        with open("data/raw/skills.csv", mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                skill = Skill(
                    id=int(row["id"]),
                    name=row["name"].strip(),
                    category=row["category"].strip(),
                    subcategory=row["subcategory"].strip() or None,
                    description=row["description"].strip() or None,
                    future_demand=row["future_demand"].strip(),
                    criticality=row["criticality"].strip(),
                    is_active=row["is_active"].lower() == "true"
                )
                db.add(skill)
                skills_count += 1
        db.commit()
        print(f"Successfully ingested {skills_count} skills.")

        # 4. Import Training Courses
        print("\nIngesting Training Courses...")
        courses_count = 0
        with open("data/raw/training_courses.csv", mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                course = TrainingCourse(
                    id=int(row["id"]),
                    code=row["code"].strip(),
                    name=row["name"].strip(),
                    description=row["description"].strip() or None,
                    category=row["category"].strip(),
                    subcategory=row["subcategory"].strip() or None,
                    duration_hours=float(row["duration_hours"]),
                    difficulty=row["difficulty"].strip(),
                    mode=TrainingMode(row["mode"].strip()),
                    provider=row["provider"].strip(),
                    skills_covered=row["skills_covered"].strip() or None,
                    prerequisites=row["prerequisites"].strip() or None,
                    target_grades=row["target_grades"].strip() or None,
                    is_mandatory=row["is_mandatory"].lower() == "true",
                    pass_score=int(row["pass_score"]),
                    is_active=row["is_active"].lower() == "true"
                )
                db.add(course)
                courses_count += 1
        db.commit()
        print(f"Successfully ingested {courses_count} training courses.")

        # 5. Import Employees (leaving manager_id empty for now to link later)
        print("\nIngesting Employees...")
        emps_count = 0
        with open("data/raw/employees.csv", mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                emp = Employee(
                    id=int(row["id"]),
                    employee_number=row["employee_number"].strip(),
                    data_source=row["data_source"].strip(),
                    name=row["name"].strip(),
                    email=row["email"].strip(),
                    department_id=int(row["department_id"]),
                    role_id=int(row["role_id"]),
                    manager_id=None,
                    grade=int(row["grade"]),
                    years_experience=float(row["years_experience"]),
                    years_in_company=float(row["years_in_company"]),
                    location=row["location"].strip(),
                    employment_status=EmploymentStatus(row["employment_status"].strip()),
                    performance_rating=row["performance_rating"].strip() or None,
                    last_rating_score=float(row["last_rating_score"]) if row["last_rating_score"] else None,
                    phone=row["phone"].strip() or None,
                    is_active=row["is_active"].lower() == "true"
                )
                db.add(emp)
                emps_count += 1
        db.commit()
        print(f"Successfully ingested {emps_count} employees.")

        # Link Managers (Hierarchical linking)
        print("\nLinking Employee Managers...")
        all_emps = db.query(Employee).all()
        # Create map for fast lookup
        emp_map = {e.id: e for e in all_emps}
        
        # We explicitly set specific manager relationships for mock presets:
        # Gareth Williams (id 1) reports to Priya Sharma (id 2)
        # Priya Sharma (id 2) reports to Head of Department (we will find a suitable employee)
        # James Okonkwo (id 3) reports to a Manager/Head of department 10
        
        # Link mock presets
        emp_map[1].manager_id = 2  # Gareth reports to Priya
        
        # Find a suitable manager for Priya (EMP1001, id 2): must be in dept 1 and have grade > 8 (e.g. grade 9 Head)
        dept1_leaders = [e for e in all_emps if e.department_id == 1 and e.grade > 8]
        if dept1_leaders:
            emp_map[2].manager_id = dept1_leaders[0].id
        else:
            # Fallback: any other higher grade
            dept1_leaders_alt = [e for e in all_emps if e.department_id == 1 and e.grade > 7 and e.id != 2]
            if dept1_leaders_alt:
                emp_map[2].manager_id = dept1_leaders_alt[0].id
                
        # Find a suitable manager for James (EMP1002, id 3): dept 10 and grade > 7
        dept10_leaders = [e for e in all_emps if e.department_id == 10 and e.grade > 7 and e.id != 3]
        if dept10_leaders:
            emp_map[3].manager_id = dept10_leaders[0].id
            
        # Link other employees to managers in the same department with higher grades
        for e in all_emps:
            if e.id in [1, 2, 3]:
                continue # Already linked
                
            possible_managers = [m for m in all_emps if m.department_id == e.department_id and m.grade > e.grade]
            if possible_managers:
                e.manager_id = possible_managers[0].id
            else:
                # If no higher grade in same dept, link to Head of another dept or leave empty (e.g. heads of departments)
                pass
                
        db.commit()
        print("Employee manager links successfully resolved.")

        # 6. Import Employee Skills
        print("\nIngesting Employee Skills...")
        emp_skills_count = 0
        with open("data/raw/employee_skills.csv", mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                lvl_str = row["level"].strip()
                lvl = SkillLevel(lvl_str)
                
                emp_skill = EmployeeSkill(
                    id=int(row["id"]),
                    employee_id=int(row["employee_id"]),
                    skill_id=int(row["skill_id"]),
                    level=lvl,
                    years_experience=float(row["years_experience"]),
                    is_certified=row["is_certified"].lower() == "true",
                    certification_name=row["certification_name"].strip() or None,
                    last_assessed=parse_date(row["last_assessed"]),
                    notes=row["notes"].strip() or None
                )
                db.add(emp_skill)
                emp_skills_count += 1
        db.commit()
        print(f"Successfully ingested {emp_skills_count} employee-skill relationships.")

        # 7. Import Employee Training Records
        print("\nIngesting Employee Training Records...")
        emp_training_count = 0
        with open("data/raw/employee_training.csv", mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                status = TrainingStatus(row["status"].strip())
                emp_train = EmployeeTraining(
                    id=int(row["id"]),
                    employee_id=int(row["employee_id"]),
                    course_id=int(row["course_id"]),
                    status=status,
                    score=float(row["score"]) if row["score"] else None,
                    completion_date=parse_date(row["completion_date"]),
                    expiry_date=parse_date(row["expiry_date"]),
                    hours_completed=float(row["hours_completed"]),
                    certificate_issued=row["certificate_issued"].lower() == "true",
                    notes=row["notes"].strip() or None
                )
                db.add(emp_train)
                emp_training_count += 1
        db.commit()
        print(f"Successfully ingested {emp_training_count} employee-training records.")

        # 8. Import Role Skill Requirements
        print("\nIngesting Role Skill Requirements...")
        role_skills_count = 0
        with open("data/raw/role_skill_requirements.csv", mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                lvl = SkillLevel(row["required_level"].strip())
                role_skill = RoleSkillRequirement(
                    id=int(row["id"]),
                    role_id=int(row["role_id"]),
                    skill_id=int(row["skill_id"]),
                    required_level=lvl,
                    is_mandatory=row["is_mandatory"].lower() == "true",
                    notes=row["notes"].strip() or None
                )
                db.add(role_skill)
                role_skills_count += 1
        db.commit()
        print(f"Successfully ingested {role_skills_count} role-skill requirements.")

        # 9. Import Career Goals
        print("\nIngesting Career Goals...")
        goals_count = 0
        with open("data/raw/career_goals.csv", mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                status = GoalStatus(row["status"].strip())
                goal = CareerGoal(
                    id=int(row["id"]),
                    employee_id=int(row["employee_id"]),
                    target_role_id=int(row["target_role_id"]) if row["target_role_id"] else None,
                    target_role_name=row["target_role_name"].strip(),
                    target_timeline_months=int(row["target_timeline_months"]),
                    current_progress_pct=float(row["current_progress_pct"]),
                    status=status,
                    notes=row["notes"].strip() or None
                )
                db.add(goal)
                goals_count += 1
        db.commit()
        print(f"Successfully ingested {goals_count} career goals.")

        # 10. Import Performance Reviews
        print("\nIngesting Performance Reviews...")
        reviews_count = 0
        with open("data/raw/performance_reviews.csv", mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rating = PerformanceRating(row["rating"].strip())
                review = PerformanceReview(
                    id=int(row["id"]),
                    employee_id=int(row["employee_id"]),
                    review_cycle=row["review_cycle"].strip(),
                    rating=rating,
                    score=float(row["score"]),
                    strengths=row["strengths"].strip() or None,
                    improvement_areas=row["improvement_areas"].strip() or None,
                    manager_comments=row["manager_comments"].strip() or None,
                    reviewer_name=row["reviewer_name"].strip() or None,
                    review_date=parse_date(row["review_date"]),
                    is_final=row["is_final"].lower() == "true"
                )
                db.add(review)
                reviews_count += 1
        db.commit()
        print(f"Successfully ingested {reviews_count} performance reviews.")

        # 11. Import Forecasting & Risks
        print("\nIngesting Forecasting and Risks...")
        
        forecast_count = 0
        with open("data/raw/workforce_forecasts.csv", mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                forecast = WorkforceForecast(
                    id=int(row["id"]),
                    department_id=int(row["department_id"]),
                    target_year=int(row["target_year"]),
                    current_headcount=int(row["current_headcount"]),
                    projected_headcount=int(row["projected_headcount"]),
                    required_headcount=int(row["required_headcount"]),
                    gap=int(row["gap"])
                )
                db.add(forecast)
                forecast_count += 1
                
        pred_count = 0
        with open("data/raw/skill_predictions.csv", mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                pred = SkillPrediction(
                    id=int(row["id"]),
                    skill_id=int(row["skill_id"]),
                    target_year=int(row["target_year"]),
                    demand_category=row["demand_category"].strip(),
                    confidence_score=float(row["confidence_score"])
                )
                db.add(pred)
                pred_count += 1
                
        readiness_count = 0
        with open("data/raw/employee_readiness.csv", mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                readiness = EmployeeReadiness(
                    id=int(row["id"]),
                    employee_id=int(row["employee_id"]),
                    target_role_id=int(row["target_role_id"]),
                    readiness_score=float(row["readiness_score"]),
                    classification=row["classification"].strip()
                )
                db.add(readiness)
                readiness_count += 1
                
        risk_count = 0
        with open("data/raw/skill_risks.csv", mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                risk = SkillRisk(
                    id=int(row["id"]),
                    department_id=int(row["department_id"]),
                    skill_id=int(row["skill_id"]) if row["skill_id"] else None,
                    risk_type=row["risk_type"].strip(),
                    risk_level=row["risk_level"].strip(),
                    description=row["description"].strip() or None
                )
                db.add(risk)
                risk_count += 1
                
        db.commit()
        print(f"Successfully ingested forecasts ({forecast_count}), predictions ({pred_count}), readiness ({readiness_count}), and risks ({risk_count}).")

        print("\nAll raw CSV data ingested successfully!")
        
    except Exception as e:
        print(f"\nError during ingestion: {e}", file=sys.stderr)
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import_data()
