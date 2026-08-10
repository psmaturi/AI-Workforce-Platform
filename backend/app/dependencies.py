"""Dependency Injection Module."""

from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.database import get_db

from app.repositories.employee_repository import EmployeeRepository
from app.repositories.department_repository import DepartmentRepository
from app.repositories.skills_repository import SkillsRepository
from app.repositories.training_repository import TrainingRepository

from app.services.employee_service import EmployeeService
from app.services.training_service import TrainingService
from app.services.skill_gap_service import SkillGapService
from app.services.career_service import CareerService
from app.services.analytics_service import AnalyticsService

from app.ml.model_manager import ModelManager, get_model_manager
from app.services.ml_service import MLService

from app.agent.workforce_agent import get_workforce_agent
from app.services.chat_service import ChatService


# --- Repositories ---
def get_employee_repo(db: Session = Depends(get_db)) -> EmployeeRepository:
    return EmployeeRepository(db)

def get_department_repo(db: Session = Depends(get_db)) -> DepartmentRepository:
    return DepartmentRepository(db)

def get_skills_repo(db: Session = Depends(get_db)) -> SkillsRepository:
    return SkillsRepository(db)

def get_training_repo(db: Session = Depends(get_db)) -> TrainingRepository:
    return TrainingRepository(db)


# --- Services ---
def get_employee_service(
    employee_repo: EmployeeRepository = Depends(get_employee_repo),
    department_repo: DepartmentRepository = Depends(get_department_repo)
) -> EmployeeService:
    return EmployeeService(employee_repo, department_repo)

def get_training_service(
    training_repo: TrainingRepository = Depends(get_training_repo),
    skills_repo: SkillsRepository = Depends(get_skills_repo)
) -> TrainingService:
    return TrainingService(training_repo, skills_repo)

def get_skill_gap_service(
    employee_repo: EmployeeRepository = Depends(get_employee_repo),
    skills_repo: SkillsRepository = Depends(get_skills_repo)
) -> SkillGapService:
    return SkillGapService(employee_repo, skills_repo)

def get_career_service(
    employee_repo: EmployeeRepository = Depends(get_employee_repo)
) -> CareerService:
    return CareerService(employee_repo)

def get_analytics_service(
    employee_repo: EmployeeRepository = Depends(get_employee_repo),
    department_repo: DepartmentRepository = Depends(get_department_repo)
) -> AnalyticsService:
    return AnalyticsService(employee_repo, department_repo)

def get_ml_service(
    employee_repo: EmployeeRepository = Depends(get_employee_repo),
    department_repo: DepartmentRepository = Depends(get_department_repo),
    skills_repo: SkillsRepository = Depends(get_skills_repo),
    training_repo: TrainingRepository = Depends(get_training_repo),
    model_manager: ModelManager = Depends(get_model_manager)
) -> MLService:
    return MLService(
        employee_repo,
        department_repo,
        skills_repo,
        training_repo,
        model_manager
    )

# --- Chat Service ---
def get_chat_service(
    employee_service: EmployeeService = Depends(get_employee_service),
    training_service: TrainingService = Depends(get_training_service),
    skill_gap_service: SkillGapService = Depends(get_skill_gap_service),
    career_service: CareerService = Depends(get_career_service),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    ml_service: MLService = Depends(get_ml_service)
) -> ChatService:
    """Dependency getter for ChatService using pre-compiled WorkforceAgent singleton."""
    agent = get_workforce_agent()
    # Inject all workforce services into the chat service
    services = {
        "employee_service": employee_service,
        "training_service": training_service,
        "skill_gap_service": skill_gap_service,
        "career_service": career_service,
        "analytics_service": analytics_service,
        "ml_service": ml_service
    }
    return ChatService(agent=agent, services=services)
