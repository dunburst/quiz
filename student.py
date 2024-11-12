from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from database import get_db
from models import Student, Class, Admin, Distribution, Subject, Teacher, Class_quiz, Questions, Quiz, Score
from auth import hash_password, get_current_user
import uuid
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from fastapi_pagination import Page, Params, paginate
from quiz import AnswerResponse, QuestionResponse, QuizDetailResponse
from collections import defaultdict
router = APIRouter()
def update_total_students(class_id: int, db: Session):
    total_students = db.query(Student).filter(Student.class_id == class_id).count()
    class_obj = db.query(Class).filter(Class.class_id == class_id).first()
    if class_obj:
        class_obj.total_student = total_students
        db.commit()
# Lấy thông tin học sinh
# Define StudentResponse model to include 'name_class'
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

# API route to retrieve all students
@router.get("/api/students", response_model=Page[StudentResponse], tags=["Students"])
def get_all_students(
    params: Params = Depends(),
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    if not isinstance(current_user, Admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access this resource")
    # Fetch all students and their respective classes
    students = db.query(Student).all()
    # Check if no students are found
    if not students:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No students found")
    # Compile list with student and class information
    student_list = []
    for student in students:
        classe = db.query(Class).filter(Class.class_id == student.class_id).first()
        student_info = {
            "student_id": student.student_id,
            "mastudent": student.mastudent,
            "gender": student.gender,
            "name": student.name,
            "birth_date": student.birth_date,
            "email": student.email,
            "phone_number": student.phone_number,
            "image": student.image,
            "class_id": student.class_id,
            "name_class": classe.name_class if classe else "Unknown",
            "first_login": student.first_login
        }
        student_list.append(student_info)
    # Paginate and return the response
    return paginate(student_list, params)
#Chi tiết người dùng
@router.get("/api/student/{student_id}", response_model=StudentResponse, tags=["Students"])
def get_student_details(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    # Kiểm tra quyền truy cập của người dùng (chỉ admin mới được phép)
    if not isinstance(current_user, Admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access this resource")
    # Tìm học sinh theo student_id
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    # Lấy thông tin lớp học của học sinh
    classe = db.query(Class).filter(Class.class_id == student.class_id).first()
    # Tạo dữ liệu trả về
    student_info = StudentResponse(
        student_id=student.student_id,
        mastudent=student.mastudent,
        gender=student.gender,
        name=student.name,
        birth_date=student.birth_date,
        email=student.email,
        phone_number=student.phone_number,
        image=student.image,
        class_id=student.class_id,
        name_class=classe.name_class if classe else "Unknown",
        first_login=student.first_login
    )
    return student_info

# Model dùng để nhận dữ liệu cập nhật
class UpdateStudentRequest(BaseModel):
    mastudent: Optional[str] = None
    name: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    image: Optional[str] = None
    class_id: Optional[int] = None

# API route để cập nhật thông tin học sinh
@router.put("/api/put/student/{student_id}", response_model=StudentResponse, tags=["Students"])
def update_student(
    student_id: str,
    request: UpdateStudentRequest,
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    # Kiểm tra quyền truy cập của người dùng (chỉ admin mới được phép)
    if not isinstance(current_user, Admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can update student information")
    # Tìm học sinh theo student_id
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    # Cập nhật các thông tin nếu có trong request
    if request.mastudent:
        student.mastudent = request.mastudent
    if request.name:
        student.name = request.name
    if request.gender:
        student.gender = request.gender
    if request.birth_date:
        student.birth_date = request.birth_date
    if request.email:
        student.email = request.email
    if request.phone_number:
        student.phone_number = request.phone_number
    if request.image:
        student.image = request.image
    if request.class_id:
        student.class_id = request.class_id
    # Lưu thay đổi vào cơ sở dữ liệu
    db.commit()
    # Lấy lại thông tin học sinh đã cập nhật và trả về
    classe = db.query(Class).filter(Class.class_id == student.class_id).first()
    updated_student = StudentResponse(
        student_id=student.student_id,
        mastudent=student.mastudent,
        gender=student.gender,
        name=student.name,
        birth_date=student.birth_date,
        email=student.email,
        phone_number=student.phone_number,
        image=student.image,
        class_id=student.class_id,
        name_class=classe.name_class if classe else "Unknown",
        first_login=student.first_login
    )
    return updated_student

# Thêm học sinh
class StudentCreate(BaseModel):
    mastudent: str
    name: str
    gender: str
    birth_date: datetime
    email: str
    phone_number: str
    class_id: int
    password: str
@router.post("/api/post/students", tags=["Students"])
def create_student(
    student_data: StudentCreate, 
    db: Session = Depends(get_db), 
    current_user: Admin = Depends(get_current_user)
):
    if not isinstance(current_user, Admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access this resource")
    # Check if the class exists
    class_info = db.query(Class).filter(Class.class_id == student_data.class_id).first()
    if not class_info:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")
    # Check if the student already exists
    existing_student = db.query(Student).filter(Student.mastudent == student_data.mastudent).first()
    if existing_student:
        raise HTTPException(status_code=400, detail="Mã học sinh đã tồn tại")
    new_student = Student(
        student_id=str(uuid.uuid4()),
        mastudent=student_data.mastudent,
        name=student_data.name,
        gender=student_data.gender,
        birth_date=student_data.birth_date,
        email=student_data.email,
        phone_number=student_data.phone_number,
        class_id=student_data.class_id,
        password=hash_password(student_data.password),
        image="https://cdn.glitch.global/83bcea06-7c19-41ce-bb52-ae99ba3f0bd0/JaZBMzV14fzRI4vBWG8jymplSUGSGgimkqtJakOV.jpeg?vUB=1728536441877",
        first_login=True
    )
    try:
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        update_total_students(student_data.class_id, db)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Mã học sinh hoặc email đã tồn tại")
    
    return {"message": "Tạo tài khoản học sinh thành công", "student_id": new_student.student_id}

# Update học sinh
class StudentUpdate(BaseModel):
    student_id: str
    name: str = None
    gender: str = None
    birth_date: datetime = None
    email: str = None
    phone_number: str = None
    class_id: int = None
    password: str = None
@router.put("/api/put/students/{student_id}", tags=["Students"])
def update_student(
    student_data: StudentUpdate, 
    db: Session = Depends(get_db), 
    current_user: Admin = Depends(get_current_user)
):
    if not isinstance(current_user, Admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access this resource")
    student = db.query(Student).filter(Student.student_id == student_data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Không tìm thấy học sinh")
    if student_data.name is not None:
        student.name = student_data.name
    if student_data.gender is not None:
        student.gender = student_data.gender
    if student_data.birth_date is not None:
        student.birth_date = student_data.birth_date
    if student_data.email is not None:
        existing_email = db.query(Student).filter(Student.email == student_data.email, Student.student_id != student_data.student_id).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email đã tồn tại")
        student.email = student_data.email
    if student_data.phone_number is not None:
        student.phone_number = student_data.phone_number
    if student_data.class_id is not None:
        class_info = db.query(Class).filter(Class.class_id == student_data.class_id).first()
        if not class_info:
            raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")
        student.class_id = student_data.class_id
        update_total_students(student_data.class_id, db)
    if student_data.password is not None:
        student.password = hash_password(student_data.password)
    try:
        db.commit()
        db.refresh(student)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Đã xảy ra lỗi khi cập nhật thông tin học sinh")
    return {"message": "Cập nhật thông tin học sinh thành công", "student_id": student.student_id}

# API tìm kiếm học sinh với phân trang
@router.get("/api/search/students", response_model=Page[StudentResponse], tags=["Students"])
def search_students(
    name: str, 
    db: Session = Depends(get_db), 
    params: Params = Depends(),
    current_user: Admin = Depends(get_current_user)
):
    if not isinstance(current_user, Admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access this resource")
    students = db.query(Student).filter(Student.name.ilike(f"%{name}%")).all()
    if not students:
        raise HTTPException(status_code=200, detail="Không tìm thấy học sinh nào")
    student_data = []
    for student in students:
        classe = db.query(Class).filter(Class.class_id == student.class_id).first()
        student_info = {
            "mastudent": student.mastudent,
            "name": student.name,
            "gender": student.gender,
            "birth_date": student.birth_date,
            "email": student.email,
            "phone_number": student.phone_number,
            "image": student.image,
            "class_id": student.class_id,
            "name_class": classe.name_class if classe else "Không rõ"
        }
        student_data.append(student_info)
    return paginate(student_data, params)

# API lấy thông tin học sinh, lớp, môn học và giáo viên
@router.get("/api/students/class_subject", tags=["Students"])
def get_student_class_subject_teacher(
    db: Session = Depends(get_db), 
    current_user: Student = Depends(get_current_user)  
):
    student = db.query(Student).filter(Student.student_id == current_user.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Không tìm thấy học sinh")
    class_info = db.query(Class).filter(Class.class_id == student.class_id).first()
    if not class_info:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")
    distributions = db.query(Distribution).filter(Distribution.class_id == student.class_id).all()
    if not distributions:
        raise HTTPException(status_code=404, detail="Không có môn học nào cho lớp này")
    class_info_data = {
        "class_id": class_info.class_id,
        "name_class": class_info.name_class
    }
    subjects_data = []
    for distribution in distributions:
        teacher = db.query(Teacher).filter(Teacher.teacher_id == distribution.teacher_id).first()
        subject = db.query(Subject).filter(Subject.subject_id == teacher.subject_id).first()
        subjects_data.append({
            "subject_id": subject.subject_id,
            "subject_image": subject.image,
            "subject_name": subject.name_subject,
            "teacher": {
                "teacher_id": teacher.teacher_id,
                "name": teacher.name,
            }
        })
    return {
        "student_id": student.student_id,
        "class": class_info_data,
        "subjects": subjects_data
    }


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

@router.get("/api/quizzes/{subject_id}", response_model=Page[dict], tags=["Students"])
def get_quizzes_by_subject(
    subject_id: int,
    params: Params = Depends(),
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    # Kiểm tra nếu người dùng không phải là học sinh
    if not isinstance(current_user, Student):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students can access their quizzes.")
    
    # Lấy danh sách quiz cho lớp học của học sinh
    class_quiz_ids = db.query(Class_quiz.quiz_id).filter(Class_quiz.class_id == current_user.class_id).subquery()
    
    # Lấy các quiz thuộc subject_id và nằm trong lớp của học sinh
    quizzes = db.query(Quiz).join(Teacher, Quiz.teacher_id == Teacher.teacher_id) \
                .filter(Teacher.subject_id == subject_id, Quiz.quiz_id.in_(class_quiz_ids)) \
                .all()
    
    # Lấy điểm của học sinh cho các quiz này
    scores = db.query(Score).filter(Score.student_id == current_user.student_id).all()
    score_dict = {score.quiz_id: score.score for score in scores}
    
    if not quizzes:
        raise HTTPException(status_code=404, detail="No quizzes available for this subject and student class.")
    
    # Chuẩn bị danh sách chi tiết cho từng quiz
    quiz_details = []
    for quiz in quizzes:
        quiz_score = score_dict.get(quiz.quiz_id, None)
        status = "Ongoing" if quiz.due_date > datetime.now() else "Expired"

        if status == "Expired" and quiz_score is None:
            quiz_score = 0
            new_score = Score(
                student_id=current_user.student_id,
                quiz_id=quiz.quiz_id,
                score=quiz_score
            )
            db.add(new_score)
            db.commit()

        quiz_info = {
            "quiz_id": quiz.quiz_id,
            "title": quiz.title,
            "due_date": quiz.due_date,
            "time_limit": quiz.time_limit,
            "question_count": quiz.question_count,
            "status": status,
            "score": quiz_score,
            "teacher_id": quiz.teacher_id
        }
        quiz_details.append(quiz_info)

    # Paginate và trả về danh sách quiz
    return paginate(quiz_details, params)

class StudentScoreResponse(BaseModel):
    student_id: str
    student_name: str
    scores: dict  # Dạng {quiz_title: score}

# API to get students and scores by class_id
@router.get("/api/class/{class_id}/students-scores", response_model=List[StudentScoreResponse], tags=["Teachers"])
def get_class_students_scores(
    class_id: int,
    db: Session = Depends(get_db),
    current_user : Teacher = Depends(get_current_user)
):
    # Xác nhận người dùng có quyền truy cập
    if not isinstance(current_user, Teacher):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only teacher can access this resource")

    # Kiểm tra nếu lớp tồn tại
    class_obj = db.query(Class).filter(Class.class_id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found")

    # Lấy danh sách học sinh trong lớp
    students = db.query(Student).filter(Student.class_id == class_id).all()
    if not students:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No students found in this class")

    # Lấy danh sách các quiz của lớp
    quizzes = db.query(Quiz).join(Class_quiz, Quiz.quiz_id == Class_quiz.quiz_id).filter(Class_quiz.class_id == class_id, Quiz.teacher_id==current_user.teacher_id).all()
    quiz_titles = {quiz.quiz_id: quiz.title for quiz in quizzes}

    # Tạo kết quả cho từng học sinh
    student_scores = []
    for student in students:
        # Lấy điểm của học sinh cho các quiz
        scores = db.query(Score).filter(Score.student_id == student.student_id, Score.quiz_id.in_(quiz_titles.keys())).all()
        score_dict = {quiz_titles[score.quiz_id]: score.score for score in scores}
        # Đảm bảo tất cả các quiz đều có mặt trong score_dict, nếu không thì thêm null
        for quiz_id, quiz_title in quiz_titles.items():
            if quiz_title not in score_dict:
                score_dict[quiz_title] = None

        # Thêm vào danh sách kết quả
        student_scores.append(StudentScoreResponse(
            student_id=student.student_id,
            student_name=student.name,
            scores=score_dict
        ))

    return student_scores