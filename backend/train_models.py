import asyncio
import argparse
from pathlib import Path
from datetime import datetime
import json

import torch
import numpy as np

from app.ml.preprocessing import (
    HealthDataPreprocessor,
    create_dataloaders,
    generate_synthetic_data,
)
from app.ml.training import RiskModelTrainer, AnomalyDetectorTrainer, TrendPredictorTrainer
from app.ml.models import HealthRiskModel, AnomalyDetectionModel, HealthTrendPredictor


def train_risk_model(
    data_path: str = None,
    output_dir: str = "./models",
    epochs: int = 50,
    batch_size: int = 32,
    learning_rate: float = 0.001,
):
    print("=" * 50)
    print("Training Health Risk Assessment Model")
    print("=" * 50)
    
    if data_path:
        import pandas as pd
        data = pd.read_csv(data_path)
    else:
        print("Generating synthetic data for training...")
        data = generate_synthetic_data(n_elderly=100, n_days=60)
    
    metric_columns = ["heart_rate", "systolic_bp", "diastolic_bp", "temperature", "spo2"]
    
    preprocessor = HealthDataPreprocessor(sequence_length=24)
    data_scaled = preprocessor.fit_transform(data, metric_columns)
    
    sequences, labels, elderly_ids = preprocessor.create_sequences(
        data_scaled, metric_columns
    )
    
    risk_labels = np.random.randint(0, 4, size=len(sequences))
    
    n_samples = len(sequences)
    n_train = int(n_samples * 0.7)
    n_val = int(n_samples * 0.15)
    
    indices = np.random.permutation(n_samples)
    train_idx = indices[:n_train]
    val_idx = indices[n_train:n_train + n_val]
    test_idx = indices[n_train + n_val:]
    
    from torch.utils.data import DataLoader, TensorDataset
    
    train_dataset = TensorDataset(
        torch.FloatTensor(sequences[train_idx]),
        torch.LongTensor(risk_labels[train_idx]),
    )
    val_dataset = TensorDataset(
        torch.FloatTensor(sequences[val_idx]),
        torch.LongTensor(risk_labels[val_idx]),
    )
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    input_size = sequences.shape[2]
    trainer = RiskModelTrainer(input_size=input_size, learning_rate=learning_rate)
    
    history = trainer.train(
        train_loader=train_loader,
        val_loader=val_loader,
        epochs=epochs,
        early_stopping_patience=10,
    )
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    model_name = f"risk_model_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    trainer.save_model(
        str(output_path / f"{model_name}.pt"),
        metadata={
            "model_type": "risk",
            "input_size": input_size,
            "metric_columns": metric_columns,
            "feature_order": metric_columns,
            "training_date": datetime.utcnow().isoformat(),
            "model_config": {
                "input_size": input_size,
                "hidden_size": 128,
                "num_layers": 2,
                "num_classes": 4,
            },
        },
    )
    
    with open(output_path / f"{model_name}_history.json", "w") as f:
        json.dump(history, f, indent=2)
    
    print(f"\nModel saved to {output_path / model_name}")
    print(f"Final training loss: {history['train_loss'][-1]:.4f}")
    print(f"Final validation loss: {history['val_loss'][-1]:.4f}")
    
    return history


def train_anomaly_model(
    data_path: str = None,
    output_dir: str = "./models",
    epochs: int = 50,
    batch_size: int = 32,
    learning_rate: float = 0.001,
):
    print("=" * 50)
    print("Training Anomaly Detection Model")
    print("=" * 50)
    
    if data_path:
        import pandas as pd
        data = pd.read_csv(data_path)
    else:
        print("Generating synthetic data for training...")
        data = generate_synthetic_data(n_elderly=100, n_days=60)
    
    metric_columns = ["heart_rate", "systolic_bp", "diastolic_bp", "temperature", "spo2"]
    
    preprocessor = HealthDataPreprocessor()
    data_scaled = preprocessor.fit_transform(data, metric_columns)
    
    sequences, _, _ = preprocessor.create_sequences(data_scaled, metric_columns)
    
    n_samples = len(sequences)
    n_train = int(n_samples * 0.7)
    n_val = int(n_samples * 0.15)
    
    indices = np.random.permutation(n_samples)
    train_idx = indices[:n_train]
    val_idx = indices[n_train:n_train + n_val]
    
    from torch.utils.data import DataLoader, TensorDataset
    
    train_dataset = TensorDataset(
        torch.FloatTensor(sequences[train_idx]),
        torch.FloatTensor(sequences[train_idx]),
    )
    val_dataset = TensorDataset(
        torch.FloatTensor(sequences[val_idx]),
        torch.FloatTensor(sequences[val_idx]),
    )
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    input_size = sequences.shape[2]
    trainer = AnomalyDetectorTrainer(input_size=input_size, learning_rate=learning_rate)
    
    history = trainer.train(
        train_loader=train_loader,
        val_loader=val_loader,
        epochs=epochs,
        early_stopping_patience=10,
    )
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    model_name = f"anomaly_model_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    trainer.save_model(
        str(output_path / f"{model_name}.pt"),
        metadata={
            "model_type": "anomaly",
            "input_size": input_size,
            "metric_columns": metric_columns,
            "feature_order": metric_columns,
            "anomaly_threshold": 0.1,
            "training_date": datetime.utcnow().isoformat(),
            "model_config": {
                "input_size": input_size,
                "hidden_size": 64,
                "latent_size": 32,
            },
        },
    )
    
    print(f"\nModel saved to {output_path / model_name}")
    print(f"Final training loss: {history['train_loss'][-1]:.4f}")
    
    return history


