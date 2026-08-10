"""Department Repository — Database query layer for department data."""

import time
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.models import Department, Employee, JobRole
from app.utils.logger import logger


class DepartmentRepository:
    """Data access layer for Department records."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, department_id: int) -> Optional[Department]:
        return self.db.query(Department).filter(
            Department.id == department_id, Department.is_active == True
        ).first()

    def get_by_name(self, name: str) -> Optional[Department]:
        return self.db.query(Department).filter(
            Department.name.ilike(f"%{name}%"), Department.is_active == True
        ).first()

    def get_by_code(self, code: str) -> Optional[Department]:
        return self.db.query(Department).filter(Department.code == code).first()

    def get_all(self) -> list[Department]:
        return self.db.query(Department).filter(Department.is_active == True).all()

    def get_employee_count(self, department_id: int) -> int:
        return (
            self.db.query(func.count(Employee.id))
            .filter(Employee.department_id == department_id, Employee.is_active == True)
            .scalar() or 0
        )

    def get_roles(self, department_id: int) -> list[JobRole]:
        return (
            self.db.query(JobRole)
            .filter(JobRole.department_id == department_id, JobRole.is_active == True)
            .all()
        )

    def get_avg_performance(self, department_id: int) -> float:
        """Average last_rating_score across all active employees in department."""
        result = (
            self.db.query(func.avg(Employee.last_rating_score))
            .filter(
                Employee.department_id == department_id,
                Employee.is_active == True,
                Employee.last_rating_score.isnot(None),
            )
            .scalar()
        )
        return round(float(result), 2) if result else 0.0
