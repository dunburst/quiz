from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, VARCHAR
from database import Base
import uuid
from sqlalchemy.orm import relationship

class Teacher(Base):
    __tablename__ = "teacher"
    teacher_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    mateacher = Column(VARCHAR(255), nullable=False)
    password = Column(VARCHAR(255), nullable=False)
    gender = Column(VARCHAR(255), nullable=False)
    name = Column(VARCHAR(255), nullable=False)
    birth_date = Column(DateTime, nullable=False)
    email = Column(VARCHAR(255), nullable=False)
    phone_number = Column(VARCHAR(15))
    image = Column(VARCHAR(255))
    subject_id = Column(Integer, ForeignKey('subject.subject_id'), nullable=False)