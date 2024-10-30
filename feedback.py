from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Union
from pydantic import BaseModel
from database import get_db
from models import Teacher, Subject, Admin, Class, Distribution, Feedback, Distribution, Student
from auth import hash_password, get_current_user
import uuid
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from fastapi_pagination import Page, Params, paginate
router = APIRouter()

class FeedbackCreate(BaseModel):
    context: str
    class_id: Optional[int]  # Required for teachers
    subject_id: Optional[int]  # Required for teachers
    is_parents: Optional[int] = 0  # Default to parent feedback
    parent_id: Optional[str] = None  # ID of parent feedback if it's a reply

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
    
@router.post("/api/post/feedback", response_model=FeedbackResponse, tags=["Feedbacks"])
def add_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    new_feedback = Feedback(
        context=feedback.context,
        is_parents=feedback.is_parents,
        parent_id=feedback.parent_id
    )

    if isinstance(current_user, Teacher):
        if not feedback.class_id or not feedback.subject_id:
            raise HTTPException(status_code=400, detail="Cần chỉ định cả class_id và subject_id")
        
        is_teacher_assigned = db.query(Distribution).filter(
            Distribution.teacher_id == current_user.teacher_id,
            Distribution.class_id == feedback.class_id
        ).join(Teacher).filter(Teacher.subject_id == feedback.subject_id).first()

        if not is_teacher_assigned:
            raise HTTPException(status_code=403, detail="Giáo viên không phụ trách lớp và môn học này")
        
        new_feedback.teacher_id = current_user.teacher_id
        new_feedback.class_id = feedback.class_id
        new_feedback.subject_id = feedback.subject_id

    elif isinstance(current_user, Student):
        if current_user.class_id != feedback.class_id:
            raise HTTPException(status_code=403, detail="Học sinh không thuộc lớp này")
        
        new_feedback.student_id = current_user.student_id
        new_feedback.class_id = current_user.class_id
        new_feedback.subject_id = feedback.subject_id

    if feedback.is_parents == 1:
        parent_feedback = db.query(Feedback).filter(Feedback.feedback_id == feedback.parent_id).first()
        if not parent_feedback:
            raise HTTPException(status_code=404, detail="Không tìm thấy feedback cha")
        new_feedback.parent_id = feedback.parent_id

    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    return new_feedback

@router.get("/api/feedback", response_model=List[FeedbackResponse], tags=["Feedbacks"])
def get_feedback(class_id: int, subject_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if isinstance(current_user, Teacher):
        is_assigned = db.query(Distribution).filter(
            Distribution.class_id == class_id,
            Distribution.teacher_id == current_user.teacher_id,
            Teacher.subject_id == subject_id
        ).join(Teacher, Teacher.teacher_id == Distribution.teacher_id).first()

        if not is_assigned:
            raise HTTPException(status_code=403, detail="Access denied: Not assigned to this class and subject.")
    
    elif isinstance(current_user, Student):
        student = db.query(Student).filter(
            Student.student_id == current_user.student_id,
            Student.class_id == class_id
        ).first()

        if not student:
            raise HTTPException(status_code=403, detail="Access denied: Not enrolled in this class.")
    
    parent_feedbacks = db.query(Feedback).filter(
        Feedback.class_id == class_id,
        Feedback.subject_id == subject_id,
        Feedback.is_parents == 0
    ).all()

    feedbacks = []
    for parent in parent_feedbacks:
        feedbacks.append(parent)
        child_feedbacks = db.query(Feedback).filter(Feedback.parent_id == parent.feedback_id).all()
        feedbacks.extend(child_feedbacks)
    
    return feedbacks