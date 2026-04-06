from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer
from .base import Base, TimestampMixin, UUIDMixin


class Institution(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "institutions"

    name = Column(String(100), nullable=False)
    address = Column(String(255))
    contact_phone = Column(String(20))
    contact_email = Column(String(100))
    description = Column(Text)
    capacity = Column(Integer)
    status = Column(String(20), default="active")


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True)
    phone = Column(String(20))
    real_name = Column(String(50))
    role = Column(String(20), nullable=False)
    status = Column(String(20), default="active")
    institution_id = Column(String(36), ForeignKey("institutions.id"))
    last_login_at = Column(DateTime)
