"""Training Recommendation Scoring Engine."""

from typing import List, Dict, Any

def recommend_training(
    employee_skills: List[Dict[str, Any]],
    target_role_skills: List[Dict[str, Any]],
    available_courses: List[Dict[str, Any]],
    top_n: int = 5
) -> List[Dict[str, Any]]:
    """
    Recommend training courses based on skill gaps.
    
    Args:
        employee_skills: List of dicts with 'skill_name', 'proficiency_level'
        target_role_skills: List of dicts with 'skill_name', 'required_proficiency'
        available_courses: List of dicts with 'id', 'title', 'target_skill', 'difficulty_level'
        top_n: Number of recommendations to return
        
    Returns:
        List of recommended courses with overall score and explanation.
    """
    # 1. Identify Gaps
    emp_skill_map = {s['skill_name'].lower(): s['proficiency_level'] for s in employee_skills}
    gap_map = {}
    
    for req in target_role_skills:
        skill = req['skill_name'].lower()
        req_prof = req.get('required_proficiency', 3)
        emp_prof = emp_skill_map.get(skill, 0)
        
        if emp_prof < req_prof:
            gap_map[skill] = req_prof - emp_prof
            
    # 2. Score Courses
    scored_courses = []
    
    for course in available_courses:
        target_skill = course.get('target_skill', '').lower()
        
        if target_skill not in gap_map:
            continue  # Only recommend courses for identified gaps
            
        gap_size = gap_map[target_skill]
        
        # Base Match Score
        skill_match_score = 90.0 if gap_size > 0 else 0.0
        
        # Difficulty Match Score (Heuristic: larger gap might need beginner course)
        difficulty = course.get('difficulty_level', 'Beginner').lower()
        diff_score = 50.0
        
        emp_prof = emp_skill_map.get(target_skill, 0)
        if emp_prof <= 1 and difficulty == "beginner":
            diff_score = 100.0
        elif emp_prof == 2 and difficulty == "intermediate":
            diff_score = 100.0
        elif emp_prof >= 3 and difficulty == "advanced":
            diff_score = 100.0
        else:
            diff_score = 70.0 # Partial match
            
        # Overall Score
        overall_score = round((skill_match_score * 0.6) + (diff_score * 0.4), 1)
        
        explanation = (
            f"Addresses your gap in {course.get('target_skill')} "
            f"(Skill Match: {skill_match_score}%, Difficulty Match: {diff_score}%)"
        )
        
        scored_courses.append({
            "course_id": course.get('id'),
            "title": course.get('title'),
            "target_skill": course.get('target_skill'),
            "overall_score": overall_score,
            "explanation": explanation
        })
        
    # 3. Sort and Return
    scored_courses.sort(key=lambda x: x['overall_score'], reverse=True)
    return scored_courses[:top_n]
