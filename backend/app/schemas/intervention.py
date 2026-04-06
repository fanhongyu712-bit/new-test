from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class InterventionPlanBase(BaseModel):
    name: str
    alert_type: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[str] = None


class InterventionPlanCreate(InterventionPlanBase):
    is_template: Optional[str] = "false"


class InterventionPlanResponse(InterventionPlanBase):
    id: str
    created_by: Optional[str]
    is_template: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class InterventionRecordBase(BaseModel):
    elderly_id: str
    alert_id: Optional[str] = None
    plan_id: Optional[str] = None
    start_time: datetime
    content: Optional[str] = None


class InterventionRecordCreate(InterventionRecordBase):
    pass


class InterventionRecordUpdate(BaseModel):
    end_time: Optional[datetime] = None
    status: Optional[str] = None
    result: Optional[str] = None
    effectiveness: Optional[str] = None


class InterventionRecordResponse(InterventionRecordBase):
    id: str
    executor_id: str
    end_time: Optional[datetime]
    status: str
    result: Optional[str]
    effectiveness: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
