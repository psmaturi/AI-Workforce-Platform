"""Employee Repository — Database query layer for employee data.

Responsibilities:
- All raw SQL/ORM queries for the employees table.
- No business logic — pure data access.
- Returns ORM model instances or None.

Integration:
- Used exclusively by EmployeeService.
- Receives SQLAlchemy Session via dependency injection.
"""

import time
from typing import Optional
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload
from app.database.models import Employee, Department, JobRole
from app.utils.logger import logger


class EmployeeRepository:
    """Data access layer for Employee records."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, employee_id: int) -> Optional[Employee]:
        """Fetch employee by primary key with department and role preloaded."""
        start = time.time()
        emp = (
            self.db.query(Employee)
            .options(
                joinedload(Employee.department),
                joinedload(Employee.role),
            )
            .filter(Employee.id == employee_id, Employee.is_active == True)
            .first()
        )
        logger.info(f"[EmployeeRepo] get_by_id({employee_id}) — {(time.time()-start)*1000:.1f}ms")
        return emp

    def get_by_employee_number(self, employee_number: str) -> Optional[Employee]:
        """Fetch employee by employee number (e.g. 'EMP001')."""
        start = time.time()
        emp = (
            self.db.query(Employee)
            .options(joinedload(Employee.department), joinedload(Employee.role))
            .filter(Employee.employee_number == employee_number, Employee.is_active == True)
            .first()
        )
        logger.info(f"[EmployeeRepo] get_by_number({employee_number}) — {(time.time()-start)*1000:.1f}ms")
        return emp

    def search_by_name(self, name: str, limit: int = 10) -> list[Employee]:
        """Full-text search on employee name (case-insensitive)."""
        start = time.time()
        results = (
            self.db.query(Employee)
            .options(joinedload(Employee.department), joinedload(Employee.role))
            .filter(
                Employee.is_active == True,
                Employee.name.ilike(f"%{name}%"),
            )
            .limit(limit)
            .all()
        )
        logger.info(f"[EmployeeRepo] search_by_name('{name}') → {len(results)} — {(time.time()-start)*1000:.1f}ms")
        return results

    def get_by_department(self, department_id: int) -> list[Employee]:
        """All active employees in a department."""
        start = time.time()
        results = (
            self.db.query(Employee)
            .options(joinedload(Employee.role))
            .filter(Employee.department_id == department_id, Employee.is_active == True)
            .all()
        )
        logger.info(f"[EmployeeRepo] get_by_department({department_id}) → {len(results)} — {(time.time()-start)*1000:.1f}ms")
        return results

    def get_with_skills(self, employee_id: int) -> Optional[Employee]:
        """Fetch employee with all EmployeeSkill records and Skill details preloaded."""
        from app.database.models import EmployeeSkill, Skill
        start = time.time()
        emp = (
            self.db.query(Employee)
            .options(
                joinedload(Employee.department),
                joinedload(Employee.role),
                joinedload(Employee.skills).joinedload(EmployeeSkill.skill),
            )
            .filter(Employee.id == employee_id, Employee.is_active == True)
            .first()
        )
        logger.info(f"[EmployeeRepo] get_with_skills({employee_id}) — {(time.time()-start)*1000:.1f}ms")
        return emp

    def get_with_full_profile(self, employee_id: int) -> Optional[Employee]:
        """Fetch employee with skills, training, reviews, and career goals preloaded."""
        from app.database.models import EmployeeSkill, Skill, EmployeeTraining, TrainingCourse
        start = time.time()
        emp = (
            self.db.query(Employee)
            .options(
                joinedload(Employee.department),
                joinedload(Employee.role),
                joinedload(Employee.manager),
                joinedload(Employee.skills).joinedload(EmployeeSkill.skill),
                joinedload(Employee.training_records).joinedload(EmployeeTraining.course),
                joinedload(Employee.performance_reviews),
                joinedload(Employee.career_goals),
            )
            .filter(Employee.id == employee_id, Employee.is_active == True)
            .first()
        )
        logger.info(f"[EmployeeRepo] get_with_full_profile({employee_id}) — {(time.time()-start)*1000:.1f}ms")
        return emp

    def get_direct_reports(self, manager_id: int) -> list[Employee]:
        """Get all direct reports for a manager."""
        return (
            self.db.query(Employee)
            .filter(Employee.manager_id == manager_id, Employee.is_active == True)
            .all()
        )

    def count_by_department(self, department_id: int) -> int:
        """Count active employees in a department."""
        return (
            self.db.query(func.count(Employee.id))
            .filter(Employee.department_id == department_id, Employee.is_active == True)
            .scalar() or 0
        )

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Employee]:
        """Paginated list of all active employees."""
        return (
            self.db.query(Employee)
            .options(joinedload(Employee.department), joinedload(Employee.role))
            .filter(Employee.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )
