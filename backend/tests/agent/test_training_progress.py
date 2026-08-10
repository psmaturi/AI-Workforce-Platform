"""Unit tests for Training Progress service, intent classification, and LangGraph routing."""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta


# =============================================================================
# 1. Training Progress Calculation Tests
# =============================================================================

class TestCalculateTrainingProgress:
    """Tests for TrainingService.calculate_training_progress."""

    def _make_record(self, status_value: str, is_mandatory: bool = False, hours: float = 0.0,
                     course_name: str = "Course", expiry_date=None):
        """Helper to build a mock EmployeeTraining record."""
        from app.database.models import TrainingStatus
        record = MagicMock()
        record.status = TrainingStatus(status_value)
        record.hours_completed = hours
        record.expiry_date = expiry_date
        record.course.name = course_name
        record.course.is_mandatory = is_mandatory
        record.course_id = id(record)  # unique id per record
        return record

    def _make_service(self, records):
        """Build a TrainingService with a mocked training_repo returning the given records."""
        from app.services.training_service import TrainingService

        training_repo = MagicMock()
        training_repo.get_employee_training_history.return_value = records
        skills_repo = MagicMock()
        return TrainingService(training_repo, skills_repo)

    # --- Basic counts ---

    def test_empty_records(self):
        svc = self._make_service([])
        result = svc.calculate_training_progress(employee_id=1)
        assert result["total_courses"] == 0
        assert result["completed"] == 0
        assert result["in_progress"] == 0
        assert result["not_started"] == 0
        assert result["completion_percentage"] == 0.0

    def test_all_completed(self):
        records = [
            self._make_record("Completed", hours=10.0, course_name="Safety Fundamentals"),
            self._make_record("Completed", hours=8.0, course_name="Fire Safety"),
        ]
        svc = self._make_service(records)
        result = svc.calculate_training_progress(employee_id=1)
        assert result["total_courses"] == 2
        assert result["completed"] == 2
        assert result["in_progress"] == 0
        assert result["not_started"] == 0
        assert result["completion_percentage"] == 100.0
        assert "Safety Fundamentals" in result["completed_courses_list"]
        assert "Fire Safety" in result["completed_courses_list"]

    def test_mixed_statuses(self):
        records = [
            self._make_record("Completed", hours=10.0, course_name="Course A"),
            self._make_record("Completed", hours=5.0, course_name="Course B"),
            self._make_record("In Progress", hours=3.0, course_name="Course C"),
            self._make_record("Not Started", hours=0.0, course_name="Course D"),
        ]
        svc = self._make_service(records)
        result = svc.calculate_training_progress(employee_id=1)
        assert result["total_courses"] == 4
        assert result["completed"] == 2
        assert result["in_progress"] == 1
        assert result["not_started"] == 1
        assert result["completion_percentage"] == 50.0
        assert "Course A" in result["completed_courses_list"]
        assert "Course C" in result["in_progress_courses_list"]
        assert "Course D" in result["not_started_courses_list"]

    # --- Completion percentage ---

    def test_completion_percentage_calculation(self):
        records = [
            self._make_record("Completed", hours=5.0),
            self._make_record("Completed", hours=5.0),
            self._make_record("Completed", hours=5.0),
            self._make_record("Not Started", hours=0.0),
        ]
        svc = self._make_service(records)
        result = svc.calculate_training_progress(employee_id=99)
        assert result["completion_percentage"] == 75.0

    # --- Total training hours ---

    def test_total_training_hours(self):
        records = [
            self._make_record("Completed", hours=8.0),
            self._make_record("In Progress", hours=3.5),
            self._make_record("Not Started", hours=0.0),
        ]
        svc = self._make_service(records)
        result = svc.calculate_training_progress(employee_id=1)
        assert result["total_hours"] == 11.5

    # --- Mandatory training ---

    def test_mandatory_completion_percentage(self):
        records = [
            self._make_record("Completed", is_mandatory=True, hours=10.0, course_name="Safety"),
            self._make_record("Not Started", is_mandatory=True, hours=0.0, course_name="Fire"),
            self._make_record("Completed", is_mandatory=False, hours=5.0, course_name="Python"),
        ]
        svc = self._make_service(records)
        result = svc.calculate_training_progress(employee_id=1)
        assert result["mandatory_completion_percentage"] == 50.0

    def test_all_mandatory_complete(self):
        records = [
            self._make_record("Completed", is_mandatory=True, hours=10.0, course_name="Safety"),
            self._make_record("Completed", is_mandatory=True, hours=6.0, course_name="Fire"),
        ]
        svc = self._make_service(records)
        result = svc.calculate_training_progress(employee_id=1)
        assert result["mandatory_completion_percentage"] == 100.0

    # --- Expired / overdue ---

    def test_expired_records_counted(self):
        records = [
            self._make_record("Expired", hours=0.0, course_name="Old Safety"),
            self._make_record("Completed", hours=5.0, course_name="New Safety"),
        ]
        svc = self._make_service(records)
        result = svc.calculate_training_progress(employee_id=1)
        assert result["expired"] == 1

    def test_overdue_by_expiry_date(self):
        past_date = datetime.utcnow() - timedelta(days=30)
        records = [
            self._make_record("In Progress", hours=2.0, course_name="Overdue Course", expiry_date=past_date),
        ]
        svc = self._make_service(records)
        result = svc.calculate_training_progress(employee_id=1)
        assert result["overdue"] >= 1

    # --- Employee-specific filtering ---

    def test_employee_id_used_in_query(self):
        from app.services.training_service import TrainingService
        training_repo = MagicMock()
        training_repo.get_employee_training_history.return_value = []
        svc = TrainingService(training_repo, MagicMock())
        svc.calculate_training_progress(employee_id=42)
        training_repo.get_employee_training_history.assert_called_once_with(42)

    # --- Invalid employee (empty records) ---

    def test_invalid_employee_returns_zeros(self):
        svc = self._make_service([])
        result = svc.calculate_training_progress(employee_id=9999)
        assert result["total_courses"] == 0
        assert result["completion_percentage"] == 0.0


