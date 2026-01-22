"""
User model for NetPilot AI.
Future Enhancements:
- Password hashing
- Role-based access control
- API token support
"""

from sqlalchemy import Column, String
from app.db.base import Base
from app.models.base_model import BaseModel

class User(Base, BaseModel):
    __tablename__ = "users"

    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
