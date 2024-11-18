from sqlalchemy import Column, Integer,VARCHAR
from database import Base
import uuid
from sqlalchemy.orm import relationship

class Grades(Base):
    __tablename__ = "grades"
    id_grades = Column(Integer, primary_key=True, autoincrement=True)
    name_grades = Column(VARCHAR(255), nullable=False)