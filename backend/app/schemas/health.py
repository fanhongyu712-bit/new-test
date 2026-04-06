from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class HealthMetricBase(BaseModel):
    name: str
    code: str
    unit: Optional[str] = None
    normal_min: Optional[float] = None
    normal_max: Optional[float] = None
    warning_min: Optional[float] = None
    warning_max: Optional[float] = None
    description: Optional[str] = None
    category: Optional[str] = None


class HealthMetricResponse(HealthMetricBase):
    id: str
    
    class Config:
        from_attributes = True


class DeviceBase(BaseModel):
    device_code: str
    device_name: str
    device_type: str
    manufacturer: Optional[str] = None
    model: Optional[str] = None


class DeviceCreate(DeviceBase):
    elderly_id: Optional[str] = None


class DeviceResponse(DeviceBase):
    id: str
    status: str
    elderly_id: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class HealthDataCreate(BaseModel):
    elderly_id: str
    device_id: Optional[str] = None
    metric_code: str
    value: float


class HealthTrendResponse(BaseModel):
    metric_code: str
    metric_name: str
    unit: Optional[str]
    data: list
    statistics: dict
