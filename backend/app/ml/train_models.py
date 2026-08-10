"""Training script to generate synthetic historical data and train ML models."""

import os
import random
import pandas as pd
from app.ml.skill_demand_prediction import SkillDemandPredictor
from app.ml.workforce_forecasting import WorkforceForecaster
from app.utils.logger import logger

def generate_synthetic_skill_data() -> pd.DataFrame:
    """Generate DEMO/SYNTHETIC historical skill demand data."""
    data = []
    # Departments: 0=EAF, 1=Rolling Mill, 2=Maintenance, 3=AI/Digital
    for _ in range(500):
        dept = random.randint(0, 3)
        current_demand = random.uniform(10, 100)
        hiring_demand = random.uniform(0, 50)
        trend = random.uniform(0.5, 2.0)
        
        # Synthetic relationship: High demand + high trend = Critical/High
        score = (current_demand * 0.4) + (hiring_demand * 0.4) + (trend * 20)
        
        if score > 70:
            cat = 3 # Critical
        elif score > 50:
            cat = 2 # High
        elif score > 30:
            cat = 1 # Medium
        else:
            cat = 0 # Low
            
        data.append({
            'department_encoded': dept,
            'current_demand': current_demand,
            'hiring_demand': hiring_demand,
            'industry_trend_score': trend,
            'demand_category_encoded': cat
        })
        
    return pd.DataFrame(data)

def generate_synthetic_workforce_data() -> pd.DataFrame:
    """Generate DEMO/SYNTHETIC historical workforce forecast data."""
    data = []
    for year in range(2020, 2026):
        for dept in range(0, 4):
            for role in range(0, 5):
                current_headcount = random.randint(10, 200)
                attrition = random.uniform(0.02, 0.15)
                
                # Baseline growth 2-5% + attrition replacement
                required = current_headcount * (1 + random.uniform(0.02, 0.05)) + (current_headcount * attrition)
                
                data.append({
                    'year': year,
                    'department_encoded': dept,
                    'role_encoded': role,
                    'current_headcount': current_headcount,
                    'attrition_rate': attrition,
                    'required_headcount': required
                })
                
    return pd.DataFrame(data)

def train_and_save_models():
    logger.info("Generating synthetic data for Skill Demand...")
    skill_df = generate_synthetic_skill_data()
    skill_model = SkillDemandPredictor()
    skill_metrics = skill_model.train(skill_df)
    logger.info(f"Skill Model trained. Metrics: {skill_metrics}")
    
    logger.info("Generating synthetic data for Workforce Forecast...")
    wf_df = generate_synthetic_workforce_data()
    wf_model = WorkforceForecaster()
    wf_metrics = wf_model.train(wf_df)
    logger.info(f"Workforce Model trained. Metrics: {wf_metrics}")
    
    # Save models
    models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models")
    os.makedirs(models_dir, exist_ok=True)
    
    skill_path = os.path.join(models_dir, "skill_demand_model.joblib")
    wf_path = os.path.join(models_dir, "workforce_forecast_model.joblib")
    
    skill_model.save(skill_path)
    wf_model.save(wf_path)
    logger.info(f"Models saved successfully to {models_dir}")

if __name__ == "__main__":
    train_and_save_models()
