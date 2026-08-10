"""Model Manager (Singleton) for caching ML models."""

import os
from typing import Dict, Any, Optional
from app.utils.logger import logger
from app.ml.skill_demand_prediction import SkillDemandPredictor
from app.ml.workforce_forecasting import WorkforceForecaster

class ModelManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.models: Dict[str, Any] = {}
        self.models_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models")
        
        # Initialize instances
        self.skill_demand_model = SkillDemandPredictor()
        self.workforce_model = WorkforceForecaster()
        
        self._initialized = True

    def load_all_models(self):
        """Load all Joblib models from disk."""
        logger.info("Initializing ML ModelManager...")
        
        skill_path = os.path.join(self.models_path, "skill_demand_model.joblib")
        if os.path.exists(skill_path):
            self.skill_demand_model.load(skill_path)
            logger.info("Loaded Skill Demand Model.")
        else:
            logger.warning(f"Skill Demand Model not found at {skill_path}")
            
        workforce_path = os.path.join(self.models_path, "workforce_forecast_model.joblib")
        if os.path.exists(workforce_path):
            self.workforce_model.load(workforce_path)
            logger.info("Loaded Workforce Forecasting Model.")
        else:
            logger.warning(f"Workforce Forecasting Model not found at {workforce_path}")

    def get_skill_model(self) -> Optional[SkillDemandPredictor]:
        if self.skill_demand_model.is_trained:
            return self.skill_demand_model
        return None
        
    def get_workforce_model(self) -> Optional[WorkforceForecaster]:
        if self.workforce_model.is_trained:
            return self.workforce_model
        return None

def get_model_manager() -> ModelManager:
    """Dependency injector for ModelManager."""
    manager = ModelManager()
    if not manager.skill_demand_model.is_trained:
        manager.load_all_models()
    return manager
