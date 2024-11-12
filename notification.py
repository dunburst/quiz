from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Union
from pydantic import BaseModel
from database import get_db
from models import Teacher, Subject, Admin, Class, Distribution, Feedback, Distribution, Student, Notification
from auth import hash_password, get_current_user
import uuid
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from fastapi_pagination import Page, Params, paginate
from typing import List, Optional
from sqlalchemy import desc
router = APIRouter()
class NotificationResponse(BaseModel):
    noti_id: str
    context: str
    time: datetime
    teacher_id: Optional[str] = None
    student_id: Optional[str] = None
@router.get("/api/notifications/", response_model=List[NotificationResponse], tags=["Notifications"])
def read_user_notifications(current_user: BaseModel = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check user role and fetch notifications accordingly
    if isinstance(current_user, Student):
        # Fetch notifications for the student
        notifications = db.query(Notification).filter(Notification.student_id == current_user.student_id).all()
    elif isinstance(current_user, Teacher):
        # Fetch notifications for the teacher
        notifications = db.query(Notification).filter(Notification.teacher_id == current_user.teacher_id).all()
    else:
        raise HTTPException(status_code=400, detail="Invalid user role")
    return notifications

