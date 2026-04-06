from sqlalchemy import Column, String, ForeignKey, Text, Numeric, Integer, DateTime
from sqlalchemy.orm import relationship
from .base import Base, UUIDMixin, TimestampMixin


class AlertRule(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "alert_rules"

    name = Column(String(100), nullable=False)
    metric_code = Column(String(30), nullable=False)
    condition_type = Column(String(20), nullable=False)
    threshold_value = Column(Numeric(10, 2))
    duration_minutes = Column(Integer)
    alert_level = Column(String(20), nullable=False)
    description = Column(Text)
    is_active = Column(String(10), default="true")


class Alert(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "alerts"

    elderly_id = Column(String(36), ForeignKey("elderly_info.id"), nullable=False)
    rule_id = Column(String(36), ForeignKey("alert_rules.id"))
    alert_level = Column(String(20), nullable=False)
    alert_type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    metric_value = Column(Numeric(10, 2))
    status = Column(String(20), default="pending")
    handler_id = Column(String(36), ForeignKey("users.id"))
    handle_time = Column(DateTime)
    handle_result = Column(Text)
    
    elderly = relationship("ElderlyInfo", foreign_keys=[elderly_id])
    rule = relationship("AlertRule", foreign_keys=[rule_id])
