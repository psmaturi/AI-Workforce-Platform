"""Skill Gap Deterministic Engine."""

from typing import Dict, List, Any

def analyze_skill_gap(employee_skills: List[Dict[str, Any]], target_role_skills: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compare an employee's current skills against a target role's required skills.
    
    Args:
        employee_skills: List of dicts with 'skill_name' and 'proficiency_level' (1-5 integer ideally).
        target_role_skills: List of dicts with 'skill_name', 'required_proficiency', and 'is_core'.
        
    Returns:
        Dict containing missing skills, upgrade needed skills, coverage %, and gap %.
    """
    emp_skill_map = {s['skill_name'].lower(): s['proficiency_level'] for s in employee_skills}
    
    missing_skills = []
    upgrade_needed = []
    total_required = len(target_role_skills)
    met_requirements = 0
    
    for req in target_role_skills:
        req_name = req['skill_name']
        req_prof = req.get('required_proficiency', 3)
        
        emp_prof = emp_skill_map.get(req_name.lower())
        
        if emp_prof is None:
            missing_skills.append({
                "skill": req_name,
                "required": req_prof,
                "current": 0,
                "gap": req_prof
            })
        elif emp_prof < req_prof:
            upgrade_needed.append({
                "skill": req_name,
                "required": req_prof,
                "current": emp_prof,
                "gap": req_prof - emp_prof
            })
        else:
            met_requirements += 1
            
    coverage_pct = round((met_requirements / total_required) * 100, 2) if total_required > 0 else 100.0
    gap_pct = round(100.0 - coverage_pct, 2)
    
    return {
        "coverage_percentage": coverage_pct,
        "gap_percentage": gap_pct,
        "missing_skills": missing_skills,
        "upgrade_needed": upgrade_needed,
        "met_requirements": met_requirements,
        "total_requirements": total_required
    }
