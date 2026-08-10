"""Skill Demand Prediction Model (Classification)."""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from typing import Dict, Any, Tuple
import joblib

class SkillDemandPredictor:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False
        
    def train(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Train the classification model.
        Expects df with features: ['department_encoded', 'current_demand', 'hiring_demand', 'industry_trend_score']
        and target: 'demand_category' (0: Low, 1: Medium, 2: High, 3: Critical)
        """
        X = df[['department_encoded', 'current_demand', 'hiring_demand', 'industry_trend_score']]
        y = df['demand_category_encoded']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Simple evaluation
        accuracy = self.model.score(X_test, y_test)
        
        return {
            "accuracy": round(accuracy, 4),
            "feature_importances": self.model.feature_importances_.tolist()
        }
        
    def predict(self, features: Dict[str, float]) -> str:
        """Predict the demand category for a given skill."""
        if not self.is_trained:
            raise ValueError("Model must be trained or loaded before predicting.")
            
        X = pd.DataFrame([features])
        pred_encoded = self.model.predict(X)[0]
        
        mapping = {0: "Low", 1: "Medium", 2: "High", 3: "Critical"}
        return mapping.get(pred_encoded, "Unknown")

    def save(self, filepath: str):
        joblib.dump(self.model, filepath)
        
    def load(self, filepath: str):
        self.model = joblib.load(filepath)
        self.is_trained = True
