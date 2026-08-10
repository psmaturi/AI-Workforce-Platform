import asyncio
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from app.dependencies import (
    get_employee_repo, get_department_repo, get_skills_repo, get_training_repo,
    get_employee_service, get_training_service, get_skill_gap_service,
    get_career_service, get_analytics_service, get_chat_service,
    get_ml_service, get_model_manager
)
from app.database.database import SessionLocal
from pprint import pprint

async def run_test():
    # 1. Setup DB Session
    db = SessionLocal()
    
    # 2. Build Repositories
    emp_repo = get_employee_repo(db)
    dept_repo = get_department_repo(db)
    skill_repo = get_skills_repo(db)
    train_repo = get_training_repo(db)
    
    # 3. Build Services
    emp_service = get_employee_service(emp_repo, dept_repo)
    train_service = get_training_service(train_repo, skill_repo)
    gap_service = get_skill_gap_service(emp_repo, skill_repo)
    career_service = get_career_service(emp_repo)
    analytics_service = get_analytics_service(emp_repo, dept_repo)
    model_manager = get_model_manager()
    ml_service = get_ml_service(emp_repo, dept_repo, skill_repo, train_repo, model_manager)
    
    # 4. Build Chat Service
    chat_service = get_chat_service(
        emp_service, train_service, gap_service, career_service, analytics_service, ml_service
    )
    
    # 5. Execute Test Queries
    queries = [
        "I am Gareth. Show me my training progress."
    ]
    
    for q in queries:
        print(f"\n====================================")
        print(f"QUERY: {q}")
        print(f"====================================")
        response = await chat_service.generate_response(q)
        print("\n--- Agent Response ---")
        print(response)
        print("----------------------\n")
        
    db.close()

if __name__ == "__main__":
    asyncio.run(run_test())
