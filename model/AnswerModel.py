from sqlalchemy import Column, String, Boolean, ForeignKey,Text
from database import Base
import uuid
from datetime import datetime
from sqlalchemy.orm import relationship

class Answer(Base):
    __tablename__ = 'answer'
    answer_id = Column(String(36),primary_key=True, default=lambda: str(uuid.uuid4()))
    question_id = Column(String(36), ForeignKey('questions.question_id'))
    answer = Column(Text)
    is_correct = Column(Boolean, default=True)