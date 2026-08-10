"""Workforce Intelligence Tools Module — Phase 4 DB-Backed Tools.

Contains LangChain tools powered by injected services via RunnableConfig.
"""

from typing import Dict, Any, List, Optional
from langchain_core.tools import tool
from langchain_core.runnables.config import RunnableConfig
from app.utils.logger import logger


def _get_service(config: RunnableConfig, service_name: str) -> Any:
    """Helper to extract a service from the RunnableConfig."""
    services = config.get("configurable", {}).get("services", {})
    return services.get(service_name)


def _check_auth(target_emp: dict, config: RunnableConfig, emp_service: Any) -> Optional[Dict[str, Any]]:
    """Enforces authentication: caller must be self, their manager, or HR."""
    cfg = config.get("configurable", {})
    auth_emp_id = cfg.get("authenticated_employee_id")
    auth_emp_num = cfg.get("authenticated_employee_number")
    
    if auth_emp_id is None and auth_emp_num is None:
        return None
        
    caller_ident = auth_emp_num if auth_emp_num is not None else str(auth_emp_id)
    caller_emp = emp_service.get_employee_profile(caller_ident)
    
    if not caller_emp:
        return {"error": "Authentication error: Caller profile not found."}
        
    # 1. Self access
    if caller_emp["id"] == target_emp["id"]:
        return None
        
    # 2. Manager report check
    target_orm = emp_service.employee_repo.get_by_id(target_emp["id"])
    if target_orm and target_orm.manager_id == caller_emp["id"]:
        return None
        
    # 3. HR check
    if caller_emp.get("department") == "Human Resources & L&D":
        return None
        
    return {"error": "Access Denied: You do not have permission to access this employee's records."}


# ---------------------------------------------------------------------------
# Employee Tools
# ---------------------------------------------------------------------------

@tool
def search_employees(query: str, config: RunnableConfig) -> List[Dict[str, Any]]:
    """Search for employees by name.

    Args:
        query (str): The name or partial name to search for.
    """
    logger.info(f"[Tool] EmployeeSearchTool: '{query}'")
    service = _get_service(config, "employee_service")
    if not service:
        return [{"error": "Service unavailable"}]
    return service.search_employees(query)


@tool
def get_employee_profile(employee_identifier: str, config: RunnableConfig) -> Dict[str, Any]:
    """Retrieve full workforce profile, job title, department, skills, and goals for an employee.

    Args:
        employee_identifier (str): Name, ID, or Employee Number of the employee.
    """
    logger.info(f"[Tool] EmployeeProfileTool for: {employee_identifier}")
    service = _get_service(config, "employee_service")
    if not service:
        return {"error": "Service unavailable"}
    
    result = service.get_employee_profile(employee_identifier)
    if not result:
        return {"error": f"Employee '{employee_identifier}' not found."}
        
    auth_err = _check_auth(result, config, service)
    if auth_err:
        return auth_err

    compact = (
        f"Employee: {result.get('name')}\n"
        f"Current Role: {result.get('role')}\n"
        f"Experience: {result.get('years_experience')} years\n"
        f"Relevant Skills: {', '.join(result.get('current_skills', []))}\n"
        f"Target Goals: {', '.join(result.get('career_goals', []))}"
    )
    return {"profile_summary": compact}


@tool
def get_department_info(department_name: str, config: RunnableConfig) -> Dict[str, Any]:
    """Get information about a department, including employee headcount.

    Args:
        department_name (str): Name of the department.
    """
    logger.info(f"[Tool] DepartmentTool for: {department_name}")
    service = _get_service(config, "employee_service")
    if not service:
        return {"error": "Service unavailable"}
    
    result = service.get_department_info(department_name)
    return result or {"error": f"Department '{department_name}' not found."}


# ---------------------------------------------------------------------------
# Skill Gap & Career Tools
# ---------------------------------------------------------------------------