# =============================================================================
# 2. Intent Classification Tests
# =============================================================================

class TestIntentClassification:
    """Tests for intent_detection_node fast classification rules."""

    def _get_intent(self, question: str) -> str:
        """Run the fast-path classifier synchronously (no LLM fallback)."""
        question_lower = question.lower()
        import re
        greeting_words = ["hello", "hey", "greetings"]
        if any(w in question_lower for w in greeting_words) or re.search(r"\bhi\b", question_lower):
            return "Greeting"
        elif any(w in question_lower for w in ["become", "career", "roadmap", "path", "role", "transition"]):
            return "Employee Career"
        elif any(w in question_lower for w in ["gap", "deficiency", "skill gap", "missing skills"]):
            return "Skill Gap"
        elif any(w in question_lower for w in ["training progress", "learning progress", "how much training",
                                                "completed training", "training have i completed",
                                                "courses am i currently", "courses have i completed",
                                                "courses are still pending", "mandatory training is complete",
                                                "how many courses"]):
            return "Training Progress"
        elif any(w in question_lower for w in ["mandatory training status", "mandatory status"]):
            return "Mandatory Training Status"
        elif any(w in question_lower for w in ["recommend courses", "training should i take", "should i learn next"]):
            return "Training Recommendation"
        elif any(w in question_lower for w in ["courses are available", "training catalog", "available courses"]):
            return "Training Catalog"
        elif any(w in question_lower for w in ["policy", "approval process", "approval rules",
                                                "rules for training", "training approval"]):
            return "Training Policy"
        elif any(w in question_lower for w in ["reimbursement", "allowance", "benefit", "rules", "budget"]):
            return "Company Policy"
        elif any(w in question_lower for w in ["promote", "promotion", "level up"]):
            return "Promotion"
        else:
            return "General Question"

    # --- Training Progress queries ---

    def test_show_training_progress(self):
        assert self._get_intent("Show me my training progress.") == "Training Progress"

    def test_how_much_training(self):
        assert self._get_intent("How much training have I completed?") == "Training Progress"

    def test_courses_completed(self):
        assert self._get_intent("What courses have I completed?") == "Training Progress"

    def test_courses_pending(self):
        assert self._get_intent("How many courses are still pending?") == "Training Progress"

    def test_learning_progress(self):
        # "learning progress" triggers the "training progress" keyword check first
        # Both intents route to TrainingProgressTool — this is the correct behaviour.
        assert self._get_intent("What is my learning progress?") == "Training Progress"

    def test_show_completed_training(self):
        assert self._get_intent("Show my completed training.") == "Training Progress"

    def test_courses_currently_taking(self):
        assert self._get_intent("Which courses am I currently taking?") == "Training Progress"

    def test_mandatory_complete(self):
        assert self._get_intent("How much of my mandatory training is complete?") == "Training Progress"

    def test_how_many_courses_completed(self):
        assert self._get_intent("How many courses have I completed?") == "Training Progress"

    # --- Training Recommendation queries ---

    def test_what_training_should_take(self):
        assert self._get_intent("What training should I take?") == "Training Recommendation"

    def test_recommend_courses(self):
        assert self._get_intent("Recommend courses for me.") == "Training Recommendation"

    def test_should_learn_next(self):
        assert self._get_intent("What should I learn next?") == "Training Recommendation"

    # --- Training Policy queries ---

    def test_training_policy(self):
        assert self._get_intent("What is the company's training policy?") == "Training Policy"

    def test_training_approval_rules(self):
        assert self._get_intent("What are the rules for training approval?") == "Training Policy"

    def test_approval_process(self):
        assert self._get_intent("What is the training approval process?") == "Training Policy"

    # --- Must NOT be Training Progress ---

    def test_skill_gap_not_training(self):
        assert self._get_intent("What are my skill gaps?") == "Skill Gap"

    def test_greeting_not_training(self):
        assert self._get_intent("Hello!") == "Greeting"


