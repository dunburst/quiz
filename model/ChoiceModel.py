from sqlalchemy import Column, String, ForeignKey
from database import Base
import uuid
from datetime import datetime
from sqlalchemy.orm import relationship

class Choice(Base):
    __tablename__ = 'choice'
    choice_id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    answer_id = Column(String(36), ForeignKey('answer.answer_id'), nullable=True)
    student_id = Column(String(36), ForeignKey('student.student_id'))