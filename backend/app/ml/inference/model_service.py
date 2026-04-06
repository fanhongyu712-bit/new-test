import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from datetime import datetime, timedelta

from ..models.health_models import (
    HealthRiskModel,
    AnomalyDetectionModel,
    HealthTrendPredictor,
    FallDetectionModel,
)
from ..preprocessing.data_preprocessor import HealthDataPreprocessor


class ModelInferenceService:
    def __init__(
        self,
        model_path: str,
        device: str = "cpu",
        model_type: str = "risk",
    ):
        self.device = device
        self.model_type = model_type
        self.model = None
        self.preprocessor = HealthDataPreprocessor()
        self.model_metadata = {}
        
        self._load_model(model_path)
    
    def _load_model(self, model_path: str):
        path = Path(model_path)
        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        checkpoint = torch.load(path, map_location=self.device)
        self.model_metadata = checkpoint.get("metadata", {})
        
        model_config = self.model_metadata.get("model_config", {})
        
        if self.model_type == "risk":
            self.model = HealthRiskModel(
                input_size=model_config.get("input_size", 10),
                hidden_size=model_config.get("hidden_size", 128),
                num_layers=model_config.get("num_layers", 2),
                num_classes=model_config.get("num_classes", 4),
            )
        elif self.model_type == "anomaly":
            self.model = AnomalyDetectionModel(
                input_size=model_config.get("input_size", 10),
                hidden_size=model_config.get("hidden_size", 64),
                latent_size=model_config.get("latent_size", 32),
            )
        elif self.model_type == "trend":
            self.model = HealthTrendPredictor(
                input_size=model_config.get("input_size", 10),
                hidden_size=model_config.get("hidden_size", 64),
                forecast_horizon=model_config.get("forecast_horizon", 7),
            )
        elif self.model_type == "fall":
            self.model = FallDetectionModel(
                input_size=model_config.get("input_size", 6),
                hidden_size=model_config.get("hidden_size", 128),
            )
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
        
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.to(self.device)
        self.model.eval()
        
        print(f"Model loaded successfully from {model_path}")
    
    def predict(self, data: np.ndarray) -> np.ndarray:
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        with torch.no_grad():
            tensor_data = torch.FloatTensor(data).to(self.device)
            
            if tensor_data.dim() == 2:
                tensor_data = tensor_data.unsqueeze(0)
            
            outputs = self.model(tensor_data)
            
            if isinstance(outputs, tuple):
                outputs = outputs[0]
            
            return outputs.cpu().numpy()
    
    def predict_risk(self, health_data: Dict[str, float]) -> Dict[str, Any]:
        if self.model_type != "risk":
            raise ValueError("This method is only for risk prediction model")
        
        feature_vector = self._prepare_features(health_data)
        prediction = self.predict(feature_vector)
        
        risk_levels = ["low", "medium", "high", "critical"]
        probabilities = self._softmax(prediction[0])
        
        predicted_class = np.argmax(probabilities)
        confidence = probabilities[predicted_class]
        
        return {
            "risk_level": risk_levels[predicted_class],
            "risk_score": float(confidence),
            "probabilities": {
                level: float(prob) for level, prob in zip(risk_levels, probabilities)
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def detect_anomaly(self, health_data: Dict[str, float]) -> Dict[str, Any]:
        if self.model_type != "anomaly":
            raise ValueError("This method is only for anomaly detection model")
        
        feature_vector = self._prepare_features(health_data)
        
        with torch.no_grad():
            tensor_data = torch.FloatTensor(feature_vector).to(self.device)
            x_recon, z = self.model(tensor_data)
            
            reconstruction_error = torch.mean((tensor_data - x_recon) ** 2, dim=1)
            anomaly_score = reconstruction_error.cpu().numpy()[0]
        
        threshold = self.model_metadata.get("anomaly_threshold", 0.1)
        is_anomaly = anomaly_score > threshold
        
        return {
            "is_anomaly": bool(is_anomaly),
            "anomaly_score": float(anomaly_score),
            "threshold": threshold,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def predict_trend(
        self,
        historical_data: List[Dict[str, float]],
        metric_columns: List[str],
    ) -> Dict[str, Any]:
        if self.model_type != "trend":
            raise ValueError("This method is only for trend prediction model")
        
        sequences = np.array([[d[col] for col in metric_columns] for d in historical_data])
        
        with torch.no_grad():
            tensor_data = torch.FloatTensor(sequences).unsqueeze(0).to(self.device)
            predictions = self.model(tensor_data)
        
        predictions_np = predictions.cpu().numpy()[0]
        
        forecast_horizon = predictions_np.shape[0]
        trend_data = []
        
        for i in range(forecast_horizon):
            prediction_point = {
                "timestamp": (datetime.utcnow() + timedelta(hours=i + 1)).isoformat(),
            }
            for j, col in enumerate(metric_columns):
                prediction_point[col] = float(predictions_np[i, j])
            trend_data.append(prediction_point)
        
        return {
            "predictions": trend_data,
            "forecast_horizon": forecast_horizon,
            "generated_at": datetime.utcnow().isoformat(),
        }
    
    def _prepare_features(self, health_data: Dict[str, float]) -> np.ndarray:
        feature_order = self.model_metadata.get("feature_order", list(health_data.keys()))
        features = np.array([[health_data.get(f, 0.0) for f in feature_order]])
        return features
    
    def _softmax(self, x: np.ndarray) -> np.ndarray:
        exp_x = np.exp(x - np.max(x))
        return exp_x / exp_x.sum()


class ModelManager:
    def __init__(self, models_dir: str, device: str = "cpu"):
        self.models_dir = Path(models_dir)
        self.device = device
        self.loaded_models: Dict[str, ModelInferenceService] = {}
    
    def get_model(self, model_name: str, model_type: str) -> ModelInferenceService:
        if model_name in self.loaded_models:
            return self.loaded_models[model_name]
        
        model_path = self.models_dir / f"{model_name}.pt"
        service = ModelInferenceService(
            str(model_path),
            device=self.device,
            model_type=model_type,
        )
        self.loaded_models[model_name] = service
        return service
    
    def unload_model(self, model_name: str):
        if model_name in self.loaded_models:
            del self.loaded_models[model_name]
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        models = []
        for model_file in self.models_dir.glob("*.pt"):
            try:
                checkpoint = torch.load(model_file, map_location=self.device)
                metadata = checkpoint.get("metadata", {})
                models.append({
                    "name": model_file.stem,
                    "path": str(model_file),
                    "type": metadata.get("model_type", "unknown"),
                    "created_at": metadata.get("timestamp", "unknown"),
                })
            except Exception as e:
                print(f"Error loading model {model_file}: {e}")
        return models
    
    def reload_model(self, model_name: str, model_type: str) -> ModelInferenceService:
        self.unload_model(model_name)
        return self.get_model(model_name, model_type)
