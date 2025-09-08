from sqlalchemy import Column, Integer, String, DateTime, func
from pathlib import Path
import sys

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
sys.path.append(str(project_root))

from app.core.database import Base

class Setting(Base):
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, index=True)
    setting_name = Column(String(255), unique=True, nullable=False, index=True)
    setting_value = Column(String(1000), nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
