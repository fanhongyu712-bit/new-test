from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AlertRuleBase(BaseModel):
    name: str
    metric_code: str
    condition_type: str
    threshold_value: Optional[float] = None
    duration_minutes: Optional[int] = None
    alert_level: str
    description: Optional[str] = None


class AlertRuleCreate(AlertRuleBase):
    pass


class AlertRuleResponse(AlertRuleBase):
    id: str
    is_active: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class AlertBase(BaseModel):
    elderly_id: str
    alert_level: str
    alert_type: str
    title: str
    content: str
    metric_value: Optional[float] = None


class AlertCreate(AlertBase):
    rule_id: Optional[str] = None


class AlertUpdate(BaseModel):
    status: Optional[str] = None
    handle_result: Optional[str] = None


class AlertResponse(AlertBase):
    id: str
    rule_id: Optional[str]
    status: str
    handler_id: Optional[str]
    handle_time: Optional[datetime]
    handle_result: Optional[str]
    created_at: datetime
    elderly_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class RiskAssessmentResponse(BaseModel):
    elderly_id: str
    risk_level: str
    risk_score: float
    risk_factors: list
    recommendations: list
    assessed_at: datetime
