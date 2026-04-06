from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class ElderlyBase(BaseModel):
    name: str
    gender: str
    birth_date: date
    id_card: Optional[str] = None
    blood_type: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    room_number: Optional[str] = None
    bed_number: Optional[str] = None
    admission_date: Optional[date] = None


class ElderlyCreate(ElderlyBase):
    institution_id: str
    nurse_id: Optional[str] = None
    allergies: Optional[str] = None
    chronic_diseases: Optional[str] = None
    medications: Optional[str] = None


class ElderlyUpdate(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    blood_type: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    room_number: Optional[str] = None
    bed_number: Optional[str] = None
    nurse_id: Optional[str] = None
    status: Optional[str] = None


class ElderlyResponse(ElderlyBase):
    id: str
    institution_id: Optional[str]
    nurse_id: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class HealthRecordBase(BaseModel):
    record_date: date
    health_status: Optional[str] = None
    nursing_level: Optional[str] = None
    special_care: Optional[str] = None


class HealthRecordCreate(HealthRecordBase):
    elderly_id: str


class HealthRecordResponse(HealthRecordBase):
    id: str
    elderly_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True
