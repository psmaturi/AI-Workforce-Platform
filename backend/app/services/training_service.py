"""Training Service Module.

Responsibilities:
- Recommends courses.
- Fetches employee training history.
"""

from typing import Optional, List, Dict, Any
from app.repositories.training_repository import TrainingRepository
from app.repositories.skills_repository import SkillsRepository
from app.database.models import TrainingCourse, EmployeeTraining, TrainingStatus
from app.utils.logger import logger
from datetime import datetime


class TrainingService:
    """Service layer for Training and Course recommendations."""

    def __init__(self, training_repo: TrainingRepository, skills_repo: SkillsRepository):
        self.training_repo = training_repo
        self.skills_repo = skills_repo

    def get_recommendations_for_skill(self, skill_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Recommend courses that cover a specific skill."""
        logger.info(f"Finding courses for skill: {skill_name}")
        # Search courses where description or skills_covered contains the skill name
        courses = self.training_repo.search_courses_by_skill(skill_name, limit=limit)
        
        return [
            {
                "code": c.code,
                "name": c.name,
                "difficulty": c.difficulty,
                "duration_hours": c.duration_hours,
                "provider": c.provider,
                "mode": c.mode.value
            }
            for c in courses
        ]

    def get_employee_training_history(self, employee_id: int) -> List[Dict[str, Any]]:
        """Get the training records of an employee."""
        records = self.training_repo.get_employee_training_history(employee_id)
        return [
            {
                "course_name": r.course.name,
                "status": r.status.value,
                "score": r.score,
                "completion_date": r.completion_date.isoformat() if r.completion_date else None,
                "provider": r.course.provider
            }
            for r in records
        ]

    def calculate_training_progress(self, employee_id: int) -> Dict[str, Any]:
        """Calculate employee training progress from PostgreSQL/SQLite records."""
        logger.info(f"Calculating training progress for employee ID: {employee_id}")
        records = self.training_repo.get_employee_training_history(employee_id)
        total_courses = len(records)
        
        completed = [r for r in records if r.status == TrainingStatus.COMPLETED]
        in_progress = [
            r for r in records
            if r.status == TrainingStatus.IN_PROGRESS or (r.status == TrainingStatus.EXPIRED and (r.hours_completed or 0.0) > 0.0)
        ]
        not_started = [
            r for r in records
            if r.status == TrainingStatus.NOT_STARTED or (r.status == TrainingStatus.EXPIRED and not ((r.hours_completed or 0.0) > 0.0))
        ]
        expired = [r for r in records if r.status == TrainingStatus.EXPIRED]
        
        # Calculate completion percentage
        completion_percentage = (len(completed) / total_courses) * 100.0 if total_courses > 0 else 0.0
        
        # Calculate total training hours from completed courses (or hours completed)
        total_hours = sum(r.hours_completed or 0.0 for r in records)
        
        # Calculate mandatory training completion
        assigned_mandatory = [r for r in records if r.course.is_mandatory]
        completed_mandatory = [r for r in assigned_mandatory if r.status == TrainingStatus.COMPLETED]
        
        if assigned_mandatory:
            mandatory_completion_percentage = (len(completed_mandatory) / len(assigned_mandatory)) * 100.0
        else:
            # Fallback to all mandatory courses in catalog
            try:
                all_mandatory_courses = self.training_repo.db.query(TrainingCourse).filter(
                    TrainingCourse.is_mandatory == True, TrainingCourse.is_active == True
                ).all()
                if all_mandatory_courses:
                    completed_ids = {r.course_id for r in completed}
                    comp_mandatory = [c for c in all_mandatory_courses if c.id in completed_ids]
                    mandatory_completion_percentage = (len(comp_mandatory) / len(all_mandatory_courses)) * 100.0
                else:
                    mandatory_completion_percentage = 100.0
            except Exception as e:
                logger.error(f"Error querying mandatory courses from database catalog: {e}")
                mandatory_completion_percentage = 100.0
                
        # Expired/overdue check
        now = datetime.utcnow()
        overdue_count = len(expired) + len([r for r in records if r.expiry_date and r.expiry_date < now and r.status != TrainingStatus.COMPLETED])

        return {
            "total_courses": total_courses,
            "completed": len(completed),
            "in_progress": len(in_progress),
            "not_started": len(not_started),
            "expired": len(expired),
            "overdue": overdue_count,
            "completion_percentage": round(completion_percentage, 1),
            "mandatory_completion_percentage": round(mandatory_completion_percentage, 1),
            "total_hours": round(total_hours, 1),
            "completed_courses_list": [r.course.name for r in completed],
            "in_progress_courses_list": [r.course.name for r in in_progress],
            "not_started_courses_list": [r.course.name for r in not_started]
        }

