"""SQLAlchemy ORM Models — Workforce Intelligence Database.

12 normalized tables representing the complete workforce data model:
  departments, job_roles, skills, employees, employee_skills,
  training_courses, employee_training, role_skill_requirements,
  performance_reviews, career_goals, learning_roadmaps, managers

All tables include: primary key, created_at, updated_at.
All FK relationships use lazy='select' for explicit control over loading.
"""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Integer, String, Float, Boolean, Text, DateTime,
    Enum as SAEnum, ForeignKey, Index, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SkillLevel(str, enum.Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    EXPERT = "Expert"


class TrainingStatus(str, enum.Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    EXPIRED = "Expired"


class EmploymentStatus(str, enum.Enum):
    ACTIVE = "Active"
    ON_LEAVE = "On Leave"
    PROBATION = "Probation"
    SEPARATED = "Separated"


class TrainingMode(str, enum.Enum):
    ONLINE = "Online"
    CLASSROOM = "Classroom"
    BLENDED = "Blended"
    ON_JOB = "On-the-Job"


class PerformanceRating(str, enum.Enum):
    EXCEPTIONAL = "Exceptional"
    EXCEEDS = "Exceeds Expectations"
    MEETS = "Meets Expectations"
    PARTIAL = "Partially Meets Expectations"
    DOES_NOT_MEET = "Does Not Meet Expectations"


class GoalStatus(str, enum.Enum):
    ACTIVE = "Active"
    ACHIEVED = "Achieved"
    ON_HOLD = "On Hold"
    ABANDONED = "Abandoned"


# ---------------------------------------------------------------------------
# Timestamp Mixin
# ---------------------------------------------------------------------------

class TimestampMixin:
    """Adds created_at and updated_at columns to a model."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


# ---------------------------------------------------------------------------
# 1. Departments
# ---------------------------------------------------------------------------

class Department(TimestampMixin, Base):
    """Organizational department (e.g., Mechanical, Electrical, AI & Digital)."""
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    head_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    employees: Mapped[list["Employee"]] = relationship("Employee", back_populates="department", lazy="select")
    job_roles: Mapped[list["JobRole"]] = relationship("JobRole", back_populates="department", lazy="select")

    def __repr__(self) -> str:
        return f"<Department(id={self.id}, name='{self.name}')>"


# ---------------------------------------------------------------------------
# 2. Job Roles
# ---------------------------------------------------------------------------

class JobRole(TimestampMixin, Base):
    """Defined job role within a department with grade and requirements."""
    __tablename__ = "job_roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=False)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)  # Grade 1-12
    track: Mapped[str] = mapped_column(String(20), default="Technical")  # Technical / Leadership
    min_experience_years: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    preferred_certifications: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    department: Mapped["Department"] = relationship("Department", back_populates="job_roles")
    employees: Mapped[list["Employee"]] = relationship("Employee", back_populates="role", lazy="select")
    skill_requirements: Mapped[list["RoleSkillRequirement"]] = relationship(
        "RoleSkillRequirement", back_populates="role", lazy="select"
    )

    __table_args__ = (
        Index("ix_jobrole_dept_grade", "department_id", "grade"),
    )

    def __repr__(self) -> str:
        return f"<JobRole(id={self.id}, title='{self.title}', grade={self.grade})>"


# ---------------------------------------------------------------------------
# 3. Skills
# ---------------------------------------------------------------------------

class Skill(TimestampMixin, Base):
    """Technical, behavioral, or digital skill definition."""
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    # Categories: Technical, Behavioral, Digital, Safety, Leadership
    subcategory: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    future_demand: Mapped[str] = mapped_column(String(20), default="Medium")  # High / Medium / Low
    criticality: Mapped[str] = mapped_column(String(20), default="Medium")  # Critical / High / Medium / Low
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    employee_skills: Mapped[list["EmployeeSkill"]] = relationship("EmployeeSkill", back_populates="skill")
    role_requirements: Mapped[list["RoleSkillRequirement"]] = relationship(
        "RoleSkillRequirement", back_populates="skill"
    )

    def __repr__(self) -> str:
        return f"<Skill(id={self.id}, name='{self.name}', category='{self.category}')>"


# ---------------------------------------------------------------------------
# 4. Employees
# ---------------------------------------------------------------------------

class Employee(TimestampMixin, Base):
    """Core employee record."""
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    data_source: Mapped[str] = mapped_column(String(50), default="SYNTHETIC_DEMO", nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("job_roles.id"), nullable=False)
    manager_id: Mapped[Optional[int]] = mapped_column(ForeignKey("employees.id"), nullable=True)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    years_experience: Mapped[float] = mapped_column(Float, default=0.0)
    years_in_company: Mapped[float] = mapped_column(Float, default=0.0)
    location: Mapped[str] = mapped_column(String(100), default="Plant HQ")
    employment_status: Mapped[EmploymentStatus] = mapped_column(
        SAEnum(EmploymentStatus), default=EmploymentStatus.ACTIVE
    )
    performance_rating: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    # Latest performance rating label (denormalized for fast lookup)
    last_rating_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    department: Mapped["Department"] = relationship("Department", back_populates="employees")
    role: Mapped["JobRole"] = relationship("JobRole", back_populates="employees")
    manager: Mapped[Optional["Employee"]] = relationship("Employee", remote_side="Employee.id", lazy="select")
    direct_reports: Mapped[list["Employee"]] = relationship(
        "Employee", back_populates="manager", foreign_keys="Employee.manager_id", lazy="select"
    )
    skills: Mapped[list["EmployeeSkill"]] = relationship("EmployeeSkill", back_populates="employee")
    training_records: Mapped[list["EmployeeTraining"]] = relationship(
        "EmployeeTraining", back_populates="employee"
    )
    performance_reviews: Mapped[list["PerformanceReview"]] = relationship(
        "PerformanceReview", back_populates="employee"
    )
    career_goals: Mapped[list["CareerGoal"]] = relationship("CareerGoal", back_populates="employee")
    learning_roadmaps: Mapped[list["LearningRoadmap"]] = relationship(
        "LearningRoadmap", back_populates="employee"
    )

    __table_args__ = (
        Index("ix_employee_dept_role", "department_id", "role_id"),
        Index("ix_employee_grade", "grade"),
    )

    def __repr__(self) -> str:
        return f"<Employee(id={self.id}, number='{self.employee_number}', name='{self.name}')>"


# ---------------------------------------------------------------------------
# 5. Employee Skills
# ---------------------------------------------------------------------------

class EmployeeSkill(TimestampMixin, Base):
    """Junction table linking employees to their verified skills with proficiency level."""
    __tablename__ = "employee_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False, index=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), nullable=False, index=True)
    level: Mapped[SkillLevel] = mapped_column(SAEnum(SkillLevel), default=SkillLevel.BEGINNER)
    years_experience: Mapped[float] = mapped_column(Float, default=0.0)
    is_certified: Mapped[bool] = mapped_column(Boolean, default=False)
    certification_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    last_assessed: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", back_populates="skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="employee_skills")

    __table_args__ = (
        UniqueConstraint("employee_id", "skill_id", name="uq_employee_skill"),
        Index("ix_empskill_employee", "employee_id"),
        Index("ix_empskill_skill", "skill_id"),
    )

    def __repr__(self) -> str:
        return f"<EmployeeSkill(emp={self.employee_id}, skill={self.skill_id}, level='{self.level}')>"


# ---------------------------------------------------------------------------
# 6. Training Courses
# ---------------------------------------------------------------------------

class TrainingCourse(TimestampMixin, Base):
    """Available training courses in the company catalog."""
    __tablename__ = "training_courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    subcategory: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    duration_hours: Mapped[float] = mapped_column(Float, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), default="Intermediate")
    # Beginner / Intermediate / Advanced / Expert
    mode: Mapped[TrainingMode] = mapped_column(SAEnum(TrainingMode), default=TrainingMode.BLENDED)
    provider: Mapped[str] = mapped_column(String(100), default="Internal")
    skills_covered: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Comma-separated skill names
    prerequisites: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_grades: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    # e.g. "3,4,5,6"
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=False)
    pass_score: Mapped[int] = mapped_column(Integer, default=70)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    training_records: Mapped[list["EmployeeTraining"]] = relationship(
        "EmployeeTraining", back_populates="course"
    )

    def __repr__(self) -> str:
        return f"<TrainingCourse(id={self.id}, code='{self.code}', name='{self.name}')>"


# ---------------------------------------------------------------------------
# 7. Employee Training Records
# ---------------------------------------------------------------------------

class EmployeeTraining(TimestampMixin, Base):
    """Record of an employee's participation in a training course."""
    __tablename__ = "employee_training"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False, index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("training_courses.id"), nullable=False, index=True)
    status: Mapped[TrainingStatus] = mapped_column(SAEnum(TrainingStatus), default=TrainingStatus.NOT_STARTED)
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    completion_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expiry_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    hours_completed: Mapped[float] = mapped_column(Float, default=0.0)
    certificate_issued: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", back_populates="training_records")
    course: Mapped["TrainingCourse"] = relationship("TrainingCourse", back_populates="training_records")

    __table_args__ = (
        Index("ix_emptraining_employee", "employee_id"),
        Index("ix_emptraining_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<EmployeeTraining(emp={self.employee_id}, course={self.course_id}, status='{self.status}')>"


# ---------------------------------------------------------------------------
# 8. Role Skill Requirements
# ---------------------------------------------------------------------------

class RoleSkillRequirement(TimestampMixin, Base):
    """Maps a job role to its required skills and minimum proficiency level."""
    __tablename__ = "role_skill_requirements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("job_roles.id"), nullable=False, index=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), nullable=False, index=True)
    required_level: Mapped[SkillLevel] = mapped_column(SAEnum(SkillLevel), nullable=False)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    role: Mapped["JobRole"] = relationship("JobRole", back_populates="skill_requirements")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="role_requirements")

    __table_args__ = (
        UniqueConstraint("role_id", "skill_id", name="uq_role_skill"),
        Index("ix_roleskill_role", "role_id"),
    )

    def __repr__(self) -> str:
        return f"<RoleSkillReq(role={self.role_id}, skill={self.skill_id}, level='{self.required_level}')>"


# ---------------------------------------------------------------------------
# 9. Performance Reviews
# ---------------------------------------------------------------------------

class PerformanceReview(TimestampMixin, Base):
    """Annual / periodic performance review record for an employee."""
    __tablename__ = "performance_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False, index=True)
    review_cycle: Mapped[str] = mapped_column(String(20), nullable=False)  # e.g. "FY2024-25"
    rating: Mapped[PerformanceRating] = mapped_column(SAEnum(PerformanceRating), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)  # 1.0 – 5.0
    strengths: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    improvement_areas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    manager_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewer_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    review_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_final: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", back_populates="performance_reviews")

    __table_args__ = (
        UniqueConstraint("employee_id", "review_cycle", name="uq_employee_review_cycle"),
        Index("ix_review_employee", "employee_id"),
    )

    def __repr__(self) -> str:
        return f"<PerformanceReview(emp={self.employee_id}, cycle='{self.review_cycle}', score={self.score})>"


# ---------------------------------------------------------------------------
# 10. Career Goals
# ---------------------------------------------------------------------------

class CareerGoal(TimestampMixin, Base):
    """An employee's declared career target role and timeline."""
    __tablename__ = "career_goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False, index=True)
    target_role_id: Mapped[Optional[int]] = mapped_column(ForeignKey("job_roles.id"), nullable=True)
    target_role_name: Mapped[str] = mapped_column(String(150), nullable=False)
    # Stored separately to allow free-text goals not yet mapped to a formal role
    target_timeline_months: Mapped[int] = mapped_column(Integer, default=12)
    current_progress_pct: Mapped[float] = mapped_column(Float, default=0.0)  # 0-100
    status: Mapped[GoalStatus] = mapped_column(SAEnum(GoalStatus), default=GoalStatus.ACTIVE)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", back_populates="career_goals")
    target_role: Mapped[Optional["JobRole"]] = relationship("JobRole", lazy="select")
    learning_roadmaps: Mapped[list["LearningRoadmap"]] = relationship(
        "LearningRoadmap", back_populates="career_goal"
    )

    __table_args__ = (
        Index("ix_careergoal_employee", "employee_id"),
    )

    def __repr__(self) -> str:
        return f"<CareerGoal(emp={self.employee_id}, target='{self.target_role_name}')>"


# ---------------------------------------------------------------------------
# 11. Learning Roadmaps
# ---------------------------------------------------------------------------

class LearningRoadmap(TimestampMixin, Base):
    """AI-generated or manually curated learning roadmap for a career goal."""
    __tablename__ = "learning_roadmaps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False, index=True)
    career_goal_id: Mapped[int] = mapped_column(ForeignKey("career_goals.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    roadmap_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # JSON array of {skill, course, priority, timeline}
    total_courses: Mapped[int] = mapped_column(Integer, default=0)
    completed_courses: Mapped[int] = mapped_column(Integer, default=0)
    estimated_months: Mapped[int] = mapped_column(Integer, default=6)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", back_populates="learning_roadmaps")
    career_goal: Mapped["CareerGoal"] = relationship("CareerGoal", back_populates="learning_roadmaps")

    def __repr__(self) -> str:
        return f"<LearningRoadmap(emp={self.employee_id}, title='{self.title}')>"

# ---------------------------------------------------------------------------
# PHASE 5: ML & Workforce Intelligence Tables
# ---------------------------------------------------------------------------

class ModelMetadata(TimestampMixin, Base):
    """Tracks deployed ML models and their evaluation metrics."""
    __tablename__ = "model_metadata"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    model_name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    model_type: Mapped[str] = mapped_column(String(50))  # e.g., Classification, Regression
    version: Mapped[str] = mapped_column(String(20))
    metrics: Mapped[Optional[str]] = mapped_column(Text)  # JSON string of metrics
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class SkillPrediction(TimestampMixin, Base):
    """Future skill demand predictions."""
    __tablename__ = "skill_predictions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), nullable=False, index=True)
    target_year: Mapped[int] = mapped_column(Integer, nullable=False)
    demand_category: Mapped[str] = mapped_column(String(20))  # Low, Medium, High, Critical
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    skill: Mapped["Skill"] = relationship("Skill", lazy="select")


class WorkforceForecast(TimestampMixin, Base):
    """Predicted future workforce headcounts."""
    __tablename__ = "workforce_forecasts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=False, index=True)
    target_year: Mapped[int] = mapped_column(Integer, nullable=False)
    current_headcount: Mapped[int] = mapped_column(Integer, default=0)
    projected_headcount: Mapped[int] = mapped_column(Integer, default=0)
    required_headcount: Mapped[int] = mapped_column(Integer, default=0)
    gap: Mapped[int] = mapped_column(Integer, default=0)
    
    department: Mapped["Department"] = relationship("Department", lazy="select")


class EmployeeReadiness(TimestampMixin, Base):
    """Computed readiness scores for employees targeting roles."""
    __tablename__ = "employee_readiness"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False, index=True)
    target_role_id: Mapped[int] = mapped_column(ForeignKey("job_roles.id"), nullable=False)
    readiness_score: Mapped[float] = mapped_column(Float, nullable=False)  # 0-100
    classification: Mapped[str] = mapped_column(String(20))  # Not Ready, Developing, Nearly Ready, Ready
    
    employee: Mapped["Employee"] = relationship("Employee", lazy="select")
    target_role: Mapped["JobRole"] = relationship("JobRole", lazy="select")


class SkillRisk(TimestampMixin, Base):
    """Identified workforce skill risks."""
    __tablename__ = "skill_risks"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=False, index=True)
    skill_id: Mapped[Optional[int]] = mapped_column(ForeignKey("skills.id"), nullable=True)
    risk_type: Mapped[str] = mapped_column(String(100))  # e.g., Single-person Dependency
    risk_level: Mapped[str] = mapped_column(String(20))  # Low, Medium, High, Critical
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    department: Mapped["Department"] = relationship("Department", lazy="select")
    skill: Mapped[Optional["Skill"]] = relationship("Skill", lazy="select")

