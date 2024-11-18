from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import uuid
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from sqlalchemy import desc

class FeedbackReply(BaseModel):
    feedback_id: str
    context: str
    teacher_id: Optional[str] = None
    student_id: Optional[str] = None
    class_id: int
    subject_id: int
    is_parents: int
    parent_id: Optional[str] = None
    created_at: datetime
    teacher_name: Optional[str] = None  # Thêm trường để lưu tên giáo viên nếu có
    student_name: Optional[str] = None  # Thêm trường để lưu tên học sinh nếu có

class FeedbackResponse(BaseModel):
    feedback_id: str
    context: str
    teacher_id: Optional[str] = None
    student_id: Optional[str] = None
    class_id: int
    subject_id: int
    is_parents: int
    parent_id: Optional[str] = None
    created_at: datetime
    replies: List[FeedbackReply] = []  # Danh sách phản hồi con
    teacher_name: Optional[str] = None  # Thêm trường để lưu tên giáo viên nếu có
    student_name: Optional[str] = None  # Thêm trường để lưu tên học sinh nếu có
    
class FeedbackCreate(BaseModel):
    context: str
    subject_id: Optional[int] = None
    class_id: Optional[int] = None
    parent_id: Optional[str] = None