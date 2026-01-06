"""
ML Models service
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.database.models import MLModel, ModelPrediction
from app.domains.models.trainer import ModelTrainer
from app.domains.models.predictor import ModelPredictor
import structlog

logger = structlog.get_logger()


class MLModelsService:
    """Service for managing ML models"""
    
    def __init__(self, db: Session):
        self.db = db
        self.trainer = ModelTrainer()
        self.predictor = ModelPredictor()
        self.predictor.load_models()
    
    def train_models(
        self,
        applications: List[Dict[str, Any]],
        version: str = "1.0.0"
    ) -> Dict[str, Any]:
        """
        Train all models with application data
        
        Returns:
            Dict with training results
        """
        results = {}
        
        # Train success model
        try:
            success_result = self.trainer.train_success_model(applications)
            results['success'] = success_result
            
            # Save to database
            model = MLModel(
                model_name=success_result['model_name'],
                model_type=success_result['model_type'],
                version=version,
                file_path=success_result['file_path'],
                accuracy=success_result['accuracy'],
                is_active='true',
                model_metadata={"features": success_result['features']}
            )
            self.db.add(model)
        except Exception as e:
            logger.error("Error training success model", error=str(e))
            results['success'] = {"error": str(e)}
        
        # Train response time model
        try:
            response_result = self.trainer.train_response_time_model(applications)
            results['response_time'] = response_result
            
            # Save to database
            model = MLModel(
                model_name=response_result['model_name'],
                model_type=response_result['model_type'],
                version=version,
                file_path=response_result['file_path'],
                accuracy=response_result.get('rmse'),  # Store RMSE as accuracy
                is_active='true',
                model_metadata={"features": response_result['features']}
            )
            self.db.add(model)
        except Exception as e:
            logger.error("Error training response time model", error=str(e))
            results['response_time'] = {"error": str(e)}
        
        self.db.commit()
        return results
    
    def predict_application_success(
        self,
        application: Dict[str, Any],
        user_id: UUID,
        application_id: UUID
    ) -> Dict[str, Any]:
        """Predict success for an application"""
        prediction = self.predictor.predict_success(application)
        
        # Store prediction
        if prediction.get('prediction') is not None:
            model = self.db.query(MLModel).filter(
                MLModel.model_type == 'success_prediction',
                MLModel.is_active == 'true'
            ).first()
            
            if model:
                pred_record = ModelPrediction(
                    model_id=model.id,
                    user_id=user_id,
                    application_id=application_id,
                    prediction=prediction
                )
                self.db.add(pred_record)
                self.db.commit()
        
        return prediction
    
    def predict_response_time(
        self,
        application: Dict[str, Any],
        user_id: UUID,
        application_id: UUID
    ) -> Dict[str, Any]:
        """Predict response time for an application"""
        prediction = self.predictor.predict_response_time(application)
        
        # Store prediction
        if prediction.get('predicted_days') is not None:
            model = self.db.query(MLModel).filter(
                MLModel.model_type == 'response_time_prediction',
                MLModel.is_active == 'true'
            ).first()
            
            if model:
                pred_record = ModelPrediction(
                    model_id=model.id,
                    user_id=user_id,
                    application_id=application_id,
                    prediction=prediction
                )
                self.db.add(pred_record)
                self.db.commit()
        
        return prediction

