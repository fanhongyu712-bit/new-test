from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random

from ..models import Alert, AlertRule, ElderlyInfo, HealthMetric
from ..schemas.alert import RiskAssessmentResponse


class AlertService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def assess_risk(self, elderly_id: UUID) -> RiskAssessmentResponse:
        result = await self.db.execute(select(ElderlyInfo).where(ElderlyInfo.id == elderly_id))
        elderly = result.scalar_one_or_none()
        
        if not elderly:
            raise ValueError("老人信息不存在")
        
        risk_factors = []
        risk_score = 0.0
        
        result = await self.db.execute(select(HealthMetric))
        metrics = result.scalars().all()
        
        metric_values = {}
        for metric in metrics:
            base_value = float(metric.normal_min + metric.normal_max) / 2 if metric.normal_min and metric.normal_max else 50
            value = base_value + random.uniform(-15, 15)
            metric_values[metric.code] = {
                "value": value,
                "metric": metric,
            }
        
        for code, data in metric_values.items():
            metric = data["metric"]
            value = data["value"]
            
            if metric.warning_max and value > float(metric.warning_max):
                risk_factors.append({
                    "type": "metric_high",
                    "metric": metric.name,
                    "value": round(value, 2),
                    "threshold": float(metric.warning_max),
                    "severity": "high",
                })
                risk_score += 25
            elif metric.normal_max and value > float(metric.normal_max):
                risk_factors.append({
                    "type": "metric_high",
                    "metric": metric.name,
                    "value": round(value, 2),
                    "threshold": float(metric.normal_max),
                    "severity": "medium",
                })
                risk_score += 15
            
            if metric.warning_min and value < float(metric.warning_min):
                risk_factors.append({
                    "type": "metric_low",
                    "metric": metric.name,
                    "value": round(value, 2),
                    "threshold": float(metric.warning_min),
                    "severity": "high",
                })
                risk_score += 25
            elif metric.normal_min and value < float(metric.normal_min):
                risk_factors.append({
                    "type": "metric_low",
                    "metric": metric.name,
                    "value": round(value, 2),
                    "threshold": float(metric.normal_min),
                    "severity": "medium",
                })
                risk_score += 15
        
        if elderly.chronic_diseases:
            for disease in elderly.chronic_diseases:
                risk_factors.append({
                    "type": "chronic_disease",
                    "name": disease.get("name", "未知"),
                    "severity": "medium",
                })
                risk_score += 10
        
        risk_score = min(risk_score, 100)
        
        if risk_score >= 75:
            risk_level = "critical"
        elif risk_score >= 50:
            risk_level = "high"
        elif risk_score >= 25:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        recommendations = self._generate_recommendations(risk_level, risk_factors)
        
        return RiskAssessmentResponse(
            elderly_id=elderly_id,
            risk_level=risk_level,
            risk_score=risk_score,
            risk_factors=risk_factors,
            recommendations=recommendations,
            assessed_at=datetime.utcnow(),
        )
    
    def _generate_recommendations(self, risk_level: str, risk_factors: List[Dict]) -> List[str]:
        recommendations = []
        
        if risk_level == "critical":
            recommendations.append("建议立即进行健康检查")
            recommendations.append("通知责任医生进行评估")
        
        for factor in risk_factors:
            if factor["type"] == "metric_high":
                recommendations.append(f"关注{factor['metric']}偏高情况")
            elif factor["type"] == "metric_low":
                recommendations.append(f"关注{factor['metric']}偏低情况")
            elif factor["type"] == "chronic_disease":
                recommendations.append(f"定期监测{factor['name']}状况")
        
        if risk_level in ["high", "critical"]:
            recommendations.append("增加巡视频率")
            recommendations.append("准备应急预案")
        
        return list(set(recommendations))
    
    async def check_alert_rules(self, elderly_id: UUID) -> List[Alert]:
        result = await self.db.execute(
            select(AlertRule).where(AlertRule.is_active == True)
        )
        rules = result.scalars().all()
        
        alerts = []
        
        result = await self.db.execute(select(HealthMetric))
        metrics = result.scalars().all()
        metric_map = {m.code: m for m in metrics}
        
        for rule in rules:
            if random.random() < 0.1:
                metric = metric_map.get(rule.metric_code)
                if metric:
                    base_value = float(metric.normal_min + metric.normal_max) / 2 if metric.normal_min and metric.normal_max else 50
                    
                    if rule.condition_type == "gt":
                        value = float(rule.threshold_value) + random.uniform(1, 10)
                    elif rule.condition_type == "lt":
                        value = float(rule.threshold_value) - random.uniform(1, 10)
                    else:
                        value = base_value + random.uniform(-20, 20)
                    
                    alert = Alert(
                        elderly_id=elderly_id,
                        rule_id=rule.id,
                        alert_level=rule.alert_level,
                        alert_type=rule.metric_code,
                        title=f"{rule.name}预警",
                        content=f"{metric.name}异常: {round(value, 2)}",
                        metric_value=round(value, 2),
                        status="pending",
                    )
                    alerts.append(alert)
        
        return alerts
    
    def _check_condition(self, value: float, condition_type: str, threshold: float) -> bool:
        if condition_type == "gt":
            return value > threshold
        elif condition_type == "lt":
            return value < threshold
        elif condition_type == "gte":
            return value >= threshold
        elif condition_type == "lte":
            return value <= threshold
        elif condition_type == "eq":
            return value == threshold
        return False
