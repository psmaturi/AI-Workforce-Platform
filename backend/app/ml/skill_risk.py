"""Workforce Skill Risk Identification Engine."""

from typing import List, Dict, Any

def identify_skill_risks(
    department_name: str,
    employees: List[Dict[str, Any]],
    department_required_skills: List[str]
) -> List[Dict[str, Any]]:
    """
    Identify workforce skill risks for a department.
    
    Args:
        department_name: Name of the department
        employees: List of employee dicts with their 'skills' (list of dicts)
        department_required_skills: List of critical skills for the department
        
    Returns:
        List of identified risks with risk level and explanation.
    """
    risks = []
    
    # 1. Map skills to employee counts
    skill_coverage = {skill.lower(): 0 for skill in department_required_skills}
    
    for emp in employees:
        for skill in emp.get('skills', []):
            skill_name = skill.get('skill_name', '').lower()
            if skill_name in skill_coverage:
                skill_coverage[skill_name] += 1
                
    # 2. Analyze Risks
    total_employees = len(employees)
    
    for skill_name, count in skill_coverage.items():
        if count == 0:
            risks.append({
                "department": department_name,
                "skill": skill_name.title(),
                "risk_type": "Critical Skill Shortage",
                "risk_level": "Critical",
                "explanation": f"No employees possess the critical skill '{skill_name.title()}'."
            })
        elif count == 1 and total_employees > 1:
            risks.append({
                "department": department_name,
                "skill": skill_name.title(),
                "risk_type": "Single-person Dependency",
                "risk_level": "High",
                "explanation": f"Only 1 employee has the skill '{skill_name.title()}', creating a single point of failure."
            })
        elif count / total_employees < 0.2:
            risks.append({
                "department": department_name,
                "skill": skill_name.title(),
                "risk_type": "Low Skill Coverage",
                "risk_level": "Medium",
                "explanation": f"Less than 20% of the department ({count}/{total_employees}) possesses '{skill_name.title()}'."
            })
            
    return risks