@tool
def analyze_skill_gap(employee_identifier: str, target_role_id: int = None, config: RunnableConfig = None) -> Dict[str, Any]:
    """Analyze the skill gap between an employee's current skills and a target role.

    Args:
        employee_identifier (str): Employee name or number.
        target_role_id (int, optional): The ID of the target job role. If None, checks current role.
    """
    logger.info(f"[Tool] SkillGapTool for: '{employee_identifier}'")
    
    # First get employee ID
    emp_service = _get_service(config, "employee_service")
    gap_service = _get_service(config, "skill_gap_service")
    
    if not emp_service or not gap_service:
        return {"error": "Services unavailable"}
        
    emp = emp_service.get_employee_profile(employee_identifier)
    if not emp:
        return {"error": f"Employee '{employee_identifier}' not found."}
        
    auth_err = _check_auth(emp, config, emp_service)
    if auth_err:
        return auth_err

    result = gap_service.analyze_gap(emp["id"], target_role_id)
    if not result:
        return {"error": "Failed to analyze skill gap."}
        
    missing = [s["skill_name"] for s in result.get("missing_skills", [])]
    upgrade = [s["skill_name"] for s in result.get("upgrade_skills", [])]
    matched = result.get("matched_skills", [])
    total_reqs = len(missing) + len(upgrade) + len(matched)
    gap_percentage = round(((len(missing) + len(upgrade)) / total_reqs) * 100.0, 1) if total_reqs > 0 else 0.0
    
    compact = (
        f"Gap Percentage: {gap_percentage}%\n"
        f"Missing completely: {', '.join(missing) if missing else 'None'}\n"
        f"Needs upgrade: {', '.join(upgrade) if upgrade else 'None'}"
    )
    return {"skill_gap_summary": compact}


@tool
def get_career_goals(employee_identifier: str, config: RunnableConfig) -> List[Dict[str, Any]]:
    """Get the defined career goals and progress for an employee.

    Args:
        employee_identifier (str): Employee name or number.
    """
    logger.info(f"[Tool] CareerGoalTool for: {employee_identifier}")
    emp_service = _get_service(config, "employee_service")
    career_service = _get_service(config, "career_service")
    
    if not emp_service or not career_service:
        return [{"error": "Services unavailable"}]
        
    emp = emp_service.get_employee_profile(employee_identifier)
    if not emp:
        return [{"error": f"Employee '{employee_identifier}' not found."}]
        
    auth_err = _check_auth(emp, config, emp_service)
    if auth_err:
        return [auth_err]
        
    return career_service.get_career_goals(emp["id"])


# ---------------------------------------------------------------------------
# Training Tools
# ---------------------------------------------------------------------------

@tool
def get_training_recommendations(skill_name: str, config: RunnableConfig) -> List[Dict[str, Any]]:
    """Retrieve training course recommendations for a specific skill from the database.

    Args:
        skill_name (str): The skill to learn or improve (e.g., 'Python', 'Leadership').
    """
    logger.info(f"[Tool] TrainingRecommendationTool for: '{skill_name}'")
    service = _get_service(config, "training_service")
    if not service:
        return [{"error": "Service unavailable"}]
    
    return service.get_recommendations_for_skill(skill_name)


@tool
def get_learning_progress(employee_identifier: str, config: RunnableConfig) -> List[Dict[str, Any]]:
    """Get an employee's training history and learning progress.

    Args:
        employee_identifier (str): Employee name or number.
    """
    logger.info(f"[Tool] LearningProgressTool for: '{employee_identifier}'")
    emp_service = _get_service(config, "employee_service")
    training_service = _get_service(config, "training_service")
    
    if not emp_service or not training_service:
        return [{"error": "Services unavailable"}]
        
    emp = emp_service.get_employee_profile(employee_identifier)
    if not emp:
        return [{"error": f"Employee '{employee_identifier}' not found."}]
        
    auth_err = _check_auth(emp, config, emp_service)
    if auth_err:
        return [auth_err]
        
    return training_service.get_employee_training_history(emp["id"])


