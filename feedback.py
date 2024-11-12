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

@router.get("/api/feedback", response_model=List[FeedbackResponse], tags=["Feedback"])
def get_feedback(
    class_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Union[Student, Teacher, Admin] = Depends(get_current_user),
):
    if isinstance(current_user, Student):
        # Lấy class_id từ token, chỉ cần kiểm tra subject_id được cung cấp
        class_id = current_user.class_id
        if not subject_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cần cung cấp subject_id để truy cập phản hồi.")
    elif isinstance(current_user, Teacher):
        # Lấy subject_id từ token, chỉ cần kiểm tra class_id được cung cấp
        subject_id = current_user.subject_id
        if not class_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cần cung cấp class_id để truy cập phản hồi.")
        class_assigned = db.query(Distribution).filter(
            Distribution.class_id == class_id,
            Distribution.teacher_id == current_user.teacher_id
        ).first()
        if not class_assigned:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền truy cập lớp học này.")
    elif isinstance(current_user, Admin):
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ học sinh, giáo viên và quản trị viên mới có quyền xem phản hồi."
        )

    # Lấy tất cả phản hồi theo class_id và subject_id
    feedback_list = db.query(Feedback).filter_by(
        class_id=class_id,
        subject_id=subject_id
    ).all()

    # Tạo một dictionary để nhóm phản hồi cha và con
    feedback_dict = {}
    for fb in feedback_list:
        teacher_name = None
        student_name = None

        # Lấy tên người phản hồi nếu là giáo viên hoặc học sinh
        if fb.teacher_id:
            teacher = db.query(Teacher).filter_by(teacher_id=fb.teacher_id).first()
            teacher_name = teacher.name if teacher else None
        if fb.student_id:
            student = db.query(Student).filter_by(student_id=fb.student_id).first()
            student_name = student.name if student else None

        if fb.is_parents == 0:
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
                replies=[],
                teacher_name=teacher_name,
                student_name=student_name
            )
        elif fb.is_parents == 1:
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
                    created_at=fb.created_at,
                    teacher_name=teacher_name,
                    student_name=student_name
                ))

    result = list(feedback_dict.values())
    return result

class FeedbackCreate(BaseModel):
    context: str
    subject_id: Optional[int] = None
    class_id: Optional[int] = None
    parent_id: Optional[str] = None

@router.post("/api/post/feedback", response_model=FeedbackResponse, tags=["Feedback"])
def create_feedback(
    feedback: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: Union[Student, Teacher] = Depends(get_current_user),
):
    # Kiểm tra quyền của học sinh hoặc giáo viên
    if isinstance(current_user, Student):
        feedback.class_id = current_user.class_id
        if not feedback.subject_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cần cung cấp subject_id để tạo phản hồi.")
        student = db.query(Student).filter(
            Student.student_id == current_user.student_id,
            Student.class_id == feedback.class_id
        ).first()
        if not student:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền gửi phản hồi cho lớp này.")
    elif isinstance(current_user, Teacher):
        feedback.subject_id = current_user.subject_id
        if not feedback.class_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cần cung cấp class_id để tạo phản hồi.")
        class_assigned = db.query(Distribution).filter(
            Distribution.class_id == feedback.class_id,
            Distribution.teacher_id == current_user.teacher_id
        ).first()
        if not class_assigned:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền gửi phản hồi cho lớp này.")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chỉ học sinh và giáo viên mới có quyền tạo phản hồi.")

    # Xác định is_parents dựa trên việc có parent_id hay không
    is_parents = 1 if feedback.parent_id else 0

    # Tạo phản hồi mới
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

    # Lấy tên của người tạo phản hồi
    teacher_name = current_user.name if isinstance(current_user, Teacher) else None
    student_name = current_user.name if isinstance(current_user, Student) else None

    # Xác định đối tượng nhận thông báo
    recipients = []

    # Nếu người tạo phản hồi là giáo viên, gửi thông báo đến tất cả học sinh trong lớp
    if isinstance(current_user, Teacher):
        students = db.query(Student).filter(Student.class_id == feedback.class_id).all()
        recipients.extend(students)

    # Nếu người tạo phản hồi là học sinh, gửi thông báo đến giáo viên phụ trách môn học của lớp
    elif isinstance(current_user, Student):
        teachers = db.query(Teacher).join(Distribution).filter(
            Distribution.class_id == feedback.class_id,
            Teacher.subject_id == feedback.subject_id
        ).all()
        recipients.extend(teachers)

    # Tạo thông báo cho mỗi người nhận
    for recipient in recipients:
        notification = Notification(
            noti_id=str(uuid.uuid4()),
            context=f"Có một phản hồi mới trong lớp {feedback.class_id} về môn học {feedback.subject_id}.",
            time=datetime.now(),
            teacher_id=recipient.teacher_id if isinstance(recipient, Teacher) else None,
            student_id=recipient.student_id if isinstance(recipient, Student) else None
        )
        db.add(notification)

    db.commit()
    return FeedbackResponse(
        feedback_id=new_feedback.feedback_id,
        context=new_feedback.context,
        teacher_id=new_feedback.teacher_id,
        student_id=new_feedback.student_id,
        class_id=new_feedback.class_id,
        subject_id=new_feedback.subject_id,
        is_parents=new_feedback.is_parents,
        parent_id=new_feedback.parent_id,
        created_at=new_feedback.created_at,
        replies=[],
        teacher_name=teacher_name,
        student_name=student_name
    )