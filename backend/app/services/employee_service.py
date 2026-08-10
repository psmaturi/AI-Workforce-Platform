"""Employee Service Module.

Responsibilities:
- Contains business logic related to employees.
- Uses EmployeeRepository and DepartmentRepository for data access.

Integration:
- Injected into LangGraph tools (e.g. Employee Search, Profile).
- Used by FastAPI routers.
"""

from typing import Optional, List, Dict, Any
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.department_repository import DepartmentRepository
from app.database.models import Employee
from app.utils.logger import logger


class EmployeeService:
    """Service layer for Employee operations."""

    def __init__(self, employee_repo: EmployeeRepository, department_repo: DepartmentRepository):
        self.employee_repo = employee_repo
        self.department_repo = department_repo

    def get_employee_profile(self, employee_identifier: str) -> Optional[Dict[str, Any]]:
        """Fetch employee profile. Identifier can be ID or Employee Number or Name."""
        logger.info(f"Fetching profile for: {employee_identifier}")
        emp = None
        
        # Try as ID
        if str(employee_identifier).isdigit():
            emp = self.employee_repo.get_with_full_profile(int(employee_identifier))
        
        # Try as Employee Number
        if not emp:
            emp = self.employee_repo.get_by_employee_number(employee_identifier)
            if emp:
                 emp = self.employee_repo.get_with_full_profile(emp.id)

        # Try as Name (first match)
        if not emp:
            results = self.employee_repo.search_by_name(employee_identifier, limit=1)
            if results:
                emp = self.employee_repo.get_with_full_profile(results[0].id)

        if not emp:
            logger.warning(f"Employee not found: {employee_identifier}")
            return None

        # Build comprehensive profile dictionary
        return {
            "id": emp.id,
            "employee_number": emp.employee_number,
            "name": emp.name,
            "email": emp.email,
            "department": emp.department.name if emp.department else "Unknown",
            "role": emp.role.title if emp.role else "Unknown",
            "grade": emp.grade,
            "years_experience": emp.years_experience,
            "location": emp.location,
            "performance_rating": emp.performance_rating or (emp.performance_reviews[-1].rating.value if emp.performance_reviews else "N/A"),
            "current_skills": [s.skill.name for s in emp.skills],
            "career_goals": [g.target_role_name for g in emp.career_goals if g.status == "Active"]
        }

    def search_employees(self, query: str) -> List[Dict[str, Any]]:
        """Search employees by name."""
        results = self.employee_repo.search_by_name(query)
        return [
            {
                "name": emp.name,
                "employee_number": emp.employee_number,
                "department": emp.department.name,
                "role": emp.role.title
            }
            for emp in results
        ]

    def get_department_info(self, department_name: str) -> Optional[Dict[str, Any]]:
        """Get department info including employee count."""
        dept = self.department_repo.get_by_name(department_name)
        if not dept:
            return None
            
        count = self.employee_repo.count_by_department(dept.id)
        return {
            "name": dept.name,
            "code": dept.code,
            "head_name": dept.head_name,
            "location": dept.location,
            "employee_count": count
        }
