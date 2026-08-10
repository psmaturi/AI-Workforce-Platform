import pytest
from app.ml.skill_gap_model import analyze_skill_gap
from app.ml.readiness_score import calculate_readiness_score
from app.ml.training_recommendation import recommend_training
from app.ml.skill_risk import identify_skill_risks

def test_analyze_skill_gap():
    emp_skills = [
        {"skill_name": "Python", "proficiency_level": 5},
        {"skill_name": "SQL", "proficiency_level": 2},
        {"skill_name": "Statistics", "proficiency_level": 1}
    ]
    
    target_skills = [
        {"skill_name": "Python", "required_proficiency": 4},
        {"skill_name": "SQL", "required_proficiency": 4},
        {"skill_name": "Statistics", "required_proficiency": 3},
        {"skill_name": "Machine Learning", "required_proficiency": 3}
    ]
    
    result = analyze_skill_gap(emp_skills, target_skills)
    
    assert result["total_requirements"] == 4
    assert result["met_requirements"] == 1 # Only Python
    assert result["coverage_percentage"] == 25.0
    
    missing = [s["skill"] for s in result["missing_skills"]]
    assert "Machine Learning" in missing
    
    upgrade = [s["skill"] for s in result["upgrade_needed"]]
    assert "SQL" in upgrade
    assert "Statistics" in upgrade

def test_calculate_readiness_score():
    # 75% skills (37.5 points), Experience match (25 points), Rating 4.0 (12 points), Training 100% (10 points)
    # 37.5 + 25 + 12 + 10 = 84.5
    result = calculate_readiness_score(
        skill_coverage_pct=75.0,
        experience_months=48,
        required_experience_months=36,
        performance_rating=4.0,
        training_completion_pct=100.0
    )
    
    assert result["readiness_score"] == 84.5
    assert result["classification"] == "Ready"

def test_recommend_training():
    emp_skills = [{"skill_name": "Python", "proficiency_level": 1}]
    target_skills = [{"skill_name": "Python", "required_proficiency": 4}]
    
    courses = [
        {"id": 1, "title": "Advanced Python", "target_skill": "Python", "difficulty_level": "Advanced"},
        {"id": 2, "title": "Beginner Python", "target_skill": "Python", "difficulty_level": "Beginner"}
    ]
    
    result = recommend_training(emp_skills, target_skills, courses)
    
    assert len(result) == 2
    # Because employee has level 1 (low), beginner course should score higher on difficulty match
    assert result[0]["course_id"] == 2 # Beginner Python should be ranked first

def test_identify_skill_risks():
    employees = [
        {"skills": [{"skill_name": "Python"}]}
    ]
    
    req_skills = ["Python", "Machine Learning"]
    
    result = identify_skill_risks("Data", employees, req_skills)
    
    # Python has 1 person, ML has 0
    risks = {r["skill"]: r["risk_level"] for r in result}
    assert risks["Machine Learning"] == "Critical"
    assert "Python" not in risks # Since there's only 1 employee total, 100% coverage, so no single-person dependency risk (Wait, single person rule says count==1 and total_employees>1)