def train_trend_model(
    data_path: str = None,
    output_dir: str = "./models",
    epochs: int = 50,
    batch_size: int = 32,
    learning_rate: float = 0.001,
    forecast_horizon: int = 7,
):
    print("=" * 50)
    print("Training Health Trend Prediction Model")
    print("=" * 50)
    
    if data_path:
        import pandas as pd
        data = pd.read_csv(data_path)
    else:
        print("Generating synthetic data for training...")
        data = generate_synthetic_data(n_elderly=100, n_days=60)
    
    metric_columns = ["heart_rate", "systolic_bp", "diastolic_bp", "temperature", "spo2"]
    
    preprocessor = HealthDataPreprocessor(
        sequence_length=24,
        forecast_horizon=forecast_horizon,
    )
    data_scaled = preprocessor.fit_transform(data, metric_columns)
    
    sequences, labels, _ = preprocessor.create_sequences(data_scaled, metric_columns)
    
    n_samples = len(sequences)
    n_train = int(n_samples * 0.7)
    n_val = int(n_samples * 0.15)
    
    indices = np.random.permutation(n_samples)
    train_idx = indices[:n_train]
    val_idx = indices[n_train:n_train + n_val]
    
    from torch.utils.data import DataLoader, TensorDataset
    
    train_dataset = TensorDataset(
        torch.FloatTensor(sequences[train_idx]),
        torch.FloatTensor(labels[train_idx]),
    )
    val_dataset = TensorDataset(
        torch.FloatTensor(sequences[val_idx]),
        torch.FloatTensor(labels[val_idx]),
    )
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    input_size = sequences.shape[2]
    trainer = TrendPredictorTrainer(
        input_size=input_size,
        forecast_horizon=forecast_horizon,
        learning_rate=learning_rate,
    )
    
    history = trainer.train(
        train_loader=train_loader,
        val_loader=val_loader,
        epochs=epochs,
        early_stopping_patience=10,
    )
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    model_name = f"trend_model_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    trainer.save_model(
        str(output_path / f"{model_name}.pt"),
        metadata={
            "model_type": "trend",
            "input_size": input_size,
            "forecast_horizon": forecast_horizon,
            "metric_columns": metric_columns,
            "feature_order": metric_columns,
            "training_date": datetime.utcnow().isoformat(),
            "model_config": {
                "input_size": input_size,
                "hidden_size": 64,
                "forecast_horizon": forecast_horizon,
            },
        },
    )
    
    print(f"\nModel saved to {output_path / model_name}")
    print(f"Final training loss: {history['train_loss'][-1]:.4f}")
    
    return history


def main():
    parser = argparse.ArgumentParser(description="Train health monitoring models")
    parser.add_argument(
        "--model",
        type=str,
        choices=["risk", "anomaly", "trend", "all"],
        default="all",
        help="Model type to train",
    )
    parser.add_argument(
        "--data",
        type=str,
        default=None,
        help="Path to training data CSV file",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="./models",
        help="Output directory for trained models",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=50,
        help="Number of training epochs",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Training batch size",
    )
    parser.add_argument(
        "--lr",
        type=float,
        default=0.001,
        help="Learning rate",
    )
    
    args = parser.parse_args()
    
    if args.model in ["risk", "all"]:
        train_risk_model(
            data_path=args.data,
            output_dir=args.output,
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.lr,
        )
    
    if args.model in ["anomaly", "all"]:
        train_anomaly_model(
            data_path=args.data,
            output_dir=args.output,
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.lr,
        )
    
    if args.model in ["trend", "all"]:
        train_trend_model(
            data_path=args.data,
            output_dir=args.output,
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.lr,
        )
    
    print("\n" + "=" * 50)
    print("Training completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    main()