# ---------------------------------------------------------------------------
# Manager Analytics Tool
# ---------------------------------------------------------------------------

@tool
def get_manager_analytics(manager_identifier: str, config: RunnableConfig) -> Dict[str, Any]:
    """Get analytics and overview for a manager's direct reports.

    Args:
        manager_identifier (str): Manager's name or number.
    """
    logger.info(f"[Tool] ManagerAnalyticsTool for: '{manager_identifier}'")
    emp_service = _get_service(config, "employee_service")
    analytics_service = _get_service(config, "analytics_service")
    
    if not emp_service or not analytics_service:
        return {"error": "Services unavailable"}
        
    emp = emp_service.get_employee_profile(manager_identifier)
    if not emp:
        return {"error": f"Manager '{manager_identifier}' not found."}
        
    return analytics_service.get_team_overview(emp["id"])


# ---------------------------------------------------------------------------
# RAG-Powered Tools (ChromaDB Knowledge Retrieval)
# ---------------------------------------------------------------------------
# Keeping the company policy tool as RAG is meant for unstructured data

@tool
def query_company_policy(policy_topic: str) -> Dict[str, str]:
    """Search company HR policy documents for a specific topic.

    Uses ChromaDB to retrieve relevant policy information from uploaded documents.

    Args:
        policy_topic (str): Policy topic to search (e.g., 'learning budget', 'promotion criteria', 'safety').
    """
    logger.info(f"[Tool] CompanyPolicyTool querying ChromaDB for: '{policy_topic}'")
    try:
        from app.rag.retriever import retrieve, format_context

        docs = retrieve(query=f"company policy {policy_topic}")
        context = format_context(docs)
        return {
            "policy_topic": policy_topic,
            "retrieved_context": context,
            "source": "ChromaDB — Company Documents",
        }
    except Exception as e:
        logger.error(f"[Tool] CompanyPolicyTool error: {e}")
        return {
            "policy_topic": policy_topic,
            "retrieved_context": "Unable to retrieve policy documents at this time.",
            "source": "Error",
        }


# ---------------------------------------------------------------------------
# ML Intelligence Tools (Phase 5)
# ---------------------------------------------------------------------------

@tool
def calculate_readiness_score(employee_identifier: str, target_role_id: int, config: RunnableConfig) -> Dict[str, Any]:
    """Calculate an employee's readiness score for a target role using the ML service.

    Args:
        employee_identifier (str): Employee name or number.
        target_role_id (int): The ID of the target job role.
    """
    logger.info(f"[Tool] ReadinessScoreTool for: '{employee_identifier}'")
    emp_service = _get_service(config, "employee_service")
    ml_service = _get_service(config, "ml_service")
    
    if not emp_service or not ml_service:
        return {"error": "Services unavailable"}
        
    emp = emp_service.get_employee_profile(employee_identifier)
    if not emp:
        return {"error": f"Employee '{employee_identifier}' not found."}
        
    auth_err = _check_auth(emp, config, emp_service)
    if auth_err:
        return auth_err

    result = ml_service.get_readiness_score(emp["id"], target_role_id)
    if "error" in result:
        return result
        
    compact = f"Readiness: {result.get('readiness_score')}%\nStatus: {result.get('classification')}"
    return {"readiness_summary": compact}


@tool
def predict_future_skill_demand(department_encoded: int, current_demand: float, hiring_demand: float, trend: float, config: RunnableConfig) -> Dict[str, str]:
    """Predict future skill demand category (Low, Medium, High, Critical) using ML.

    Args:
        department_encoded (int): Department ID.
        current_demand (float): Current demand metric.
        hiring_demand (float): Hiring demand metric.
        trend (float): Industry trend score.
    """
    logger.info("[Tool] FutureSkillDemandTool")
    ml_service = _get_service(config, "ml_service")
    if not ml_service:
        return {"error": "Services unavailable"}
        
    prediction = ml_service.predict_future_demand(department_encoded, current_demand, hiring_demand, trend)
    return {"predicted_demand": prediction}


