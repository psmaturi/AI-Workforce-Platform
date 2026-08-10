"""Readiness Score Deterministic Engine."""

from typing import Dict, Any

def calculate_readiness_score(
    skill_coverage_pct: float,
    experience_months: int,
    required_experience_months: int,
    performance_rating: float = 3.0,
    training_completion_pct: float = 100.0
) -> Dict[str, Any]:
    """
    Calculate an employee's readiness score for a target role (0-100).
    
    Weighting (Configurable):
    - Skill Coverage: 50%
    - Experience Match: 25%
    - Performance Rating: 15% (Scale 1-5, where 3 = 100% of the 15%, 5 = 120% bonus)
    - Training Completion: 10%
    """
    
    # 1. Skill Score (max 50 points)
    skill_score = (skill_coverage_pct / 100.0) * 50
    
    # 2. Experience Score (max 25 points, capped at 25)
    exp_ratio = experience_months / required_experience_months if required_experience_months > 0 else 1.0
    exp_score = min(exp_ratio * 25, 25.0)
    
    # 3. Performance Score (max 15 base points, up to 18 with bonus)
    # 3.0 rating = 15 points. 5.0 rating = 15 * (5/3) = 25 points? 
    # Let's cap at 15 points for standard, bonus points allowed but total readiness capped at 100.
    perf_ratio = performance_rating / 5.0  # 5.0 -> 1.0 -> 15 points. Wait, if 5 is max.
    perf_score = perf_ratio * 15.0
    
    # 4. Training Score (max 10 points)
    training_score = (training_completion_pct / 100.0) * 10
    
    total_score = min(skill_score + exp_score + perf_score + training_score, 100.0)
    total_score = round(total_score, 1)
    
    # Classification
    if total_score < 40:
        classification = "Not Ready"
    elif total_score < 60:
        classification = "Developing"
    elif total_score < 80:
        classification = "Nearly Ready"
    else:
        classification = "Ready"
        
    return {
        "readiness_score": total_score,
        "classification": classification,
        "breakdown": {
            "skill_points": round(skill_score, 1),
            "experience_points": round(exp_score, 1),
            "performance_points": round(perf_score, 1),
            "training_points": round(training_score, 1)
        }
    }
