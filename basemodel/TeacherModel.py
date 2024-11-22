from typing import List, Optional, Dict, Union
from pydantic import BaseModel
from datetime import datetime

#Lấy thông tin giáo viên
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


# Thêm giáo viên
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

# Update giáo viên
class TeacherUpdate(BaseModel):
    teacher_id: str
    mateacher: Optional[str] = None
    name: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[datetime] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    subject_id: Optional[int] = None
    class_ids: Optional[List[int]] = None  