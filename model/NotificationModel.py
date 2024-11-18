from sqlalchemy import Column, String, DateTime, ForeignKey,Text
from database import Base
import uuid
from sqlalchemy.orm import relationship

class Notification(Base):
    __tablename__ = 'notification'
    noti_id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    context = Column(Text)
    time = Column(DateTime)
    teacher_id = Column(String(36), ForeignKey('teacher.teacher_id'), nullable=True)
    student_id = Column(String(36), ForeignKey('student.student_id'), nullable=True)