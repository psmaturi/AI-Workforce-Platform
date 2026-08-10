"""Skill Gap Service Module.

Responsibilities:
- Calculates skill gaps between employee and roles.
"""

from typing import Optional, List, Dict, Any
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.skills_repository import SkillsRepository
from app.database.models import SkillLevel
from app.utils.logger import logger


class SkillGapService:
    """Service layer for identifying Skill Gaps."""

    def __init__(self, employee_repo: EmployeeRepository, skills_repo: SkillsRepository):
        self.employee_repo = employee_repo
        self.skills_repo = skills_repo

    def _level_to_int(self, level: SkillLevel) -> int:
        mapping = {
            SkillLevel.BEGINNER: 1,
            SkillLevel.INTERMEDIATE: 2,
            SkillLevel.ADVANCED: 3,
            SkillLevel.EXPERT: 4
        }
        return mapping.get(level, 0)

    def analyze_gap(self, employee_id: int, target_role_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Analyze gap between employee's current skills and a target role.
        If target_role_id is None, uses their current role.
        """
        emp = self.employee_repo.get_with_skills(employee_id)
        if not emp:
            logger.warning(f"Employee {employee_id} not found for skill gap analysis.")
            return None

        role_id_to_check = target_role_id or emp.role_id
        
        # Get requirements for role
        requirements = self.skills_repo.get_role_requirements(role_id_to_check)
        
        current_skills_map = {es.skill_id: es.level for es in emp.skills}
        
        missing_skills = []
        upgrade_skills = []
        matched_skills = []
        
        for req in requirements:
            req_skill_id = req.skill_id
            req_level = req.required_level
            
            if req_skill_id not in current_skills_map:
                missing_skills.append({
                    "skill_name": req.skill.name,
                    "required_level": req_level.value,
                    "is_mandatory": req.is_mandatory
                })
            else:
                emp_level = current_skills_map[req_skill_id]
                if self._level_to_int(emp_level) < self._level_to_int(req_level):
                    upgrade_skills.append({
                        "skill_name": req.skill.name,
                        "current_level": emp_level.value,
                        "required_level": req_level.value,
                        "is_mandatory": req.is_mandatory
                    })
                else:
                    matched_skills.append(req.skill.name)

        return {
            "employee_name": emp.name,
            "target_role_id": role_id_to_check,
            "missing_skills": missing_skills,
            "upgrade_skills": upgrade_skills,
            "matched_skills": matched_skills,
            "gap_score": len(missing_skills) * 2 + len(upgrade_skills)
        }
