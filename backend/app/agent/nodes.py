"""LangGraph Workflow Nodes Module."""

import time
import asyncio
import re
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from app.agent.state import AgentState
from app.agent.prompts import (
    SYSTEM_PROMPT,
    INTENT_CLASSIFICATION_SYSTEM_PROMPT,
    RAG_SYSTEM_PROMPT,
    KNOWLEDGE_INTENTS,
)
from app.llm.ollama_client import get_llm_client
from app.utils.logger import logger


def extract_employee_identifier(state: AgentState) -> str:
    """Extracts employee name or ID from current question or conversation history."""
    question = state.get("question", "")
    
    # 1. Check target patterns first (explicitly asking about someone else)
    patterns_target = [
        r"\b([A-Za-z0-9_]+)'s\s+(?:training|learning|mandatory|courses)",
        r"(?:training|learning|courses)\s+(?:progress\s+)?for\s+([A-Za-z0-9_]+)",
        r"(?:should|has|completed)\s+([A-Za-z0-9_]+)\s+(?:take|complete|done|completed)",
    ]
    for pattern in patterns_target:
        match = re.search(pattern, question, re.IGNORECASE)
        if match:
            candidate = match.group(1).strip(".!? ")
            if candidate.lower() not in ["the", "a", "an", "this", "that", "my", "your", "his", "her", "our", "their", "each", "every", "any", "some", "team", "my team", "our team", "employees", "my employees", "direct reports", "my reports", "staff", "department", "organization", "company", "reports"]:
                return candidate
            
    # 2. Check self-identification patterns in the current question
    patterns_self = [
        r"\bi\s+am\s+([A-Za-z0-9_]+)",
        r"\bmy\s+name\s+is\s+([A-Za-z0-9_]+)"
    ]
    for pattern in patterns_self:
        match = re.search(pattern, question, re.IGNORECASE)
        if match:
            return match.group(1).strip(".!? ")

    # 3. If caller is authenticated, use their authenticated identifier as the default self
    auth_emp = state.get("metadata", {}).get("authenticated_employee_number") or state.get("metadata", {}).get("authenticated_employee_id")
    if auth_emp:
        return str(auth_emp)

    # 4. Check self-identification patterns in history
    messages = state.get("messages", [])
    for msg in reversed(messages):
        content = getattr(msg, "content", "")
        for pattern in patterns_self:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip(".!? ")

    return "EMP1000"  # Default fallback


