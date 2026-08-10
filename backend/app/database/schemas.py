"""Pydantic Schemas for Workforce Intelligence Database.

Responsibilities:
- Defines data validation, serialization, and deserialization models.
- Provides base schemas and response models for the API.

Integration:
- Used by Services for standardized data return types.
- Used by FastAPI routers for request/response bodies.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field
from app.database.models import SkillLevel, EmploymentStatus, TrainingStatus, GoalStatus


# ---------------------------------------------------------------------------
# Base Models
# ---------------------------------------------------------------------------
class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TimestampBase(ORMBase):
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Department
# ---------------------------------------------------------------------------
class DepartmentBase(BaseModel):
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=20)
    description: Optional[str] = None
    head_name: Optional[str] = None
    location: Optional[str] = None
    is_active: bool = True

class DepartmentResponse(DepartmentBase, TimestampBase):
    id: int


# ---------------------------------------------------------------------------
# Job Role
# ---------------------------------------------------------------------------
class JobRoleBase(BaseModel):
    title: str = Field(..., max_length=150)
    grade: int
    track: str = "Technical"
    min_experience_years: int = 0
    description: Optional[str] = None
    preferred_certifications: Optional[str] = None
    is_active: bool = True

class JobRoleResponse(JobRoleBase, TimestampBase):
    id: int
    department_id: int


# ---------------------------------------------------------------------------
# Skill
# ---------------------------------------------------------------------------
class SkillBase(BaseModel):
    name: str = Field(..., max_length=150)
    category: str = Field(..., max_length=80)
    subcategory: Optional[str] = None
    description: Optional[str] = None
    future_demand: str = "Medium"
    criticality: str = "Medium"
    is_active: bool = True

class SkillResponse(SkillBase, TimestampBase):
    id: int


# ---------------------------------------------------------------------------
# Employee Skill
# ---------------------------------------------------------------------------
class EmployeeSkillBase(BaseModel):
    level: SkillLevel = SkillLevel.BEGINNER
    years_experience: float = 0.0
    is_certified: bool = False
    certification_name: Optional[str] = None
    notes: Optional[str] = None

class EmployeeSkillResponse(EmployeeSkillBase, TimestampBase):
    id: int
    employee_id: int
    skill_id: int
    skill: Optional[SkillResponse] = None


# ---------------------------------------------------------------------------
# Employee
# ---------------------------------------------------------------------------
class EmployeeBase(BaseModel):
    employee_number: str = Field(..., max_length=20)
    name: str = Field(..., max_length=150)
    email: str = Field(..., max_length=200)
    grade: int
    years_experience: float = 0.0
    years_in_company: float = 0.0
    location: str = "Plant HQ"
    employment_status: EmploymentStatus = EmploymentStatus.ACTIVE
    performance_rating: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True

class EmployeeResponse(EmployeeBase, TimestampBase):
    id: int
    department_id: int
    role_id: int
    manager_id: Optional[int] = None
    department: Optional[DepartmentResponse] = None
    role: Optional[JobRoleResponse] = None


class EmployeeProfileResponse(EmployeeResponse):
    skills: List[EmployeeSkillResponse] = []


# ---------------------------------------------------------------------------
# Training Course
# ---------------------------------------------------------------------------
class TrainingCourseBase(BaseModel):
    code: str = Field(..., max_length=30)
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    category: str = Field(..., max_length=80)
    duration_hours: float
    difficulty: str = "Intermediate"
    provider: str = "Internal"
    skills_covered: Optional[str] = None
    is_mandatory: bool = False
    is_active: bool = True

class TrainingCourseResponse(TrainingCourseBase, TimestampBase):
    id: int


# ---------------------------------------------------------------------------
# Employee Training
# ---------------------------------------------------------------------------
class EmployeeTrainingResponse(TimestampBase):
    id: int
    employee_id: int
    course_id: int
    status: TrainingStatus
    score: Optional[float] = None
    completion_date: Optional[datetime] = None
    course: Optional[TrainingCourseResponse] = None


# ---------------------------------------------------------------------------
# Role Skill Requirement
# ---------------------------------------------------------------------------
class RoleSkillRequirementResponse(TimestampBase):
    id: int
    role_id: int
    skill_id: int
    required_level: SkillLevel
    is_mandatory: bool
    skill: Optional[SkillResponse] = None


# ---------------------------------------------------------------------------
# Career Goal
# ---------------------------------------------------------------------------
class CareerGoalResponse(TimestampBase):
    id: int
    employee_id: int
    target_role_id: Optional[int] = None
    target_role_name: str
    target_timeline_months: int
    current_progress_pct: float
    status: GoalStatus
    target_role: Optional[JobRoleResponse] = None


# ---------------------------------------------------------------------------
# Learning Roadmap
# ---------------------------------------------------------------------------
class LearningRoadmapResponse(TimestampBase):
    id: int
    employee_id: int
    career_goal_id: int
    title: str
    roadmap_json: Optional[str] = None
    total_courses: int
    completed_courses: int
    estimated_months: int
    is_ai_generated: bool
    is_active: bool
