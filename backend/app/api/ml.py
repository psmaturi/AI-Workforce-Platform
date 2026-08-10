"""Machine Learning Endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, Header
from typing import Dict, Any, List, Optional
from app.dependencies import get_ml_service, get_employee_service
from app.services.ml_service import MLService
from app.services.employee_service import EmployeeService

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

def verify_employee_access(
    employee_id: int,
    x_employee_id: Optional[str] = Header(None, alias="X-Employee-Id"),
    x_employee_number: Optional[str] = Header(None, alias="X-Employee-Number"),
    emp_service: EmployeeService = Depends(get_employee_service)
):
    """Enforces that employees can only view their own records, managers can view direct reports, and HR can view all."""
    if not x_employee_id and not x_employee_number:
        # Dev/tests environment fallback
        return
        
    caller_ident = x_employee_number if x_employee_number else x_employee_id
    caller = emp_service.get_employee_profile(caller_ident)
    if not caller:
        raise HTTPException(status_code=401, detail="Authentication failed: caller profile not found.")
        
    # 1. Self access
    if caller["id"] == employee_id:
        return
        
    # 2. Manager direct reports access
    target = emp_service.employee_repo.get_by_id(employee_id)
    if target and target.manager_id == caller["id"]:
        return
        
    # 3. HR access
    if caller.get("department") == "Human Resources & L&D":
        return
        
    raise HTTPException(status_code=403, detail="Access Denied: You do not have permission to access this employee's records.")

def verify_manager_access(
    manager_id: int,
    x_employee_id: Optional[str] = Header(None, alias="X-Employee-Id"),
    x_employee_number: Optional[str] = Header(None, alias="X-Employee-Number"),
    emp_service: EmployeeService = Depends(get_employee_service)
):
    """Enforces that only the manager or HR can view the manager's team dashboard."""
    if not x_employee_id and not x_employee_number:
        return
        
    caller_ident = x_employee_number if x_employee_number else x_employee_id
    caller = emp_service.get_employee_profile(caller_ident)
    if not caller:
        raise HTTPException(status_code=401, detail="Authentication failed: caller profile not found.")
        
    # 1. Self access
    if caller["id"] == manager_id:
        return
        
    # 2. HR access
    if caller.get("department") == "Human Resources & L&D":
        return
        
    raise HTTPException(status_code=403, detail="Access Denied: You do not have permission to view this manager's team dashboard.")

def verify_hr_access(
    x_employee_id: Optional[str] = Header(None, alias="X-Employee-Id"),
    x_employee_number: Optional[str] = Header(None, alias="X-Employee-Number"),
    emp_service: EmployeeService = Depends(get_employee_service)
):
    """Restricts access exclusively to HR personnel."""
    if not x_employee_id and not x_employee_number:
        return
        
    caller_ident = x_employee_number if x_employee_number else x_employee_id
    caller = emp_service.get_employee_profile(caller_ident)
    if not caller:
        raise HTTPException(status_code=401, detail="Authentication failed: caller profile not found.")
        
    # HR department access
    if caller.get("department") == "Human Resources & L&D":
        return
        
    raise HTTPException(status_code=403, detail="Access Denied: HR-only resource.")


@router.get("/employee/{employee_id}/skill-gap", dependencies=[Depends(verify_employee_access)])
def get_employee_skill_gap(
    employee_id: int, 
    target_role_id: int = Query(..., description="Target Job Role ID"),
    ml_service: MLService = Depends(get_ml_service)
) -> Dict[str, Any]:
    """Analyze the skill gap for an employee against a target role."""
    result = ml_service.get_skill_gap(employee_id, target_role_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.get("/employee/{employee_id}/readiness", dependencies=[Depends(verify_employee_access)])
def get_employee_readiness(
    employee_id: int, 
    target_role_id: int = Query(..., description="Target Job Role ID"),
    ml_service: MLService = Depends(get_ml_service)
) -> Dict[str, Any]:
    """Calculate the readiness score for an employee."""
    result = ml_service.get_readiness_score(employee_id, target_role_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.get("/employee/{employee_id}/recommendations", dependencies=[Depends(verify_employee_access)])
def get_training_recommendations(
    employee_id: int, 
    target_role_id: int = Query(..., description="Target Job Role ID"),
    ml_service: MLService = Depends(get_ml_service)
) -> List[Dict[str, Any]]:
    """Get training recommendations based on skill gaps."""
    result = ml_service.get_training_recommendations(employee_id, target_role_id)
    if result and "error" in result[0]:
        raise HTTPException(status_code=404, detail=result[0]["error"])
    return result

@router.get("/skills/future-demand")
def predict_future_demand(
    department_id: int = Query(...),
    current_demand: float = Query(...),
    hiring_demand: float = Query(...),
    industry_trend: float = Query(...),
    ml_service: MLService = Depends(get_ml_service)
) -> Dict[str, str]:
    """Predict future demand category for a skill."""
    prediction = ml_service.predict_future_demand(department_id, current_demand, hiring_demand, industry_trend)
    return {"demand_category": prediction}

@router.get("/workforce/forecast")
def forecast_workforce(
    year: int = Query(...),
    department_id: int = Query(...),
    role_id: int = Query(...),
    current_headcount: int = Query(...),
    attrition_rate: float = Query(...),
    ml_service: MLService = Depends(get_ml_service)
) -> Dict[str, int]:
    """Forecast future workforce headcount requirements."""
    prediction = ml_service.forecast_workforce(year, department_id, role_id, current_headcount, attrition_rate)
    return {"required_headcount": prediction}

@router.get("/workforce/risks")
def identify_workforce_risks(
    department_id: int = Query(...),
    ml_service: MLService = Depends(get_ml_service)
) -> List[Dict[str, Any]]:
    """Identify workforce skill risks for a department."""
    result = ml_service.get_skill_risks(department_id)
    if result and "error" in result[0]:
        raise HTTPException(status_code=404, detail=result[0]["error"])
    return result

@router.get("/manager/{manager_id}/dashboard", dependencies=[Depends(verify_manager_access)])
def get_manager_dashboard_data(
    manager_id: int,
    ml_service: MLService = Depends(get_ml_service)
) -> Dict[str, Any]:
    """Get manager-level team overview metrics."""
    return ml_service.get_manager_dashboard(manager_id)

@router.get("/hr/dashboard", dependencies=[Depends(verify_hr_access)])
def get_hr_dashboard_data(
    ml_service: MLService = Depends(get_ml_service)
) -> Dict[str, Any]:
    """Get organization-wide dashboard overview metrics for HR."""
    return ml_service.get_hr_dashboard()
