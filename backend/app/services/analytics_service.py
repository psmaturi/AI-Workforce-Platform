"""Analytics Service Module.

Responsibilities:
- Manager-level analytics.
"""

from typing import Optional, List, Dict, Any
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.department_repository import DepartmentRepository
from app.utils.logger import logger


class AnalyticsService:
    """Service layer for Manager Analytics."""

    def __init__(self, employee_repo: EmployeeRepository, department_repo: DepartmentRepository):
        self.employee_repo = employee_repo
        self.department_repo = department_repo

    def get_team_overview(self, manager_id: int) -> Dict[str, Any]:
        """Get an overview of a manager's direct reports."""
        reports = self.employee_repo.get_direct_reports(manager_id)
        
        # Calculate some basic stats
        total_reports = len(reports)
        avg_experience = sum(e.years_experience for e in reports) / total_reports if total_reports > 0 else 0
        
        return {
            "manager_id": manager_id,
            "total_direct_reports": total_reports,
            "average_experience_years": round(avg_experience, 1),
            "reports": [
                {
                    "employee_number": r.employee_number,
                    "name": r.name,
                    "role": r.role.title if r.role else "N/A"
                }
                for r in reports
            ]
        }
