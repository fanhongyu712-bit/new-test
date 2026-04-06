from sqlalchemy import Column, String, ForeignKey, Text, DateTime
from .base import Base, UUIDMixin, TimestampMixin


class InterventionPlan(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "intervention_plans"

    name = Column(String(100), nullable=False)
    alert_type = Column(String(50))
    description = Column(Text)
    steps = Column(Text)
    created_by = Column(String(36), ForeignKey("users.id"))
    is_template = Column(String(10), default="false")


class InterventionRecord(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "intervention_records"

    elderly_id = Column(String(36), ForeignKey("elderly_info.id"), nullable=False)
    alert_id = Column(String(36), ForeignKey("alerts.id"))
    plan_id = Column(String(36), ForeignKey("intervention_plans.id"))
    executor_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    status = Column(String(20), default="ongoing")
    content = Column(Text)
    result = Column(Text)
    effectiveness = Column(String(20))
