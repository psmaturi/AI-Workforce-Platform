"""Repositories package."""
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.skills_repository import SkillsRepository
from app.repositories.training_repository import TrainingRepository
from app.repositories.department_repository import DepartmentRepository

__all__ = [
    "EmployeeRepository",
    "SkillsRepository",
    "TrainingRepository",
    "DepartmentRepository",
]
