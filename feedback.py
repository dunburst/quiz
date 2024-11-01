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
from typing import List, Optional
router = APIRouter()

router = APIRouter()
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

@router.get("/api/feedback/", response_model=List[FeedbackResponse], tags=["Feedback"])
def get_feedback(
    class_id: int,
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: Union[Student, Teacher] = Depends(get_current_user),
):
    # Kiểm tra quyền của học sinh và giáo viên (đã rút ngắn để đơn giản)
    if isinstance(current_user, Student):
        student = db.query(Student).filter(Student.student_id == current_user.student_id, Student.class_id == class_id).first()
        if not student:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền truy cập.")
    elif isinstance(current_user, Teacher):
        teacher = db.query(Teacher).filter(Teacher.teacher_id == current_user.teacher_id).first()
        class_assigned = db.query(Distribution).filter(
            Distribution.class_id == class_id, Distribution.teacher_id == teacher.teacher_id).first()
        if not class_assigned or teacher.subject_id != subject_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền truy cập.")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chỉ có học sinh và giáo viên mới có quyền xem phản hồi.")
    # Lấy tất cả phản hồi theo class_id và subject_id
    feedback_list = db.query(Feedback).filter_by(class_id=class_id, subject_id=subject_id).all()
    # Tạo một dictionary để nhóm phản hồi cha và con
    feedback_dict = {}
    # Phân loại phản hồi cha và con
    for fb in feedback_list:
        if fb.is_parents == 0:
            # Phản hồi cha - thêm vào dictionary với feedback_id là key
            feedback_dict[fb.feedback_id] = FeedbackResponse(
                feedback_id=fb.feedback_id,
                context=fb.context,
                teacher_id=fb.teacher_id,
                student_id=fb.student_id,
                class_id=fb.class_id,
                subject_id=fb.subject_id,
                is_parents=fb.is_parents,
                parent_id=fb.parent_id,
                created_at=fb.created_at,
                replies=[]  # Tạo danh sách replies rỗng
            )
        elif fb.is_parents == 1:
            # Phản hồi con - thêm vào replies của phản hồi cha nếu parent_id hợp lệ
            if fb.parent_id in feedback_dict:
                feedback_dict[fb.parent_id].replies.append(FeedbackReply(
                    feedback_id=fb.feedback_id,
                    context=fb.context,
                    teacher_id=fb.teacher_id,
                    student_id=fb.student_id,
                    class_id=fb.class_id,
                    subject_id=fb.subject_id,
                    is_parents=fb.is_parents,
                    parent_id=fb.parent_id,
                    created_at=fb.created_at
                ))
    # Chuyển đổi từ dictionary thành danh sách kết quả
    result = list(feedback_dict.values())
    
    return result

class FeedbackCreate(BaseModel):
    context: str
    subject_id: int
    class_id: int
    parent_id: Optional[str] = None

@router.post("/api/post/feedback/", response_model=FeedbackResponse, tags=["Feedback"])
def create_feedback(
    feedback: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: Union[Student, Teacher] = Depends(get_current_user),
):
    # Permission checks (student/teacher validation omitted here for brevity)
      # Kiểm tra quyền của học sinh hoặc giáo viên
    if isinstance(current_user,Student):
        # Xác định xem học sinh có thuộc lớp này không
        student = db.query(Student).filter(
            Student.student_id == current_user.student_id, Student.class_id == feedback.class_id
        ).first()
        if not student:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền gửi phản hồi cho lớp này.")
    # Determine is_parents based on parent_id presence
    is_parents = 1 if feedback.parent_id else 0
    new_feedback = Feedback(
        context=feedback.context,
        teacher_id=current_user.teacher_id if isinstance(current_user, Teacher) else None,
        student_id=current_user.student_id if isinstance(current_user, Student) else None,
        class_id=feedback.class_id,
        subject_id=feedback.subject_id,
        is_parents=is_parents,
        parent_id=feedback.parent_id
    )
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    return new_feedback