from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

# Lấy thông tin học sinh
class StudentResponse(BaseModel):
    student_id: str
    mastudent: str
    gender: str
    name: str
    birth_date: datetime
    email: str
    phone_number: str
    image: str
    class_id: int
    name_class: str  # New field for class name
    first_login: bool

class StudentCreate(BaseModel):
    mastudent: str
    name: str
    gender: str
    birth_date: datetime
    email: str
    phone_number: str
    class_id: int
    password: str

class StudentUpdate(BaseModel):
    student_id: str
    mastudent : Optional[str] = None
    name: str = None
    gender: str = None
    birth_date: datetime = None
    email: str = None
    phone_number: str = None
    class_id: int = None
    password: str = None

class QuizResponse(BaseModel):
    quiz_id: str  
    title: str
    due_date: datetime  
    time_limit: int
    question_count: int
    status: str
    score: Optional[float]  # Có thể là None nếu chưa có điểm
    teacher_id: str  # Thay đổi theo kiểu dữ liệu thực tế nếu cần
class SubjectQuizzesResponse(BaseModel):
    subject_id: int
    subject_name: str
    quizzes: List[QuizResponse]

class StudentScoreResponse(BaseModel):
    student_id: str
    student_name: str
    scores: dict  # Dạng {quiz_title: score}