async def intent_detection_node(state: AgentState) -> Dict[str, Any]:
    """Node 1: Classifies the intent of the user question.

    Args:
        state (AgentState): Current graph state.

    Returns:
        Dict[str, Any]: State updates with classified intent.
    """
    question = state.get("question", "")
    logger.info(f"Received Question: '{question}'")

    start_time = time.time()
    question_lower = question.lower()

    # Fast Pattern Classification Rulebook
    greeting_words = ["hello", "hey", "greetings"]
    if any(w in question_lower for w in greeting_words) or re.search(r"\bhi\b", question_lower):
        intent = "Greeting"
    elif "team" in question_lower or "direct report" in question_lower or "my reports" in question_lower or "my employees" in question_lower or "staff" in question_lower:
        if "gap" in question_lower:
            intent = "Team Skill Gap Analysis"
        elif "most training" in question_lower or "need training" in question_lower or "need the most" in question_lower:
            intent = "Team Training Analysis"
        elif "readiness" in question_lower:
            intent = "Team Readiness Analysis"
        elif "risk" in question_lower:
            intent = "Team Skill Risk Analysis"
        elif "forecast" in question_lower or "shortage" in question_lower or "gaps are expected" in question_lower:
            intent = "Workforce Forecasting"
        else:
            intent = "Team Training Progress"
    elif "organisational" in question_lower or "organization" in question_lower or "highest-risk skills" in question_lower or "highest risk skills" in question_lower or "lowest training completion" in question_lower or "overview of" in question_lower:
        if "shortage" in question_lower or "forecast" in question_lower:
            intent = "Workforce Forecasting"
        else:
            intent = "HR Organization Analytics"
    elif any(w in question_lower for w in ["become", "career", "roadmap", "path", "role", "transition"]):
        intent = "Employee Career"
    elif any(w in question_lower for w in ["gap", "deficiency", "skill gap", "missing skills"]):
        intent = "Skill Gap"
    elif any(w in question_lower for w in ["training progress", "how much training", "completed training", "training have i completed", "courses am i currently", "courses have i completed", "courses are still pending", "show my completed training", "which courses am i currently taking", "how many courses have i completed"]):
        intent = "Training Progress"
    elif any(w in question_lower for w in ["learning progress", "what is my learning progress"]):
        intent = "Learning Progress"
    elif any(w in question_lower for w in ["mandatory training status", "mandatory status", "mandatory training is complete", "mandatory training complete"]):
        intent = "Mandatory Training Status"
    elif any(w in question_lower for w in ["recommend courses", "training should i take", "should i learn next"]):
        intent = "Training Recommendation"
    elif any(w in question_lower for w in ["courses are available", "training catalog", "available courses"]):
        intent = "Training Catalog"
    elif any(w in question_lower for w in ["policy", "approval process", "approval rules", "rules for training", "training approval"]):
        intent = "Training Policy"
    elif any(w in question_lower for w in ["reimbursement", "allowance", "benefit", "rules", "budget"]):
        intent = "Company Policy"
    elif any(w in question_lower for w in ["promote", "promotion", "level up"]):
        intent = "Promotion"
    else:
        # Fallback to LLM Classifier
        try:
            llm = get_llm_client()
            response = await llm.ainvoke([
                SystemMessage(content=INTENT_CLASSIFICATION_SYSTEM_PROMPT),
                HumanMessage(content=question)
            ])
            intent = str(response.content).strip()
        except Exception as e:
            logger.error(f"Intent detection LLM fallback error: {e}")
            intent = "General Question"

    elapsed = time.time() - start_time
    logger.info(f"Intent: {intent}")

    return {
        "intent": intent,
        "metadata": {**state.get("metadata", {}), "intent_detection_time": elapsed},
    }


from langchain_core.runnables.config import RunnableConfig

