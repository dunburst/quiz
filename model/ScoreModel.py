from sqlalchemy import Column, String, DateTime, ForeignKey,Float
from database import Base
import uuid
from sqlalchemy.orm import relationship

class Score(Base):
    __tablename__ = 'score'
    score_id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey('student.student_id'))
    quiz_id = Column(String(36), ForeignKey('quiz.quiz_id'))
    score = Column(Float, nullable=True)
    time_start = Column(DateTime, nullable=True)
    time_end = Column(DateTime, nullable=True)
    status = Column(String)