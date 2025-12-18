"""
Base model definitions for NetPilot AI.

This file contains:
1. SQLAlchemy BaseModel mixin used for ORM database tables.
2. Pydantic models used for FastAPI request validation.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import declarative_mixin

from pydantic import BaseModel as PydanticBaseModel


# ---------------------------------------------------------------------------
# SQLAlchemy ORM Base Mixin
# ---------------------------------------------------------------------------
@declarative_mixin
class BaseModel:
    """Common SQLAlchemy columns for all database models."""

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ---------------------------------------------------------------------------
# Pydantic Request Models
# ---------------------------------------------------------------------------
class VPCDeleteRequest(PydanticBaseModel):
    """Body model for deleting a VPC."""

    vpc_id: str