async def tool_execution_node(state: AgentState, config: RunnableConfig) -> Dict[str, Any]:
    """Node 2: Selects the appropriate tool label and any non-RAG tool data based on intent.

    RAG retrieval is deferred to response_generation_node to avoid blocking
    the event loop with synchronous ChromaDB calls.

    Args:
        state (AgentState): Current graph state.
        config (RunnableConfig): Configuration containing injected services.

    Returns:
        Dict[str, Any]: State updates containing tool selection and result.
    """
    intent = state.get("intent", "General Question")
    question = state.get("question", "")

    start_time = time.time()
    tool_selected = "None"
    tool_result: Dict[str, Any] = {}
    
    # We use a mock logged-in user for Phase 4 demonstration
    current_user = extract_employee_identifier(state)

    try:
        if intent == "Team Training Progress":
            tool_selected = "TeamTrainingProgressTool"
            from app.agent.tools import get_team_training_progress
            logger.info("Database: Employee Training Records")
            res = await asyncio.to_thread(get_team_training_progress.invoke, {}, config)
            tool_result = {"team_training_progress": res}

        elif intent == "Team Skill Gap Analysis":
            tool_selected = "TeamSkillGapTool"
            from app.agent.tools import get_team_skill_gaps
            res = await asyncio.to_thread(get_team_skill_gaps.invoke, {}, config)
            tool_result = {"team_skill_gaps": res}

        elif intent == "Team Training Analysis":
            tool_selected = "TeamTrainingAnalysisTool"
            from app.agent.tools import get_team_training_analysis
            res = await asyncio.to_thread(get_team_training_analysis.invoke, {}, config)
            tool_result = {"team_training_analysis": res}

        elif intent == "Team Readiness Analysis":
            tool_selected = "TeamReadinessTool"
            from app.agent.tools import get_team_readiness_analysis
            res = await asyncio.to_thread(get_team_readiness_analysis.invoke, {}, config)
            tool_result = {"team_readiness": res}

        elif intent == "Team Skill Risk Analysis":
            tool_selected = "TeamSkillRiskTool"
            from app.agent.tools import get_team_skill_risks
            res = await asyncio.to_thread(get_team_skill_risks.invoke, {}, config)
            tool_result = {"team_skill_risks": res}

        elif intent == "Workforce Forecasting":
            tool_selected = "WorkforceForecastTool"
            from app.agent.tools import get_workforce_forecasting
            res = await asyncio.to_thread(get_workforce_forecasting.invoke, {}, config)
            tool_result = {"workforce_forecast": res}

        elif intent == "HR Organization Analytics":
            tool_selected = "HROrganizationAnalyticsTool"
            from app.agent.tools import get_hr_organization_analytics
            res = await asyncio.to_thread(get_hr_organization_analytics.invoke, {}, config)
            tool_result = {"hr_organization_analytics": res}

        elif intent == "Employee Career":
            tool_selected = "LearningRoadmapTool + Readiness + ML Skill Gap + RAG"
            from app.agent.tools import analyze_skill_gap, get_employee_profile, calculate_readiness_score
            
            profile = await asyncio.to_thread(get_employee_profile.invoke, {"employee_identifier": current_user}, config)
            
            # Using Role ID 5 for "Mechanical Specialist" as requested in the demo.
            # In a full system, an LLM extracts this ID.
            target_role_id = 5 
            
            readiness = await asyncio.to_thread(
                calculate_readiness_score.invoke,
                {"employee_identifier": current_user, "target_role_id": target_role_id}, config
            )

            gap = await asyncio.to_thread(
                analyze_skill_gap.invoke,
                {"employee_identifier": current_user, "target_role_id": target_role_id}, config
            )
            tool_result = {"profile": profile, "readiness": readiness, "skill_gap": gap, "rag_query": question}

        elif intent == "Skill Gap":
            tool_selected = "SkillGapTool (ML)"
            from app.agent.tools import analyze_skill_gap
            gap = await asyncio.to_thread(
                analyze_skill_gap.invoke,
                {"employee_identifier": current_user, "target_role_id": 5}, config
            )
            tool_result = {"skill_gap": gap}

        elif intent in ["Training Progress", "Learning Progress", "Mandatory Training Status"]:
            tool_selected = "TrainingProgressTool"
            from app.agent.tools import get_training_progress
            logger.info("Database: Employee Training Records")
            progress = await asyncio.to_thread(
                get_training_progress.invoke,
                {"employee_identifier": current_user}, config
            )
            logger.info("Progress: Calculated")
            tool_result = {"training_progress": progress}

        elif intent == "Training Recommendation":
            tool_selected = "TrainingRecommendationTool (ML)"
            from app.agent.tools import get_training_recommendations
            # Extract a likely skill from the question or default to Python for demo
            ml_courses = await asyncio.to_thread(
                get_training_recommendations.invoke,
                {"skill_name": "Python"}, config
            )
            tool_result = {"ml_courses": ml_courses}

        elif intent == "Training Policy":
            tool_selected = "CompanyPolicyTool (RAG)"
            tool_result = {"rag_query": f"training policy approval process {question}"}

        elif intent == "Training Catalog":
            tool_selected = "CompanyPolicyTool (RAG)"
            tool_result = {"rag_query": f"available courses training catalog {question}"}

        elif intent == "Company Policy":
            tool_selected = "CompanyPolicyTool (RAG)"
            tool_result = {"rag_query": question}

        elif intent == "Promotion":
            tool_selected = "PromotionPolicyTool (RAG)"
            tool_result = {"rag_query": "promotion criteria eligibility requirements"}

        elif intent == "Greeting":
            tool_selected = "None (Greeting)"
            tool_result = {"info": "No tool required for greeting."}

        elif intent == "Training":
            # Legacy fallback — route to recommendation (old single "Training" label)
            tool_selected = "TrainingRecommendationTool (ML)"
            from app.agent.tools import get_training_recommendations
            ml_courses = await asyncio.to_thread(
                get_training_recommendations.invoke,
                {"skill_name": "Python"}, config
            )
            tool_result = {"ml_courses": ml_courses}

        else:
            tool_selected = "EmployeeProfileTool"
            from app.agent.tools import get_employee_profile
            tool_result = await asyncio.to_thread(
                get_employee_profile.invoke,
                {"employee_identifier": current_user}, config
            )

    except Exception as e:
        logger.error(f"Error during tool execution '{tool_selected}': {e}")
        tool_result = {"error": f"Tool execution failed gracefully: {str(e)}"}

    elapsed = time.time() - start_time
    logger.info(f"Tool: {tool_selected}")

    return {
        "tool_selected": tool_selected,
        "tool_result": tool_result,
        "metadata": {**state.get("metadata", {}), "tool_execution_time": elapsed},
    }


async def response_generation_node(state: AgentState) -> Dict[str, Any]:
    """Node 3: Generates the final response using Qwen2.5.

    For knowledge-requiring intents (Company Policy, Training, Promotion, Skill Gap,
    Employee Career), retrieves context from ChromaDB via async-safe aretrieve()
    and injects it as grounded context to the LLM.

    For greetings and general questions, generates a direct conversational response.

    Args:
        state (AgentState): Current graph state.

    Returns:
        Dict[str, Any]: State updates with the final generated response.
    """
    question = state.get("question", "")
    intent = state.get("intent", "General Question")
    tool_selected = state.get("tool_selected", "None")
    tool_result = state.get("tool_result", {})
    messages = state.get("messages", [])

    # Limit chat history to MAX_HISTORY_MESSAGES
    from app.config import settings
    history_limit = settings.MAX_HISTORY_MESSAGES
    
    # We always need the latest HumanMessage and SystemMessage logic, 
    # but the state contains the rolling conversation.
    # We will slice the history if it's too long.
    if len(messages) > history_limit:
        messages = messages[-history_limit:]

    start_time = time.time()
    final_answer = ""

    try:
        llm = get_llm_client()

        if intent in KNOWLEDGE_INTENTS:
            # -------------------------------------------------------------------
            # RAG-Grounded Path: async-safe ChromaDB retrieval + LLM generation
            # -------------------------------------------------------------------
            from app.rag.retriever import aretrieve, format_context

            # Use the refined RAG query from tool_result if available
            rag_query = tool_result.get("rag_query", question) if isinstance(tool_result, dict) else question

            logger.info(f"Executing Graph")
            docs = await aretrieve(query=rag_query)
            rag_context = format_context(docs)

            # Enrich context with non-RAG tool data (e.g., skill gap analysis)
            extra_context = ""
            if isinstance(tool_result, dict):
                if "skill_gap" in tool_result:
                    extra_context = f"\n\n---\n\nSkill Gap Analysis:\n{tool_result['skill_gap']}"
                if "profile" in tool_result:
                    extra_context += f"\n\nEmployee Profile:\n{tool_result['profile']}"
                if "readiness" in tool_result:
                    extra_context += f"\n\nReadiness:\n{tool_result['readiness']}"
                    
            combined_context = rag_context + extra_context
            logger.info(f"Context Length: {len(combined_context)} characters")

            system_prompt = RAG_SYSTEM_PROMPT.format(context=combined_context)
            
            payload = [SystemMessage(content=system_prompt)] + messages + [HumanMessage(content=question)]

            try:
                response = await llm.ainvoke(payload)
            except Exception as llm_err:
                logger.warning(f"LLM Generation failed (possible OOM). Initiating Fallback Strategy. Error: {llm_err}")
                
                # Fallback: Severe Context Compression
                # Try dropping RAG completely if we have ML/tool output, otherwise truncate RAG heavily
                if extra_context:
                    reduced_context = "FALLBACK - RAG EXCLUDED DUE TO RESOURCE LIMITS\n" + extra_context
                else:
                    reduced_context = rag_context[:500] + "...\n(TRUNCATED DUE TO RESOURCE LIMITS)"
                    
                logger.info(f"Fallback Context Length: {len(reduced_context)} characters")
                fallback_prompt = RAG_SYSTEM_PROMPT.format(context=reduced_context)
                
                # Exclude chat history in fallback to save memory
                fallback_payload = [
                    SystemMessage(content=fallback_prompt),
                    HumanMessage(content=question)
                ]
                
                response = await llm.ainvoke(fallback_payload)
            
            final_answer = str(response.content)

        else:
            # -------------------------------------------------------------------
            # Direct Conversational Path (Greetings, General Questions)
            # -------------------------------------------------------------------
            logger.info(f"Executing Graph")
            if intent in ["Training Progress", "Learning Progress", "Mandatory Training Status"]:
                def format_training_progress_response(tr: dict) -> str:
                    progress = tr.get("training_progress", {})
                    if not progress or "error" in progress:
                        return progress.get("error", "Error: Training progress data unavailable.")

                    lines = [
                        "Your Training Progress",
                        "",
                        f"Overall Completion: {progress.get('completion_percentage', 0.0)}%",
                        "",
                        f"Completed: {progress.get('completed', 0)}",
                        f"In Progress: {progress.get('in_progress', 0)}",
                        f"Not Started: {progress.get('not_started', 0)}",
                        "",
                        f"Mandatory Training: {progress.get('mandatory_completion_percentage', 0.0)}% complete"
                    ]
                    
                    completed_list = progress.get("completed_courses_list", [])
                    if completed_list:
                        lines.extend([
                            "",
                            "Completed Training:",
                            *[f"- {c}" for c in completed_list]
                        ])
                        
                    in_progress_list = progress.get("in_progress_courses_list", [])
                    if in_progress_list:
                        lines.extend([
                            "",
                            "Currently In Progress:",
                            *[f"- {c}" for c in in_progress_list]
                        ])
                        
                    not_started_list = progress.get("not_started_courses_list", [])
                    if not_started_list:
                        lines.extend([
                            "",
                            "Recommended Next:",
                            f"- {not_started_list[0]}"
                        ])
                        
                    return "\n".join(lines)

                final_answer = format_training_progress_response(tool_result)
                logger.info("Response: Generated")
            else:
                prompt = f"""{SYSTEM_PROMPT}

User Query: {question}
Detected Intent: {intent}
Tool Output: {tool_result}

Provide a clear, helpful, and professional response."""

                payload = [SystemMessage(content=SYSTEM_PROMPT)] + messages + [HumanMessage(content=prompt)]
                response = await llm.ainvoke(payload)
                logger.info("Response: Generated")
                final_answer = str(response.content)

    except Exception as e:
        logger.error(f"Response generation error: {e}", exc_info=True)
        final_answer = (
            "I am here to assist with workforce intelligence questions. "
            f"However, I encountered an issue: {str(e)}"
        )

    elapsed = time.time() - start_time
    logger.info(f"Graph Completed")
    logger.info(f"LLM Response Time: {elapsed:.2f}s" if intent not in ["Training Progress", "Learning Progress", "Mandatory Training Status"] else f"Generated programmatically")

    return {
        "final_response": final_answer,
        "messages": [HumanMessage(content=question), SystemMessage(content=final_answer)],
        "metadata": {**state.get("metadata", {}), "response_generation_time": elapsed},
    }
