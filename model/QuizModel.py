from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from database import Base
import uuid
from sqlalchemy.orm import relationship

class Quiz(Base):
    __tablename__ = 'quiz'
    quiz_id = Column(String(36),primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String)
    due_date = Column(DateTime)
    time_limit = Column(Integer)
    question_count = Column(Integer)
    teacher_id = Column(String(36), ForeignKey('teacher.teacher_id'))