from datetime import datetime, date
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, func, ForeignKey
from backend.app.db.database import Base

class User(Base):
    """SQLAlchemy ORM model for application users."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}')>"

class Application(Base):
    """SQLAlchemy ORM model for tracked job applications."""

    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company = Column(String(200), nullable=False, index=True)
    job_title = Column(String(200), nullable=False, index=True)
    job_description = Column(Text, nullable=True)
    application_date = Column(Date, nullable=True, default=date.today)
    status = Column(String(50), nullable=False, default="saved", index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    interview_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<Application(id={self.id}, company='{self.company}', job_title='{self.job_title}', status='{self.status}')>"
