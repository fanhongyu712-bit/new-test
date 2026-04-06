from sqlalchemy import Column, String, Date, ForeignKey, Text, Numeric
from .base import Base, TimestampMixin, UUIDMixin


class ElderlyInfo(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "elderly_info"

    name = Column(String(50), nullable=False)
    gender = Column(String(10), nullable=False)
    birth_date = Column(Date, nullable=False)
    id_card = Column(String(18), unique=True)
    blood_type = Column(String(5))
    height = Column(Numeric(5, 2))
    weight = Column(Numeric(5, 2))
    allergies = Column(Text)
    chronic_diseases = Column(Text)
    medications = Column(Text)
    emergency_contact = Column(Text)
    room_number = Column(String(20))
    bed_number = Column(String(20))
    admission_date = Column(Date)
    institution_id = Column(String(36), ForeignKey("institutions.id"))
    nurse_id = Column(String(36), ForeignKey("users.id"))
    status = Column(String(20), default="active")


class HealthRecord(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "health_records"

    elderly_id = Column(String(36), ForeignKey("elderly_info.id"), nullable=False)
    record_date = Column(Date, nullable=False)
    health_status = Column(Text)
    nursing_level = Column(String(20))
    special_care = Column(Text)
