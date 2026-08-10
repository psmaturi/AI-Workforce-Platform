"""Skills Repository — Database query layer for skills and employee skill data.

Responsibilities:
- Queries for skills, employee_skills, and role_skill_requirements.
- Calculates raw skill gap data (not business logic — that's in SkillGapService).

Integration:
- Used by SkillGapService and TrainingService.
"""

import time
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from app.database.models import Skill, EmployeeSkill, RoleSkillRequirement, JobRole
from app.utils.logger import logger


class SkillsRepository:
    """Data access layer for Skills and EmployeeSkills."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_employee_skills(self, employee_id: int) -> list[EmployeeSkill]:
        """All skills for a given employee with Skill details joined."""
        start = time.time()
        results = (
            self.db.query(EmployeeSkill)
            .options(joinedload(EmployeeSkill.skill))
            .filter(EmployeeSkill.employee_id == employee_id)
            .all()
        )
        logger.info(f"[SkillsRepo] get_employee_skills({employee_id}) → {len(results)} skills — {(time.time()-start)*1000:.1f}ms")
        return results

    def get_role_requirements(self, role_id: int) -> list[RoleSkillRequirement]:
        """All required skills for a given job role."""
        start = time.time()
        results = (
            self.db.query(RoleSkillRequirement)
            .options(joinedload(RoleSkillRequirement.skill))
            .filter(RoleSkillRequirement.role_id == role_id)
            .all()
        )
        logger.info(f"[SkillsRepo] get_role_requirements({role_id}) → {len(results)} reqs — {(time.time()-start)*1000:.1f}ms")
        return results

    def get_role_by_title(self, title: str) -> Optional[JobRole]:
        """Find a job role by title (case-insensitive partial match)."""
        return (
            self.db.query(JobRole)
            .filter(JobRole.title.ilike(f"%{title}%"), JobRole.is_active == True)
            .first()
        )

    def get_role_requirements_by_title(self, role_title: str) -> list[RoleSkillRequirement]:
        """Get skill requirements for a role specified by title."""
        role = self.get_role_by_title(role_title)
        if not role:
            return []
        return self.get_role_requirements(role.id)

    def get_skill_by_name(self, name: str) -> Optional[Skill]:
        """Find a skill by exact or partial name match."""
        return (
            self.db.query(Skill)
            .filter(Skill.name.ilike(f"%{name}%"), Skill.is_active == True)
            .first()
        )

    def get_skills_by_category(self, category: str) -> list[Skill]:
        """All skills in a given category."""
        return (
            self.db.query(Skill)
            .filter(Skill.category == category, Skill.is_active == True)
            .all()
        )

    def get_employee_skill_map(self, employee_id: int) -> dict[int, EmployeeSkill]:
        """Return a dict of {skill_id: EmployeeSkill} for fast gap lookup."""
        skills = self.get_employee_skills(employee_id)
        return {es.skill_id: es for es in skills}

    def count_skills(self) -> int:
        """Total active skill count."""
        from sqlalchemy import func
        return self.db.query(func.count(Skill.id)).filter(Skill.is_active == True).scalar() or 0