@tool
def forecast_workforce_headcount(year: int, department_encoded: int, role_encoded: int, current_headcount: int, attrition: float, config: RunnableConfig) -> Dict[str, int]:
    """Forecast required workforce headcount using ML.

    Args:
        year (int): Target year.
        department_encoded (int): Department ID.
        role_encoded (int): Role ID.
        current_headcount (int): Current headcount.
        attrition (float): Expected attrition rate.
    """
    logger.info("[Tool] WorkforceForecastTool")
    ml_service = _get_service(config, "ml_service")
    if not ml_service:
        return {"error": "Services unavailable"}
        
    prediction = ml_service.forecast_workforce(year, department_encoded, role_encoded, current_headcount, attrition)
    return {"forecasted_required_headcount": prediction}


@tool
def identify_workforce_skill_risks(department_id: int, config: RunnableConfig) -> List[Dict[str, Any]]:
    """Identify workforce skill risks for a department.

    Args:
        department_id (int): Department ID.
    """
    logger.info(f"[Tool] SkillRiskTool for department: {department_id}")
    ml_service = _get_service(config, "ml_service")
    if not ml_service:
        return [{"error": "Services unavailable"}]
        
    return ml_service.get_skill_risks(department_id)


@tool
def get_training_progress(employee_identifier: str, config: RunnableConfig) -> Dict[str, Any]:
    """Calculate and return an employee's training progress, completion percentage, and status.

    Args:
        employee_identifier (str): Employee name, ID, or employee number.
    """
    logger.info(f"[Tool] TrainingProgressTool for: '{employee_identifier}'")
    emp_service = _get_service(config, "employee_service")
    training_service = _get_service(config, "training_service")
    
    if not emp_service or not training_service:
        return {"error": "Services unavailable"}
        
    # Get target employee profile
    target_emp = emp_service.get_employee_profile(employee_identifier)
    if not target_emp:
        return {"error": f"Employee '{employee_identifier}' not found."}

    auth_err = _check_auth(target_emp, config, emp_service)
    if auth_err:
        return auth_err
        
    progress = training_service.calculate_training_progress(target_emp["id"])
    progress["employee"] = target_emp["name"]
    return progress


def _team_dashboard_impl(config: RunnableConfig) -> Dict[str, Any]:
    """Shared implementation for all manager team analytics tools."""
    emp_service = _get_service(config, "employee_service")
    ml_service = _get_service(config, "ml_service")
    
    if not emp_service or not ml_service:
        return {"error": "Services unavailable"}
        
    cfg = config.get("configurable", {})
    auth_emp_num = cfg.get("authenticated_employee_number")
    auth_emp_id = cfg.get("authenticated_employee_id")
    
    caller_ident = auth_emp_num if auth_emp_num else str(auth_emp_id) if auth_emp_id else "EMP1001"
    caller = emp_service.get_employee_profile(caller_ident)
    if not caller:
        return {"error": "Authentication error: Caller profile not found."}
        
    logger.info(f"Scope: {caller.get('name')}'s Direct Reports")
    logger.info("Database: Employee Training Records")
        
    if caller.get("department") != "Human Resources & L&D" and caller.get("grade", 0) < 8:
        return {"error": "Access Denied: Team analytics are only available to managers and HR."}
         
    return ml_service.get_manager_dashboard(caller["id"])


@tool
def get_team_training_progress(config: RunnableConfig) -> Dict[str, Any]:
    """Get training progress and completion status for a manager's direct reports."""
    logger.info("[Tool] TeamTrainingProgressTool")
    return _team_dashboard_impl(config)


@tool
def get_team_skill_gaps(config: RunnableConfig) -> Dict[str, Any]:
    """Get aggregated skill gaps for a manager's direct reports."""
    logger.info("[Tool] TeamSkillGapTool")
    return _team_dashboard_impl(config)


