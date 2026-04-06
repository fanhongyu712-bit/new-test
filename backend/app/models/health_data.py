from sqlalchemy import Column, String, Text, Numeric, DateTime, ForeignKey
from .base import Base, UUIDMixin, TimestampMixin


class HealthMetric(Base, UUIDMixin):
    __tablename__ = "health_metrics"

    name = Column(String(50), nullable=False)
    code = Column(String(30), unique=True, nullable=False)
    unit = Column(String(20))
    normal_min = Column(Numeric(10, 2))
    normal_max = Column(Numeric(10, 2))
    warning_min = Column(Numeric(10, 2))
    warning_max = Column(Numeric(10, 2))
    description = Column(Text)
    category = Column(String(50))


class Device(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "devices"

    device_code = Column(String(50), unique=True, nullable=False)
    device_name = Column(String(100), nullable=False)
    device_type = Column(String(50), nullable=False)
    manufacturer = Column(String(100))
    model = Column(String(50))
    status = Column(String(20), default="active")
    elderly_id = Column(String(36), ForeignKey("elderly_info.id"))
    last_data_at = Column(DateTime)