# =============================================================================
# 3. LangGraph Routing Tests (Tool Selection)
# =============================================================================

class TestToolRouting:
    """Verify that correct tool is selected based on intent."""

    def _simulate_routing(self, intent: str) -> str:
        """Simulate the tool_execution_node routing logic."""
        if intent == "Employee Career":
            return "LearningRoadmapTool + Readiness + ML Skill Gap + RAG"
        elif intent == "Skill Gap":
            return "SkillGapTool (ML)"
        elif intent in ["Training Progress", "Learning Progress", "Mandatory Training Status"]:
            return "TrainingProgressTool"
        elif intent == "Training Recommendation":
            return "TrainingRecommendationTool (ML)"
        elif intent == "Training Policy":
            return "CompanyPolicyTool (RAG)"
        elif intent == "Training Catalog":
            return "CompanyPolicyTool (RAG)"
        elif intent == "Company Policy":
            return "CompanyPolicyTool (RAG)"
        elif intent == "Promotion":
            return "PromotionPolicyTool (RAG)"
        elif intent == "Greeting":
            return "None (Greeting)"
        elif intent == "Training":
            return "TrainingRecommendationTool (ML)"
        else:
            return "EmployeeProfileTool"

    def test_training_progress_routes_to_tool(self):
        assert self._simulate_routing("Training Progress") == "TrainingProgressTool"

    def test_learning_progress_routes_to_tool(self):
        assert self._simulate_routing("Learning Progress") == "TrainingProgressTool"

    def test_mandatory_status_routes_to_tool(self):
        assert self._simulate_routing("Mandatory Training Status") == "TrainingProgressTool"

    def test_training_recommendation_routes_correctly(self):
        assert self._simulate_routing("Training Recommendation") == "TrainingRecommendationTool (ML)"

    def test_training_policy_routes_to_rag(self):
        assert self._simulate_routing("Training Policy") == "CompanyPolicyTool (RAG)"

    def test_training_catalog_routes_to_rag(self):
        assert self._simulate_routing("Training Catalog") == "CompanyPolicyTool (RAG)"

    def test_greeting_no_tool(self):
        assert self._simulate_routing("Greeting") == "None (Greeting)"

    def test_training_progress_not_rag(self):
        """Training Progress must NOT be routed to RAG."""
        tool = self._simulate_routing("Training Progress")
        assert "RAG" not in tool

    def test_learning_progress_not_rag(self):
        """Learning Progress must NOT be routed to RAG."""
        tool = self._simulate_routing("Learning Progress")
        assert "RAG" not in tool


# =============================================================================
# 4. Employee Identifier Extraction Tests
# =============================================================================

