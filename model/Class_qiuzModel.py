from sqlalchemy import Column, String, Integer, ForeignKey
from database import Base
import uuid
from datetime import datetime
from sqlalchemy.orm import relationship

class Class_quiz(Base):
     __tablename__ = 'class_quiz'
     class_quiz_id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
     class_id = Column(Integer, ForeignKey('class.class_id'))   
     quiz_id = Column(String(36), ForeignKey('quiz.quiz_id'))