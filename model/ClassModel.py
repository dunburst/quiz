from sqlalchemy import Column, String, Integer, ForeignKey, VARCHAR
from database import Base
import uuid
from datetime import datetime
from sqlalchemy.orm import relationship

class Class(Base):
    __tablename__ = "class"
    class_id = Column(Integer, primary_key=True, autoincrement=True)
    name_class = Column(VARCHAR(255), nullable=False)
    years = Column(String(36))
    total_student = Column(Integer)
    id_grades = Column(Integer, ForeignKey('grades.id_grades'), nullable=False)