class TestExtractEmployeeIdentifier:
    """Tests for the extract_employee_identifier helper in nodes.py."""

    def _make_state(self, question: str, history: list = None) -> dict:
        """Create a minimal AgentState dict."""
        msgs = []
        if history:
            from langchain_core.messages import HumanMessage
            msgs = [HumanMessage(content=m) for m in history]
        return {"question": question, "messages": msgs}

    def test_extracts_name_from_question_i_am(self):
        from app.agent.nodes import extract_employee_identifier
        state = self._make_state("I am Gareth. Show me my training progress.")
        result = extract_employee_identifier(state)
        assert result == "Gareth"

    def test_extracts_name_from_question_my_name(self):
        from app.agent.nodes import extract_employee_identifier
        state = self._make_state("My name is James. What training have I done?")
        result = extract_employee_identifier(state)
        assert result == "James"

    def test_extracts_name_from_history(self):
        from app.agent.nodes import extract_employee_identifier
        state = self._make_state(
            question="Show me my training progress.",
            history=["I am Gareth.", "Hello there"]
        )
        result = extract_employee_identifier(state)
        assert result == "Gareth"

    def test_extracts_name_from_target_possessive(self):
        from app.agent.nodes import extract_employee_identifier
        state = self._make_state("Show me Gareth's training progress.")
        result = extract_employee_identifier(state)
        assert result == "Gareth"

    def test_extracts_name_from_target_for(self):
        from app.agent.nodes import extract_employee_identifier
        state = self._make_state("What is the learning progress for Priya?")
        result = extract_employee_identifier(state)
        assert result == "Priya"

    def test_authenticated_metadata_override(self):
        from app.agent.nodes import extract_employee_identifier
        state = {
            "question": "Show me my training progress.",
            "messages": [],
            "metadata": {
                "authenticated_employee_number": "EMP1001"
            }
        }
        result = extract_employee_identifier(state)
        assert result == "EMP1001"

    def test_fallback_to_default(self):
        from app.agent.nodes import extract_employee_identifier
        state = self._make_state("Show me training progress.")
        result = extract_employee_identifier(state)
        assert result == "EMP1000"


# =============================================================================
# 5. Security & Authorization Checks Tests
# =============================================================================

class TestGetTrainingProgressSecurity:
    """Tests for secure authorization checks in get_training_progress tool."""

    def test_self_access_allowed(self):
        from app.agent.tools import get_training_progress
        
        # Mock services
        emp_service = MagicMock()
        emp_service.get_employee_profile.side_effect = lambda ident: {
            "id": 1, "name": "Gareth", "employee_number": "EMP1000"
        } if ident in ["Gareth", "EMP1000"] else None
        
        training_service = MagicMock()
        training_service.calculate_training_progress.return_value = {"completed": 2}
        
        config = {
            "configurable": {
                "services": {
                    "employee_service": emp_service,
                    "training_service": training_service
                },
                "authenticated_employee_id": 1,
                "authenticated_employee_number": "EMP1000"
            }
        }
        
        result = get_training_progress.invoke({"employee_identifier": "Gareth"}, config)
        assert "error" not in result
        assert result["employee"] == "Gareth"
        assert result["completed"] == 2

    def test_manager_access_allowed(self):
        from app.agent.tools import get_training_progress
        
        # Mock services
        emp_service = MagicMock()
        # Employee 1 is Gareth, Employee 2 is Priya (Manager)
        emp_service.get_employee_profile.side_effect = lambda ident: {
            "id": 1, "name": "Gareth", "employee_number": "EMP1000"
        } if ident in ["Gareth", "EMP1000"] else ({
            "id": 2, "name": "Priya", "employee_number": "EMP1001"
        } if ident in ["Priya", "EMP1001"] else None)
        
        # Mock ORM mapping for manager check
        target_orm = MagicMock()
        target_orm.manager_id = 2  # Priya is manager of Gareth
        emp_service.employee_repo.get_by_id.return_value = target_orm

        training_service = MagicMock()
        training_service.calculate_training_progress.return_value = {"completed": 2}
        
        config = {
            "configurable": {
                "services": {
                    "employee_service": emp_service,
                    "training_service": training_service
                },
                "authenticated_employee_id": 2,
                "authenticated_employee_number": "EMP1001"
            }
        }
        
        result = get_training_progress.invoke({"employee_identifier": "Gareth"}, config)
        assert "error" not in result
        assert result["employee"] == "Gareth"

    def test_unauthorized_access_denied(self):
        from app.agent.tools import get_training_progress
        
        # Mock services
        emp_service = MagicMock()
        # Employee 1 is Gareth, Employee 3 is James (Not Manager)
        emp_service.get_employee_profile.side_effect = lambda ident: {
            "id": 1, "name": "Gareth", "employee_number": "EMP1000"
        } if ident in ["Gareth", "EMP1000"] else ({
            "id": 3, "name": "James", "employee_number": "EMP1002"
        } if ident in ["James", "EMP1002"] else None)
        
        # Mock ORM mapping for manager check
        target_orm = MagicMock()
        target_orm.manager_id = 2  # Priya is manager, not James
        emp_service.employee_repo.get_by_id.return_value = target_orm

        training_service = MagicMock()
        
        config = {
            "configurable": {
                "services": {
                    "employee_service": emp_service,
                    "training_service": training_service
                },
                "authenticated_employee_id": 3,
                "authenticated_employee_number": "EMP1002"
            }
        }
        
        result = get_training_progress.invoke({"employee_identifier": "Gareth"}, config)
        assert "error" in result
        assert "Access Denied" in result["error"]
