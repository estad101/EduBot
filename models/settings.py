"""
Settings model - stores application configuration.
"""
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.types import Integer
from datetime import datetime
from config.database import Base


class AdminSetting(Base):
    """
    Admin Settings model - stores configuration key-value pairs.
    
    Fields:
        id: Primary key
        key: Setting key (unique)
        value: Setting value (stored as text for flexibility)
        description: Description of the setting
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "admin_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=True)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<AdminSetting(key='{self.key}', value='{self.value[:50]}...')>"
