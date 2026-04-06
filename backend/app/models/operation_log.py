from sqlalchemy import Column, String, ForeignKey, Text, DateTime
from .base import Base, UUIDMixin


class OperationLog(Base, UUIDMixin):
    __tablename__ = "operation_logs"

    user_id = Column(String(36), ForeignKey("users.id"))
    action = Column(String(50), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(String(36))
    detail = Column(Text)
    ip_address = Column(String(50))
    user_agent = Column(String(255))
    created_at = Column(DateTime, nullable=False)
