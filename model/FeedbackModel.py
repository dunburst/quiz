from sqlalchemy import Column, String, Integer, DateTime, ForeignKey,Text
from database import Base
import uuid
from datetime import datetime
from sqlalchemy.orm import relationship

class Feedback(Base):
    __tablename__ = 'feedback'
    feedback_id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    context = Column(Text)
    teacher_id = Column(String(36), ForeignKey('teacher.teacher_id'), nullable=True)
    student_id = Column(String(36), ForeignKey('student.student_id'), nullable=True)
    class_id = Column(Integer, ForeignKey('class.class_id'), nullable=False)  # Bắt buộc phải có lớp
    subject_id = Column(Integer, ForeignKey('subject.subject_id'), nullable=False)  # Bắt buộc phải có môn học
    is_parents = Column(Integer, default=0)  # 0 là feedback cha, 1 là feedback con
    parent_id = Column(String(36), nullable=True)  # Chỉ điền khi là feedback con
    created_at = Column(DateTime, default=lambda: datetime.now()) 