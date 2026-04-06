import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class HealthRiskModel(nn.Module):
    def __init__(
        self,
        input_size: int,
        hidden_size: int = 128,
        num_layers: int = 2,
        num_classes: int = 4,
        dropout: float = 0.3,
    ):
        super().__init__()
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=True,
        )
        
        self.attention = nn.MultiheadAttention(
            embed_dim=hidden_size * 2,
            num_heads=4,
            dropout=dropout,
            batch_first=True,
        )
        
        self.fc1 = nn.Linear(hidden_size * 2, hidden_size)
        self.bn1 = nn.BatchNorm1d(hidden_size)
        self.dropout1 = nn.Dropout(dropout)
        
        self.fc2 = nn.Linear(hidden_size, hidden_size // 2)
        self.bn2 = nn.BatchNorm1d(hidden_size // 2)
        self.dropout2 = nn.Dropout(dropout)
        
        self.fc3 = nn.Linear(hidden_size // 2, num_classes)
        
        self.relu = nn.ReLU()
        
    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        lstm_out, _ = self.lstm(x)
        
        attn_out, _ = self.attention(lstm_out, lstm_out, lstm_out, key_padding_mask=mask)
        
        pooled = torch.mean(attn_out, dim=1)
        
        out = self.fc1(pooled)
        out = self.bn1(out)
        out = self.relu(out)
        out = self.dropout1(out)
        
        out = self.fc2(out)
        out = self.bn2(out)
        out = self.relu(out)
        out = self.dropout2(out)
        
        out = self.fc3(out)
        
        return out


class AnomalyDetectionModel(nn.Module):
    def __init__(
        self,
        input_size: int,
        hidden_size: int = 64,
        latent_size: int = 32,
        num_layers: int = 2,
    ):
        super().__init__()
        
        self.encoder = nn.ModuleList()
        current_size = input_size
        for i in range(num_layers):
            self.encoder.append(nn.Linear(current_size, hidden_size))
            self.encoder.append(nn.ReLU())
            self.encoder.append(nn.BatchNorm1d(hidden_size))
            current_size = hidden_size
            hidden_size = hidden_size // 2
        
        self.latent = nn.Linear(current_size, latent_size)
        
        hidden_size = latent_size * 2
        self.decoder = nn.ModuleList()
        for i in range(num_layers):
            self.decoder.append(nn.Linear(hidden_size, hidden_size * 2))
            self.decoder.append(nn.ReLU())
            self.decoder.append(nn.BatchNorm1d(hidden_size * 2))
            hidden_size = hidden_size * 2
        
        self.output = nn.Linear(hidden_size, input_size)
        
    def encode(self, x: torch.Tensor) -> torch.Tensor:
        for layer in self.encoder:
            x = layer(x)
        return self.latent(x)
    
    def decode(self, z: torch.Tensor) -> torch.Tensor:
        for layer in self.decoder:
            z = layer(z)
        return self.output(z)
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        z = self.encode(x)
        x_recon = self.decode(z)
        return x_recon, z
    
    def get_anomaly_score(self, x: torch.Tensor) -> torch.Tensor:
        x_recon, _ = self.forward(x)
        return torch.mean((x - x_recon) ** 2, dim=1)


class HealthTrendPredictor(nn.Module):
    def __init__(
        self,
        input_size: int,
        hidden_size: int = 64,
        num_layers: int = 2,
        forecast_horizon: int = 7,
    ):
        super().__init__()
        
        self.encoder = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
        )
        
        self.decoder = nn.LSTM(
            input_size=hidden_size * 2,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
        )
        
        self.fc = nn.Linear(hidden_size, input_size)
        self.forecast_horizon = forecast_horizon
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        _, (h, c) = self.encoder(x)
        
        decoder_input = torch.zeros(x.size(0), self.forecast_horizon, h.size(2) * 2, device=x.device)
        decoder_input[:, 0, :] = torch.cat([h[-2], h[-1]], dim=1)
        
        decoder_output, _ = self.decoder(decoder_input, (h[-1].unsqueeze(0), c[-1].unsqueeze(0)))
        
        predictions = self.fc(decoder_output)
        
        return predictions


class FallDetectionModel(nn.Module):
    def __init__(
        self,
        input_size: int = 6,
        hidden_size: int = 128,
        num_layers: int = 2,
        num_classes: int = 2,
    ):
        super().__init__()
        
        self.conv1 = nn.Conv1d(input_size, 64, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm1d(64)
        self.relu = nn.ReLU()
        self.pool = nn.MaxPool1d(2)
        
        self.conv2 = nn.Conv1d(64, 128, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm1d(128)
        
        self.lstm = nn.LSTM(
            input_size=128,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
        )
        
        self.fc = nn.Sequential(
            nn.Linear(hidden_size * 2, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, num_classes),
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x.permute(0, 2, 1)
        
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.pool(x)
        
        x = self.conv2(x)
        x = self.bn2(x)
        x = self.relu(x)
        
        x = x.permute(0, 2, 1)
        
        lstm_out, _ = self.lstm(x)
        
        out = lstm_out[:, -1, :]
        out = self.fc(out)
        
        return out
