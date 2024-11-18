from sqlalchemy import Column, String, Integer,ForeignKey
from database import Base
import uuid
from datetime import datetime
from sqlalchemy.orm import relationship

class Distribution(Base):
    __tablename__ = "distribution"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    class_id = Column(Integer, ForeignKey('class.class_id'), nullable=False)
    teacher_id = Column(String(36), ForeignKey('teacher.teacher_id'), nullable=False)