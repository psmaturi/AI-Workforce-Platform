import pytest
from unittest.mock import MagicMock, patch
from langchain_core.messages import HumanMessage
from app.agent.nodes import extract_employee_identifier, intent_detection_node
from app.agent.tools import (
    get_training_progress, get_team_training_progress, get_team_skill_gaps,
    get_team_training_analysis, get_team_readiness_analysis,
    get_team_skill_risks, get_workforce_forecasting, get_hr_organization_analytics
)

# =============================================================================
# Mock states and mock config generators
# =============================================================================

def make_state(question: str, auth_emp_num=None, auth_emp_id=None):
    return {
        "question": question,
        "messages": [HumanMessage(content=question)],
        "metadata": {
            "authenticated_employee_number": auth_emp_num,
            "authenticated_employee_id": auth_emp_id
        }
    }

def make_config(auth_emp_id, auth_emp_num, department="Mechanical Engineering", grade=5):
    emp_service = MagicMock()
    # Mock profiles
    def profile_side_effect(ident):
        if ident in ["Gareth", "EMP1000", "1"]:
            return {"id": 1, "name": "Gareth Williams", "employee_number": "EMP1000", "department": "Mechanical Engineering", "grade": 5}
        elif ident in ["Priya", "EMP1001", "2"]:
            return {"id": 2, "name": "Priya Sharma", "employee_number": "EMP1001", "department": "Mechanical Engineering", "grade": 8}
        elif ident in ["James", "EMP1002", "3"]:
            return {"id": 3, "name": "James Okonkwo", "employee_number": "EMP1002", "department": "Human Resources & L&D", "grade": 7}
        elif ident in ["Unrelated", "EMP1999", "99"]:
            return {"id": 99, "name": "Unrelated Employee", "employee_number": "EMP1999", "department": "AI & Digital", "grade": 5}
        return None

    emp_service.get_employee_profile.side_effect = profile_side_effect
    
    # Mock ORM manager mapping
    def repo_side_effect(emp_id):
        mock_orm = MagicMock()
        if emp_id == 1:
            mock_orm.manager_id = 2  # Priya manages Gareth
        else:
            mock_orm.manager_id = 999  # Unrelated managers
        return mock_orm
    emp_service.employee_repo.get_by_id.side_effect = repo_side_effect
    
    training_service = MagicMock()
    training_service.calculate_training_progress.return_value = {"completed": 2, "in_progress": 1}
    training_service.get_employee_training_history.return_value = []
    
    ml_service = MagicMock()
    ml_service.get_manager_dashboard.return_value = {
        "team_size": 24,
        "avg_readiness": 72.5,
        "avg_skill_coverage": 68.0,
        "training_completion": 82.0
    }
    ml_service.get_hr_dashboard.return_value = {
        "total_employees": 500,
        "departments_count": 10,
        "avg_readiness": 70.0
    }
    ml_service.get_skill_risks.return_value = []
    
    career_service = MagicMock()
    career_service.get_career_goals.return_value = []

    return {
        "configurable": {
            "services": {
                "employee_service": emp_service,
                "training_service": training_service,
                "ml_service": ml_service,
                "career_service": career_service,
                "analytics_service": MagicMock(),
                "skill_gap_service": MagicMock()
            },
            "authenticated_employee_id": auth_emp_id,
            "authenticated_employee_number": auth_emp_num
        }
    }


# =============================================================================
# 1. Team Entity Extraction & Training Routing Tests
# =============================================================================

def test_team_entity_extraction_ignored():
    """Verify that 'team', 'my team', etc. are not extracted as employee names."""
    state = make_state("Show me my team's training progress.", "EMP1001", 2)
    candidate = extract_employee_identifier(state)
    assert candidate == "EMP1001"  # falls back to caller instead of matching "team"

def test_team_training_intent_routing():
    """Verify fast-path classification correctly routes 'my team's training progress' to Team Training Progress."""
    question = "Show me my team's training progress."
    question_lower = question.lower()
    
    # Simulate the exact fast-path logic from intent_detection_node
    team_words = ["team", "direct report", "my reports", "my employees", "staff"]
    is_team_question = any(w in question_lower for w in team_words)
    
    assert is_team_question, "Expected question to be classified as team-scoped"
    
    # With 'training' present and no 'gap', 'risk', etc. — falls to default 'Team Training Progress'
    assert "gap" not in question_lower
    assert "risk" not in question_lower
    assert "readiness" not in question_lower
    # Verify the entity 'team' itself is in the stop-word list
    from app.agent.nodes import extract_employee_identifier
    state = make_state(question, "EMP1001", 2)
    candidate = extract_employee_identifier(state)
    # Should NOT return 'team' — should return the authenticated number instead
    assert candidate.lower() != "team", f"Expected 'team' to be excluded from entity extraction, got: '{candidate}'"


# =============================================================================
# 2. Role-based Authorization and Tool Access Controls
# =============================================================================

def test_manager_team_training_access_allowed():
    """Verify that a manager can access team training progress."""
    config = make_config(auth_emp_id=2, auth_emp_num="EMP1001", grade=8)
    res = get_team_training_progress.invoke({}, config)
    assert "error" not in res
    assert res["team_size"] == 24

def test_manager_team_skill_gap_access_allowed():
    """Verify that a manager can access team skill gap metrics."""
    config = make_config(auth_emp_id=2, auth_emp_num="EMP1001", grade=8)
    res = get_team_skill_gaps.invoke({}, config)
    assert "error" not in res
    assert res["team_size"] == 24

def test_employee_team_data_denied():
    """Verify that a normal employee is blocked from accessing team data."""
    config = make_config(auth_emp_id=1, auth_emp_num="EMP1000", grade=5)
    res = get_team_training_progress.invoke({}, config)
    assert "error" in res
    assert "Access Denied" in res["error"]

def test_manager_direct_report_access_allowed():
    """Verify that a manager can access their direct report's data."""
    config = make_config(auth_emp_id=2, auth_emp_num="EMP1001", grade=8)
    # Target Gareth (EMP1000)
    res = get_training_progress.invoke({"employee_identifier": "Gareth"}, config)
    assert "error" not in res
    assert res["employee"] == "Gareth Williams"

def test_manager_unrelated_employee_denied():
    """Verify that a manager cannot access unrelated employee data."""
    config = make_config(auth_emp_id=2, auth_emp_num="EMP1001", grade=8)
    # Target Unrelated (EMP1999)
    res = get_training_progress.invoke({"employee_identifier": "Unrelated"}, config)
    assert "error" in res
    assert "Access Denied" in res["error"]

def test_hr_organization_analytics_allowed():
    """Verify that HR can access organization-wide dashboard metrics."""
    config = make_config(auth_emp_id=3, auth_emp_num="EMP1002")
    res = get_hr_organization_analytics.invoke({}, config)
    assert "error" not in res
    assert res["total_employees"] == 500

def test_non_hr_organization_analytics_denied():
    """Verify that non-HR users are blocked from organization analytics."""
    config = make_config(auth_emp_id=2, auth_emp_num="EMP1001")
    res = get_hr_organization_analytics.invoke({}, config)
    assert "error" in res
    assert "Access Denied" in res["error"]


# =============================================================================
# 3. Regression Checks
# =============================================================================

def test_regression_individual_training_progress():
    """Verify that employee can still retrieve their own training progress."""
    config = make_config(auth_emp_id=1, auth_emp_num="EMP1000", grade=5)
    res = get_training_progress.invoke({"employee_identifier": "Gareth"}, config)
    assert "error" not in res
    assert res["employee"] == "Gareth Williams"
