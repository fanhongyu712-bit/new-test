import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
import torch
from torch.utils.data import Dataset, DataLoader


class HealthDataPreprocessor:
    def __init__(
        self,
        sequence_length: int = 24,
        forecast_horizon: int = 6,
        scaler_type: str = "standard",
    ):
        self.sequence_length = sequence_length
        self.forecast_horizon = forecast_horizon
        self.scalers: Dict[str, StandardScaler | MinMaxScaler] = {}
        self.scaler_type = scaler_type
        self.metric_stats: Dict[str, Dict] = {}
        
    def fit(self, data: pd.DataFrame, metric_columns: List[str]) -> "HealthDataPreprocessor":
        for col in metric_columns:
            if self.scaler_type == "standard":
                self.scalers[col] = StandardScaler()
            else:
                self.scalers[col] = MinMaxScaler()
            
            self.scalers[col].fit(data[[col]])
            
            self.metric_stats[col] = {
                "mean": data[col].mean(),
                "std": data[col].std(),
                "min": data[col].min(),
                "max": data[col].max(),
                "median": data[col].median(),
            }
        
        return self
    
    def transform(self, data: pd.DataFrame, metric_columns: List[str]) -> pd.DataFrame:
        transformed = data.copy()
        for col in metric_columns:
            if col in self.scalers:
                transformed[col] = self.scalers[col].transform(data[[col]])
        return transformed
    
    def fit_transform(self, data: pd.DataFrame, metric_columns: List[str]) -> pd.DataFrame:
        self.fit(data, metric_columns)
        return self.transform(data, metric_columns)
    
    def inverse_transform(self, data: np.ndarray, metric_column: str) -> np.ndarray:
        if metric_column in self.scalers:
            return self.scalers[metric_column].inverse_transform(data.reshape(-1, 1)).flatten()
        return data
    
    def create_sequences(
        self,
        data: pd.DataFrame,
        metric_columns: List[str],
        elderly_id_column: str = "elderly_id",
        time_column: str = "recorded_at",
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        sequences = []
        labels = []
        elderly_ids = []
        
        for elderly_id in data[elderly_id_column].unique():
            elderly_data = data[data[elderly_id_column] == elderly_id].sort_values(time_column)
            
            values = elderly_data[metric_columns].values
            
            for i in range(len(values) - self.sequence_length - self.forecast_horizon):
                seq = values[i:i + self.sequence_length]
                label = values[i + self.sequence_length:i + self.sequence_length + self.forecast_horizon]
                
                sequences.append(seq)
                labels.append(label)
                elderly_ids.append(elderly_id)
        
        return np.array(sequences), np.array(labels), np.array(elderly_ids)
    
    def detect_anomalies(
        self,
        data: pd.DataFrame,
        metric_columns: List[str],
        z_threshold: float = 3.0,
    ) -> pd.DataFrame:
        anomalies = pd.DataFrame()
        
        for col in metric_columns:
            if col in self.metric_stats:
                mean = self.metric_stats[col]["mean"]
                std = self.metric_stats[col]["std"]
                
                z_scores = np.abs((data[col] - mean) / std)
                anomaly_mask = z_scores > z_threshold
                
                anomaly_data = data[anomaly_mask].copy()
                anomaly_data["metric"] = col
                anomaly_data["z_score"] = z_scores[anomaly_mask]
                anomaly_data["anomaly_type"] = np.where(
                    data.loc[anomaly_mask, col] > mean,
                    "high",
                    "low"
                )
                
                anomalies = pd.concat([anomalies, anomaly_data])
        
        return anomalies
    
    def handle_missing_values(
        self,
        data: pd.DataFrame,
        metric_columns: List[str],
        method: str = "interpolate",
    ) -> pd.DataFrame:
        handled = data.copy()
        
        for col in metric_columns:
            if method == "interpolate":
                handled[col] = handled[col].interpolate(method="linear")
            elif method == "forward_fill":
                handled[col] = handled[col].ffill()
            elif method == "backward_fill":
                handled[col] = handled[col].bfill()
            elif method == "mean":
                handled[col] = handled[col].fillna(self.metric_stats.get(col, {}).get("mean", 0))
        
        return handled
    
    def extract_features(self, data: pd.DataFrame, metric_columns: List[str]) -> pd.DataFrame:
        features = pd.DataFrame()
        
        for col in metric_columns:
            features[f"{col}_mean"] = data[col].rolling(window=6).mean()
            features[f"{col}_std"] = data[col].rolling(window=6).std()
            features[f"{col}_min"] = data[col].rolling(window=6).min()
            features[f"{col}_max"] = data[col].rolling(window=6).max()
            features[f"{col}_trend"] = data[col].diff()
            features[f"{col}_rate_of_change"] = data[col].pct_change()
        
        return features.fillna(0)


class HealthDataset(Dataset):
    def __init__(
        self,
        sequences: np.ndarray,
        labels: np.ndarray,
        elderly_ids: Optional[np.ndarray] = None,
    ):
        self.sequences = torch.FloatTensor(sequences)
        self.labels = torch.FloatTensor(labels)
        self.elderly_ids = elderly_ids
        
    def __len__(self) -> int:
        return len(self.sequences)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.sequences[idx], self.labels[idx]


class RiskDataset(Dataset):
    def __init__(
        self,
        sequences: np.ndarray,
        risk_labels: np.ndarray,
        elderly_ids: Optional[np.ndarray] = None,
    ):
        self.sequences = torch.FloatTensor(sequences)
        self.risk_labels = torch.LongTensor(risk_labels)
        self.elderly_ids = elderly_ids
        
    def __len__(self) -> int:
        return len(self.sequences)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.sequences[idx], self.risk_labels[idx]


def create_dataloaders(
    sequences: np.ndarray,
    labels: np.ndarray,
    batch_size: int = 32,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    n_samples = len(sequences)
    n_train = int(n_samples * train_ratio)
    n_val = int(n_samples * val_ratio)
    
    indices = np.random.permutation(n_samples)
    train_indices = indices[:n_train]
    val_indices = indices[n_train:n_train + n_val]
    test_indices = indices[n_train + n_val:]
    
    train_dataset = HealthDataset(sequences[train_indices], labels[train_indices])
    val_dataset = HealthDataset(sequences[val_indices], labels[val_indices])
    test_dataset = HealthDataset(sequences[test_indices], labels[test_indices])
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    return train_loader, val_loader, test_loader


def generate_synthetic_data(
    n_elderly: int = 100,
    n_days: int = 30,
    metrics: List[str] = None,
    seed: int = 42,
) -> pd.DataFrame:
    np.random.seed(seed)
    
    if metrics is None:
        metrics = ["heart_rate", "systolic_bp", "diastolic_bp", "temperature", "spo2"]
    
    metric_configs = {
        "heart_rate": {"mean": 75, "std": 10, "min": 50, "max": 120},
        "systolic_bp": {"mean": 120, "std": 15, "min": 80, "max": 180},
        "diastolic_bp": {"mean": 80, "std": 10, "min": 50, "max": 110},
        "temperature": {"mean": 36.5, "std": 0.5, "min": 35, "max": 39},
        "spo2": {"mean": 97, "std": 2, "min": 90, "max": 100},
    }
    
    data = []
    base_time = datetime.utcnow() - timedelta(days=n_days)
    
    for elderly_id in range(1, n_elderly + 1):
        for day in range(n_days):
            for hour in range(24):
                record = {
                    "elderly_id": f"elderly_{elderly_id:03d}",
                    "recorded_at": base_time + timedelta(days=day, hours=hour),
                }
                
                for metric in metrics:
                    config = metric_configs.get(metric, {"mean": 50, "std": 10, "min": 0, "max": 100})
                    value = np.random.normal(config["mean"], config["std"])
                    value = np.clip(value, config["min"], config["max"])
                    record[metric] = round(value, 2)
                
                data.append(record)
    
    return pd.DataFrame(data)
