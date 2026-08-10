"""Career Service Module.

Responsibilities:
- Handles career goals and roadmaps.
"""

from typing import Optional, List, Dict, Any
from app.repositories.employee_repository import EmployeeRepository
from app.database.models import CareerGoal, GoalStatus
from app.utils.logger import logger


class CareerService:
    """Service layer for Career Goals and Roadmaps."""

    def __init__(self, employee_repo: EmployeeRepository):
        self.employee_repo = employee_repo

    def get_career_goals(self, employee_id: int) -> List[Dict[str, Any]]:
        """Fetch career goals for an employee."""
        emp = self.employee_repo.get_with_full_profile(employee_id)
        if not emp:
            return []
            
        return [
            {
                "target_role_name": g.target_role_name,
                "timeline_months": g.target_timeline_months,
                "progress_pct": g.current_progress_pct,
                "status": g.status.value
            }
            for g in emp.career_goals
        ]
