"""
ML model training utilities
"""
import pickle
from typing import Dict, Any, List, Optional
from pathlib import Path
import structlog
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error, classification_report
import pandas as pd
import numpy as np

logger = structlog.get_logger()


class ModelTrainer:
    """Train ML models for predictions"""
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
    
    def prepare_features(self, applications: List[Dict[str, Any]]) -> pd.DataFrame:
        """Prepare feature matrix from applications"""
        features = []
        
        for app in applications:
            feature_dict = {
                'salary_min': app.get('salary_min', 0) or 0,
                'salary_max': app.get('salary_max', 0) or 0,
                'interview_count': app.get('interview_count', 0),
                'response_time_days': app.get('response_time_days') or 0,
                'time_to_interview_days': app.get('time_to_interview_days') or 0,
                'interest_level_encoded': self._encode_interest(app.get('interest_level', '')),
                'has_deadline': 1 if app.get('deadline') else 0,
                'days_until_deadline': self._days_until_deadline(app.get('deadline')),
            }
            features.append(feature_dict)
        
        return pd.DataFrame(features)
    
    def _encode_interest(self, interest: str) -> int:
        """Encode interest level to numeric"""
        mapping = {
            'very-high': 4,
            'high': 3,
            'medium': 2,
            'low': 1,
        }
        return mapping.get(interest.lower(), 0)
    
    def _days_until_deadline(self, deadline: Optional[str]) -> int:
        """Calculate days until deadline"""
        if not deadline:
            return 999  # No deadline = far future
        
        try:
            from datetime import datetime
            if isinstance(deadline, str):
                deadline_dt = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            else:
                deadline_dt = deadline
            
            now = datetime.now(deadline_dt.tzinfo) if deadline_dt.tzinfo else datetime.now()
            days = (deadline_dt - now).days
            return max(0, days) if days >= 0 else 999
        except:
            return 999
    
    def train_success_model(
        self,
        applications: List[Dict[str, Any]],
        model_name: str = "success_prediction"
    ) -> Dict[str, Any]:
        """
        Train a model to predict application success (accepted/rejected)
        
        Returns:
            Dict with model metadata and metrics
        """
        if len(applications) < 10:
            raise ValueError("Need at least 10 applications to train model")
        
        # Prepare features and labels
        df = self.prepare_features(applications)
        labels = [1 if app.get('status') == 'accepted' else 0 for app in applications]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            df, labels, test_size=0.2, random_state=42
        )
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Save model
        model_path = self.models_dir / f"{model_name}.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        logger.info(
            "Success model trained",
            model_name=model_name,
            accuracy=accuracy,
            samples=len(applications)
        )
        
        return {
            "model_name": model_name,
            "model_type": "success_prediction",
            "accuracy": float(accuracy),
            "file_path": str(model_path),
            "features": list(df.columns),
            "samples": len(applications)
        }
    
    def train_response_time_model(
        self,
        applications: List[Dict[str, Any]],
        model_name: str = "response_time_prediction"
    ) -> Dict[str, Any]:
        """
        Train a model to predict response time in days
        
        Returns:
            Dict with model metadata and metrics
        """
        # Filter applications with response times
        apps_with_response = [
            app for app in applications
            if app.get('response_time_days') is not None
        ]
        
        if len(apps_with_response) < 10:
            raise ValueError("Need at least 10 applications with response times")
        
        # Prepare features and labels
        df = self.prepare_features(apps_with_response)
        labels = [app.get('response_time_days') for app in apps_with_response]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            df, labels, test_size=0.2, random_state=42
        )
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        
        # Save model
        model_path = self.models_dir / f"{model_name}.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        logger.info(
            "Response time model trained",
            model_name=model_name,
            rmse=rmse,
            samples=len(apps_with_response)
        )
        
        return {
            "model_name": model_name,
            "model_type": "response_time_prediction",
            "rmse": float(rmse),
            "file_path": str(model_path),
            "features": list(df.columns),
            "samples": len(apps_with_response)
        }
    
    def load_model(self, model_name: str):
        """Load a trained model"""
        model_path = self.models_dir / f"{model_name}.pkl"
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model {model_name} not found")
        
        with open(model_path, 'rb') as f:
            return pickle.load(f)

