from sqlalchemy import Column, String, ForeignKey,Text
from database import Base
import uuid
from sqlalchemy.orm import relationship

class Questions(Base):
    __tablename__ = 'questions'
    question_id = Column(String(36),primary_key=True, default=lambda: str(uuid.uuid4()))
    quiz_id = Column(String(36), ForeignKey('quiz.quiz_id'))
    question_text= Column(Text, nullable=False)