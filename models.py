# models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import pytz

Base = declarative_base()

# ====================
# LEAD MODEL (Updated)
# ====================
class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)
    status = Column(String, default="new")  # new, warm, hot, human_needed
    score = Column(Float, default=0.0)
    category = Column(String, nullable=True)  # e.g., "Undergrad", "MBA", "Test Prep"
    chat_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC))
    last_message = Column(Text, nullable=True)


# ====================
# API LOG MODEL (NEW)
# ====================
class APILog(Base):
    __tablename__ = "api_logs"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, index=True)
    message_type = Column(String)  # 'received', 'replied', 'unanswered', 'llm_analysis'
    llm_prompt = Column(Text, nullable=True)
    llm_response = Column(Text, nullable=True)
    api_success = Column(Boolean, default=True)
    api_error = Column(String, nullable=True)
    response_time_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC))