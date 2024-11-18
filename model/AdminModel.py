from sqlalchemy import Column,String,VARCHAR
from database import Base
import uuid
from datetime import datetime
from sqlalchemy.orm import relationship

class Admin(Base):
    __tablename__ = "admin"
    admin_id = Column(String(36), primary_key=True)
    password = Column(VARCHAR(255), nullable=False)