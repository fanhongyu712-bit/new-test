from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import random

from app.db import get_db
from app.models import ElderlyInfo, HealthMetric
from app.schemas.common import ResponseBase
from app.ml_service import ml_service

router = APIRouter()


@router.get("/health-risk/{elderly_id}", response_model=ResponseBase)
async def predict_health_risk(
    elderly_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ElderlyInfo).where(ElderlyInfo.id == elderly_id))
    elderly = result.scalar_one_or_none()
    
    if not elderly:
        return ResponseBase(code=404, message="老人信息不存在")
    
    health_data = {
        "elderly_id": elderly_id,
        "heart_rate": random.uniform(60, 130),
        "systolic_bp": random.uniform(90, 185),
        "diastolic_bp": random.uniform(60, 100),
        "temperature": random.uniform(36.0, 38.5),
        "spo2": random.uniform(91, 99),
        "blood_glucose_fasting": random.uniform(4.0, 11.0),
        "steps": random.randint(1000, 8000),
        "sleep_duration": random.uniform(5, 9),
        "room_temperature": random.uniform(20, 28),
        "room_humidity": random.uniform(40, 70),
    }
    
    risk_result = ml_service.predict_health_risk(health_data)
    
    return ResponseBase(data=risk_result)


@router.get("/anomaly-detection/{elderly_id}", response_model=ResponseBase)
async def detect_anomaly(
    elderly_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ElderlyInfo).where(ElderlyInfo.id == elderly_id))
    elderly = result.scalar_one_or_none()
    
    if not elderly:
        return ResponseBase(code=404, message="老人信息不存在")
    
    health_data = {
        "elderly_id": elderly_id,
        "heart_rate": random.uniform(60, 140),
        "systolic_bp": random.uniform(80, 190),
        "diastolic_bp": random.uniform(50, 110),
        "temperature": random.uniform(35.5, 39.5),
        "spo2": random.uniform(88, 99),
        "blood_glucose_fasting": random.uniform(3.5, 12.0),
        "steps": random.randint(500, 10000),
        "sleep_duration": random.uniform(4, 10),
        "room_temperature": random.uniform(18, 32),
        "room_humidity": random.uniform(30, 80),
    }
    
    anomaly_result = ml_service.detect_anomaly(health_data)
    
    return ResponseBase(data=anomaly_result)


@router.get("/trend-prediction/{elderly_id}", response_model=ResponseBase)
async def predict_trend(
    elderly_id: str,
    metric: str = Query("heart_rate", description="指标类型: heart_rate, systolic_bp, diastolic_bp, temperature, spo2"),
    days: int = Query(7, ge=1, le=14, description="预测天数"),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ElderlyInfo).where(ElderlyInfo.id == elderly_id))
    elderly = result.scalar_one_or_none()
    
    if not elderly:
        return ResponseBase(code=404, message="老人信息不存在")
    
    base_values = {
        "heart_rate": 75,
        "systolic_bp": 120,
        "diastolic_bp": 80,
        "temperature": 36.5,
        "spo2": 97,
    }
    
    historical_data = []
    for i in range(10, 0, -1):
        data_point = {"date": (datetime.utcnow() - timedelta(days=i)).isoformat()}
        for m, base in base_values.items():
            data_point[m] = base + random.uniform(-10, 10)
        historical_data.append(data_point)
    
    trend_result = ml_service.predict_trend(historical_data, metric)
    
    return ResponseBase(data=trend_result)


@router.get("/batch-risk-assessment", response_model=ResponseBase)
async def batch_risk_assessment(
    institution_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(ElderlyInfo).where(ElderlyInfo.status == "active")
    if institution_id:
        query = query.where(ElderlyInfo.institution_id == institution_id)
    
    result = await db.execute(query.limit(50))
    elderly_list = result.scalars().all()
    
    assessments = []
    for elderly in elderly_list:
        health_data = {
            "elderly_id": elderly.id,
            "heart_rate": random.uniform(55, 135),
            "systolic_bp": random.uniform(85, 190),
            "diastolic_bp": random.uniform(55, 105),
            "temperature": random.uniform(35.8, 38.8),
            "spo2": random.uniform(89, 99),
            "blood_glucose_fasting": random.uniform(3.8, 12.0),
            "steps": random.randint(500, 10000),
            "sleep_duration": random.uniform(4.5, 9.5),
            "room_temperature": random.uniform(19, 30),
            "room_humidity": random.uniform(35, 75),
        }
        
        risk_result = ml_service.predict_health_risk(health_data)
        assessments.append({
            "elderly_id": elderly.id,
            "elderly_name": elderly.name,
            "room_number": elderly.room_number,
            **risk_result
        })
    
    risk_distribution = {
        "low": len([a for a in assessments if a["risk_level"] == "low"]),
        "medium": len([a for a in assessments if a["risk_level"] == "medium"]),
        "high": len([a for a in assessments if a["risk_level"] == "high"]),
        "critical": len([a for a in assessments if a["risk_level"] == "critical"]),
    }
    
    return ResponseBase(data={
        "total_assessed": len(assessments),
        "risk_distribution": risk_distribution,
        "assessments": assessments,
    })


@router.get("/model-info", response_model=ResponseBase)
async def get_model_info():
    return ResponseBase(data={
        "models": [
            {
                "name": "HealthRiskModel",
                "type": "risk_prediction",
                "architecture": "LSTM + Multi-Head Attention",
                "description": "健康风险预测模型，基于LSTM和注意力机制预测老人健康风险等级",
                "input_features": 10,
                "output_classes": 4,
                "risk_levels": ["low", "medium", "high", "critical"]
            },
            {
                "name": "AnomalyDetectionModel",
                "type": "anomaly_detection",
                "architecture": "Autoencoder",
                "description": "基于自编码器的异常检测模型，用于检测健康数据中的异常模式",
                "input_features": 10,
                "latent_dim": 16
            },
            {
                "name": "HealthTrendPredictor",
                "type": "trend_prediction",
                "architecture": "Bidirectional LSTM Encoder-Decoder",
                "description": "基于编码器-解码器架构的健康趋势预测模型",
                "input_features": 5,
                "forecast_horizon": 7
            }
        ],
        "ml_technologies": [
            "PyTorch深度学习框架",
            "LSTM长短期记忆网络",
            "Multi-Head Attention注意力机制",
            "Autoencoder自编码器",
            "Bidirectional LSTM双向编码"
        ]
    })
