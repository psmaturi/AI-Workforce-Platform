"""Training Repository — Database query layer for training courses and records.

Responsibilities:
- Queries training_courses and employee_training tables.
- Finds courses relevant to specific skills or roles.
- Returns training history and completion status.

Integration:
- Used by TrainingService and CareerService.
"""

import time
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from app.database.models import TrainingCourse, EmployeeTraining, TrainingStatus
from app.utils.logger import logger


class TrainingRepository:
    """Data access layer for TrainingCourse and EmployeeTraining."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_course_by_id(self, course_id: int) -> Optional[TrainingCourse]:
        """Fetch a course by primary key."""
        return self.db.query(TrainingCourse).filter(
            TrainingCourse.id == course_id, TrainingCourse.is_active == True
        ).first()

    def get_course_by_code(self, code: str) -> Optional[TrainingCourse]:
        """Fetch a course by its catalog code (e.g. 'DS-011')."""
        return self.db.query(TrainingCourse).filter(
            TrainingCourse.code == code
        ).first()

    def search_courses_by_skill(self, skill_name: str, limit: int = 10) -> list[TrainingCourse]:
        """Find courses whose skills_covered field contains the skill name."""
        start = time.time()
        results = (
            self.db.query(TrainingCourse)
            .filter(
                TrainingCourse.is_active == True,
                TrainingCourse.skills_covered.ilike(f"%{skill_name}%"),
            )
            .limit(limit)
            .all()
        )
        logger.info(f"[TrainingRepo] courses for skill '{skill_name}' → {len(results)} — {(time.time()-start)*1000:.1f}ms")
        return results

    def get_courses_by_category(self, category: str, limit: int = 20) -> list[TrainingCourse]:
        """Courses filtered by category."""
        return (
            self.db.query(TrainingCourse)
            .filter(TrainingCourse.category == category, TrainingCourse.is_active == True)
            .limit(limit)
            .all()
        )

    def get_employee_training_history(self, employee_id: int) -> list[EmployeeTraining]:
        """All training records for an employee with course details joined."""
        start = time.time()
        results = (
            self.db.query(EmployeeTraining)
            .options(joinedload(EmployeeTraining.course))
            .filter(EmployeeTraining.employee_id == employee_id)
            .order_by(EmployeeTraining.created_at.desc())
            .all()
        )
        logger.info(f"[TrainingRepo] history({employee_id}) → {len(results)} records — {(time.time()-start)*1000:.1f}ms")
        return results

    def get_completed_course_ids(self, employee_id: int) -> set[int]:
        """Return set of course_ids the employee has completed."""
        records = (
            self.db.query(EmployeeTraining.course_id)
            .filter(
                EmployeeTraining.employee_id == employee_id,
                EmployeeTraining.status == TrainingStatus.COMPLETED,
            )
            .all()
        )
        return {r.course_id for r in records}

    def get_in_progress_courses(self, employee_id: int) -> list[EmployeeTraining]:
        """All in-progress training records for an employee."""
        return (
            self.db.query(EmployeeTraining)
            .options(joinedload(EmployeeTraining.course))
            .filter(
                EmployeeTraining.employee_id == employee_id,
                EmployeeTraining.status == TrainingStatus.IN_PROGRESS,
            )
            .all()
        )

    def get_mandatory_incomplete(self, employee_id: int) -> list[TrainingCourse]:
        """Find mandatory courses not yet completed by this employee."""
        completed_ids = self.get_completed_course_ids(employee_id)
        mandatory = (
            self.db.query(TrainingCourse)
            .filter(TrainingCourse.is_mandatory == True, TrainingCourse.is_active == True)
            .all()
        )
        return [c for c in mandatory if c.id not in completed_ids]

    def get_courses_for_target_grades(self, grade: int, limit: int = 20) -> list[TrainingCourse]:
        """Find courses whose target_grades includes the given grade."""
        grade_str = str(grade)
        return (
            self.db.query(TrainingCourse)
            .filter(
                TrainingCourse.is_active == True,
                TrainingCourse.target_grades.ilike(f"%{grade_str}%"),
            )
            .limit(limit)
            .all()
        )

    def count_completions_by_department(self, department_id: int) -> int:
        """Count total training completions for all employees in a department."""
        from app.database.models import Employee
        from sqlalchemy import func
        result = (
            self.db.query(func.count(EmployeeTraining.id))
            .join(Employee, Employee.id == EmployeeTraining.employee_id)
            .filter(
                Employee.department_id == department_id,
                EmployeeTraining.status == TrainingStatus.COMPLETED,
            )
            .scalar()
        )
        return result or 0
