"""
ML model prediction utilities
"""
from typing import Dict, Any, Optional
from uuid import UUID
import structlog
from app.domains.models.trainer import ModelTrainer

logger = structlog.get_logger()


class ModelPredictor:
    """Make predictions using trained ML models"""
    
    def __init__(self, models_dir: str = "models"):
        self.trainer = ModelTrainer(models_dir)
        self.models = {}
    
    def load_models(self):
        """Load all available models"""
        try:
            self.models['success'] = self.trainer.load_model('success_prediction')
            logger.info("Success prediction model loaded")
        except FileNotFoundError:
            logger.warning("Success prediction model not found")
        
        try:
            self.models['response_time'] = self.trainer.load_model('response_time_prediction')
            logger.info("Response time prediction model loaded")
        except FileNotFoundError:
            logger.warning("Response time prediction model not found")
    
    def predict_success(
        self,
        application: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict if an application will be successful
        
        Returns:
            Dict with prediction and confidence
        """
        if 'success' not in self.models:
            return {
                "prediction": None,
                "confidence": None,
                "error": "Model not available"
            }
        
        try:
            # Prepare features
            df = self.trainer.prepare_features([application])
            
            # Predict
            model = self.models['success']
            prediction = model.predict(df)[0]
            probabilities = model.predict_proba(df)[0]
            
            confidence = float(max(probabilities))
            
            return {
                "prediction": bool(prediction),
                "confidence": confidence,
                "probability_accepted": float(probabilities[1]),
                "probability_rejected": float(probabilities[0])
            }
        except Exception as e:
            logger.error("Error predicting success", error=str(e))
            return {
                "prediction": None,
                "confidence": None,
                "error": str(e)
            }
    
    def predict_response_time(
        self,
        application: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict response time in days
        
        Returns:
            Dict with predicted days
        """
        if 'response_time' not in self.models:
            return {
                "predicted_days": None,
                "error": "Model not available"
            }
        
        try:
            # Prepare features
            df = self.trainer.prepare_features([application])
            
            # Predict
            model = self.models['response_time']
            predicted_days = model.predict(df)[0]
            
            return {
                "predicted_days": float(predicted_days),
                "predicted_days_rounded": int(round(predicted_days))
            }
        except Exception as e:
            logger.error("Error predicting response time", error=str(e))
            return {
                "predicted_days": None,
                "error": str(e)
            }

