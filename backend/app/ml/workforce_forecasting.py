"""Workforce Forecasting Model (Regression)."""

import pandas as pd
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from typing import Dict, Any
import joblib

class WorkforceForecaster:
    def __init__(self):
        self.model = XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
        self.is_trained = False
        
    def train(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Train the regression model.
        Expects df with features: ['year', 'department_encoded', 'role_encoded', 'current_headcount', 'attrition_rate']
        and target: 'required_headcount'
        """
        X = df[['year', 'department_encoded', 'role_encoded', 'current_headcount', 'attrition_rate']]
        y = df['required_headcount']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        preds = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        r2 = r2_score(y_test, preds)
        
        return {
            "mae": round(mae, 4),
            "r2": round(r2, 4)
        }
        
    def predict(self, features: Dict[str, float]) -> int:
        """Predict the required headcount for a future year."""
        if not self.is_trained:
            raise ValueError("Model must be trained or loaded before predicting.")
            
        X = pd.DataFrame([features])
        # XGBoost output is float, round to nearest int headcount
        pred = self.model.predict(X)[0]
        return max(int(round(pred)), 0)

    def save(self, filepath: str):
        joblib.dump(self.model, filepath)
        
    def load(self, filepath: str):
        self.model = joblib.load(filepath)
        self.is_trained = True
