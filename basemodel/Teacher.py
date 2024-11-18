from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Union
from pydantic import BaseModel
from datetime import datetime

class TeacherResponse(BaseModel):
    teacher_id: str
    mateacher: str
    gender: str
    name: str
    birth_date: datetime
    email: str
    phone_number: Optional[str]
    image: Optional[str]
    subject: str  # New field for subject name
    classes: List[Dict[str, Union[str, int]]]  # Allow class_id to be str or int
    
class TeacherUpdateRequest(BaseModel):
    mateacher: Optional[str] = None
    gender: Optional[str] = None
    name: Optional[str] = None
    birth_date: Optional[datetime] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    image: Optional[str] = None
    subject_id: Optional[int] = None
    
class TeacherCreate(BaseModel):
    mateacher: str
    name: str
    gender: str
    birth_date: datetime
    email: str
    phone_number: Optional[str]
    subject_id: int
    password: str
    class_ids: List[int]  
    
class TeacherUpdate(BaseModel):
    teacher_id: str
    name: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[datetime] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    subject_id: Optional[int] = None
    password: Optional[str] = None
    class_ids: Optional[List[int]] = None  