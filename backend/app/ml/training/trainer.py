import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from typing import Dict, List, Optional, Tuple
import numpy as np
from pathlib import Path
import json
from datetime import datetime

from ..models.health_models import HealthRiskModel, AnomalyDetectionModel, HealthTrendPredictor


class ModelTrainer:
    def __init__(
        self,
        model: nn.Module,
        device: str = "cpu",
        learning_rate: float = 0.001,
        weight_decay: float = 1e-5,
    ):
        self.model = model.to(device)
        self.device = device
        self.optimizer = optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode="min", factor=0.5, patience=5, verbose=True
        )
        self.history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
        
    def train_epoch(self, train_loader: DataLoader, criterion: nn.Module) -> Tuple[float, float]:
        self.model.train()
        total_loss = 0.0
        correct = 0
        total = 0
        
        for batch_x, batch_y in train_loader:
            batch_x = batch_x.to(self.device)
            batch_y = batch_y.to(self.device)
            
            self.optimizer.zero_grad()
            outputs = self.model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            
            self.optimizer.step()
            
            total_loss += loss.item()
            
            if outputs.dim() > 1 and outputs.size(1) > 1:
                _, predicted = torch.max(outputs, 1)
                _, labels = torch.max(batch_y, 1) if batch_y.dim() > 1 else (None, batch_y)
                correct += (predicted == labels).sum().item()
                total += labels.size(0)
        
        avg_loss = total_loss / len(train_loader)
        accuracy = correct / total if total > 0 else 0.0
        
        return avg_loss, accuracy
    
    def validate(self, val_loader: DataLoader, criterion: nn.Module) -> Tuple[float, float]:
        self.model.eval()
        total_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                batch_x = batch_x.to(self.device)
                batch_y = batch_y.to(self.device)
                
                outputs = self.model(batch_x)
                loss = criterion(outputs, batch_y)
                
                total_loss += loss.item()
                
                if outputs.dim() > 1 and outputs.size(1) > 1:
                    _, predicted = torch.max(outputs, 1)
                    _, labels = torch.max(batch_y, 1) if batch_y.dim() > 1 else (None, batch_y)
                    correct += (predicted == labels).sum().item()
                    total += labels.size(0)
        
        avg_loss = total_loss / len(val_loader)
        accuracy = correct / total if total > 0 else 0.0
        
        return avg_loss, accuracy
    
    def train(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        criterion: nn.Module,
        epochs: int = 50,
        early_stopping_patience: int = 10,
    ) -> Dict:
        best_val_loss = float("inf")
        patience_counter = 0
        best_model_state = None
        
        for epoch in range(epochs):
            train_loss, train_acc = self.train_epoch(train_loader, criterion)
            val_loss, val_acc = self.validate(val_loader, criterion)
            
            self.history["train_loss"].append(train_loss)
            self.history["val_loss"].append(val_loss)
            self.history["train_acc"].append(train_acc)
            self.history["val_acc"].append(val_acc)
            
            self.scheduler.step(val_loss)
            
            print(f"Epoch {epoch + 1}/{epochs}")
            print(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}")
            print(f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}")
            
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                best_model_state = self.model.state_dict().copy()
            else:
                patience_counter += 1
                
            if patience_counter >= early_stopping_patience:
                print(f"Early stopping triggered at epoch {epoch + 1}")
                break
        
        if best_model_state:
            self.model.load_state_dict(best_model_state)
        
        return self.history
    
    def save_model(self, path: str, metadata: Optional[Dict] = None):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        checkpoint = {
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "history": self.history,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        if metadata:
            checkpoint["metadata"] = metadata
        
        torch.save(checkpoint, path)
        print(f"Model saved to {path}")
    
    def load_model(self, path: str):
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        self.history = checkpoint.get("history", self.history)
        print(f"Model loaded from {path}")
        return checkpoint.get("metadata", {})


class RiskModelTrainer(ModelTrainer):
    def __init__(self, input_size: int, device: str = "cpu", **kwargs):
        model = HealthRiskModel(input_size=input_size)
        super().__init__(model, device, **kwargs)
        self.criterion = nn.CrossEntropyLoss()
    
    def train_epoch(self, train_loader: DataLoader, criterion: nn.Module = None) -> Tuple[float, float]:
        return super().train_epoch(train_loader, criterion or self.criterion)
    
    def validate(self, val_loader: DataLoader, criterion: nn.Module = None) -> Tuple[float, float]:
        return super().validate(val_loader, criterion or self.criterion)


class AnomalyDetectorTrainer(ModelTrainer):
    def __init__(self, input_size: int, device: str = "cpu", **kwargs):
        model = AnomalyDetectionModel(input_size=input_size)
        super().__init__(model, device, **kwargs)
        self.criterion = nn.MSELoss()
    
    def train_epoch(self, train_loader: DataLoader, criterion: nn.Module = None) -> Tuple[float, float]:
        self.model.train()
        total_loss = 0.0
        
        for batch_x, _ in train_loader:
            batch_x = batch_x.to(self.device)
            
            self.optimizer.zero_grad()
            x_recon, _ = self.model(batch_x)
            loss = self.criterion(x_recon, batch_x)
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
        
        avg_loss = total_loss / len(train_loader)
        return avg_loss, 0.0
    
    def validate(self, val_loader: DataLoader, criterion: nn.Module = None) -> Tuple[float, float]:
        self.model.eval()
        total_loss = 0.0
        
        with torch.no_grad():
            for batch_x, _ in val_loader:
                batch_x = batch_x.to(self.device)
                x_recon, _ = self.model(batch_x)
                loss = self.criterion(x_recon, batch_x)
                total_loss += loss.item()
        
        avg_loss = total_loss / len(val_loader)
        return avg_loss, 0.0


class TrendPredictorTrainer(ModelTrainer):
    def __init__(self, input_size: int, forecast_horizon: int = 7, device: str = "cpu", **kwargs):
        model = HealthTrendPredictor(input_size=input_size, forecast_horizon=forecast_horizon)
        super().__init__(model, device, **kwargs)
        self.criterion = nn.MSELoss()
    
    def train_epoch(self, train_loader: DataLoader, criterion: nn.Module = None) -> Tuple[float, float]:
        self.model.train()
        total_loss = 0.0
        
        for batch_x, batch_y in train_loader:
            batch_x = batch_x.to(self.device)
            batch_y = batch_y.to(self.device)
            
            self.optimizer.zero_grad()
            predictions = self.model(batch_x)
            loss = self.criterion(predictions, batch_y)
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
        
        avg_loss = total_loss / len(train_loader)
        return avg_loss, 0.0
    
    def validate(self, val_loader: DataLoader, criterion: nn.Module = None) -> Tuple[float, float]:
        self.model.eval()
        total_loss = 0.0
        
        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                batch_x = batch_x.to(self.device)
                batch_y = batch_y.to(self.device)
                predictions = self.model(batch_x)
                loss = self.criterion(predictions, batch_y)
                total_loss += loss.item()
        
        avg_loss = total_loss / len(val_loader)
        return avg_loss, 0.0