@tool
def get_team_training_analysis(config: RunnableConfig) -> Dict[str, Any]:
    """Analyze which employees in the team need the most training."""
    logger.info("[Tool] TeamTrainingAnalysisTool")
    return _team_dashboard_impl(config)


@tool
def get_team_readiness_analysis(config: RunnableConfig) -> Dict[str, Any]:
    """Get average readiness score of the team."""
    logger.info("[Tool] TeamReadinessTool")
    return _team_dashboard_impl(config)


@tool
def get_team_skill_risks(config: RunnableConfig) -> Dict[str, Any]:
    """Summarize skill risks for the team/department."""
    logger.info("[Tool] TeamSkillRiskTool")
    return _team_dashboard_impl(config)


@tool
def get_workforce_forecasting(config: RunnableConfig) -> Dict[str, Any]:
    """Provide workforce forecasting projections for the department."""
    logger.info("[Tool] WorkforceForecastTool")
    emp_service = _get_service(config, "employee_service")
    ml_service = _get_service(config, "ml_service")
    
    if not emp_service or not ml_service:
        return {"error": "Services unavailable"}
        
    cfg = config.get("configurable", {})
    auth_emp_num = cfg.get("authenticated_employee_number")
    auth_emp_id = cfg.get("authenticated_employee_id")
    
    caller_ident = auth_emp_num if auth_emp_num else str(auth_emp_id) if auth_emp_id else "EMP1001"
    caller = emp_service.get_employee_profile(caller_ident)
    if not caller:
        return {"error": "Authentication error: Caller profile not found."}
        
    mgr = emp_service.employee_repo.get_by_id(caller["id"])
    dept_id = mgr.department_id if mgr else 1
    
    db = emp_service.employee_repo.db
    from app.database.models import WorkforceForecast
    forecasts = db.query(WorkforceForecast).filter(WorkforceForecast.department_id == dept_id).all()
    
    return {
        "department_id": dept_id,
        "department": caller.get("department", "Unknown"),
        "forecasts": [
            {
                "target_year": f.target_year,
                "current_headcount": f.current_headcount,
                "projected_headcount": f.projected_headcount,
                "required_headcount": f.required_headcount,
                "gap": f.gap
            }
            for f in forecasts
        ]
    }


@tool
def get_hr_organization_analytics(config: RunnableConfig) -> Dict[str, Any]:
    """Retrieve organization-wide workforce readiness and skill gap analytics for HR."""
    logger.info("[Tool] HROrganizationAnalyticsTool")
    emp_service = _get_service(config, "employee_service")
    ml_service = _get_service(config, "ml_service")
    
    if not emp_service or not ml_service:
        return {"error": "Services unavailable"}
        
    cfg = config.get("configurable", {})
    auth_emp_num = cfg.get("authenticated_employee_number")
    auth_emp_id = cfg.get("authenticated_employee_id")
    
    caller_ident = auth_emp_num if auth_emp_num else str(auth_emp_id) if auth_emp_id else "EMP1002"
    caller = emp_service.get_employee_profile(caller_ident)
    if not caller:
        return {"error": "Authentication error: Caller profile not found."}
        
    if caller.get("department") != "Human Resources & L&D":
        return {"error": "Access Denied: Organization-wide analytics are restricted to HR personnel."}
        
    return ml_service.get_hr_dashboard()


# ---------------------------------------------------------------------------
# Tool Registry
# ---------------------------------------------------------------------------

ALL_WORKFORCE_TOOLS = [
    search_employees,
    get_employee_profile,
    get_department_info,
    analyze_skill_gap,
    get_career_goals,
    get_training_recommendations,
    get_learning_progress,
    get_training_progress,
    get_manager_analytics,
    calculate_readiness_score,
    predict_future_skill_demand,
    forecast_workforce_headcount,
    identify_workforce_skill_risks,
    query_company_policy,
    get_team_training_progress,
    get_team_skill_gaps,
    get_team_training_analysis,
    get_team_readiness_analysis,
    get_team_skill_risks,
    get_workforce_forecasting,
    get_hr_organization_analytics
]

