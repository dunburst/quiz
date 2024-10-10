from fastapi import FastAPI, HTTPException, status, Depends
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean, ForeignKey, VARCHAR, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import uuid
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
# Kết nối MySQL
DATABASE_URL = "mysql+pymysql://root:12345@localhost:3306/quiz"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
app = FastAPI()
origins = [
    "http://localhost:3000",  # React frontend
    # Add more origins if needed, or use "*" to allow all
]
# Add CORS middleware to the FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow requests from specified origins
    allow_credentials=True,  # Allow cookies and credentials
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)
# Định nghĩa các bảng sử dụng SQLAlchemy
class Subject(Base):
    __tablename__ = "subject"
    subject_id = Column(Integer, primary_key=True, autoincrement=True)
    name_subject = Column(VARCHAR(255), nullable=False)
    image = Column(VARCHAR(255), nullable=False)
class Teacher(Base):
    __tablename__ = "teacher"
    teacher_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    password = Column(VARCHAR(255), nullable=False)
    gender = Column(VARCHAR(255), nullable=False)
    name = Column(VARCHAR(255), nullable=False)
    birth_date = Column(DateTime, nullable=False)
    email = Column(VARCHAR(255), nullable=False)
    phone_number = Column(VARCHAR(15))
    image = Column(VARCHAR(255))
    subject_id = Column(Integer, ForeignKey('subject.subject_id'), nullable=False)
class Class(Base):
    __tablename__ = "class"
    class_id = Column(Integer, primary_key=True, autoincrement=True)
    name_class = Column(VARCHAR(255), nullable=False)
class Student(Base):
    __tablename__ = "student"
    student_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    password = Column(VARCHAR(255), nullable=False)
    gender = Column(VARCHAR(255), nullable=False)
    name = Column(VARCHAR(255), nullable=False)
    birth_date = Column(DateTime, nullable=False)
    email = Column(VARCHAR(255), nullable=False)
    phone_number = Column(VARCHAR(15))
    image = Column(VARCHAR(255))
    class_id = Column(Integer, ForeignKey('class.class_id'), nullable=False)
    first_login = Column(Boolean, default=True)
class Distribution(Base):
    __tablename__ = "distribution"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    class_id = Column(Integer, ForeignKey('class.class_id'), nullable=False)
    teacher_id = Column(String(36), ForeignKey('teacher.teacher_id'), nullable=False)
class Comment(Base):
    __tablename__ = "comment"
    comment_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    context = Column(Text, nullable=False)
    student_id = Column(String(36), ForeignKey('student.student_id'), nullable=False)
    teacher_id = Column(String(36), ForeignKey('teacher.teacher_id'), nullable=False)
# Dependency để lấy session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# API đăng nhập và trả về thông tin người dùng dựa trên id (student_id hoặc teacher_id)
# Định nghĩa Pydantic Model cho body của request
class LoginRequest(BaseModel):
    user_id: str
    password: str

# API đăng nhập
@app.post("/api/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # Kiểm tra nếu là học sinh
    student = db.query(Student).filter(Student.student_id == request.user_id).first()
    if student:
        if student.password != request.password:  # Kiểm tra mật khẩu
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sai mật khẩu")
        if student.first_login:
            return {"id": student.student_id}  # Nếu đăng nhập lần đầu thì trả về ID
        return {  # Nếu không thì trả về đầy đủ thông tin
            "id": student.student_id,
            "name": student.name,
            "email": student.email,
            "phone_number": student.phone_number,
            "birth_date": student.birth_date,
            "image": student.image
        }
    
    # Kiểm tra nếu là giáo viên
    teacher = db.query(Teacher).filter(Teacher.teacher_id == request.user_id).first()
    if teacher:
        if teacher.password != request.password:  # Kiểm tra mật khẩu
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sai mật khẩu")
        return {  # Trả về thông tin giáo viên
            "id": teacher.teacher_id,
            "name": teacher.name,
            "email": teacher.email,
            "phone_number": teacher.phone_number
        }
    
    # Trả về lỗi nếu không tìm thấy người dùng
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy thông tin người dùng")
# API đổi mật khẩu cho học sinh lần đầu đăng nhập
@app.post("/api/change-password")
def change_password(student_id: str, new_password: str, confirm_password: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Học sinh không tồn tại")
    
    if new_password != confirm_password:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mật khẩu xác nhận không đúng")
    Student.first_login = False  # Đặt lại `first_login` thành False sau khi đổi mật khẩu
    student.password = new_password  # Lưu mật khẩu trực tiếp
    db.commit()
    return {"message": "Đổi mật khẩu thành công"}

# Student
# API lấy thông tin học sinh, lớp, môn học và giáo viên
@app.get("/api/student/{student_id}/class_subject")
def get_student_class_subject_teacher(student_id: str, db: Session = Depends(get_db)):
    # Lấy thông tin học sinh
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Không tìm thấy học sinh")
    # Lấy thông tin lớp học của học sinh
    class_info = db.query(Class).filter(Class.class_id == student.class_id).first()
    if not class_info:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")
    # Lấy các phân phối môn học (Distribution) liên quan đến lớp của học sinh
    distributions = db.query(Distribution).filter(Distribution.class_id == student.class_id).all()
    if not distributions:
        raise HTTPException(status_code=404, detail="Không có môn học nào cho lớp này")
    class_info_data = {
        "class_id": class_info.class_id,
        "name_class": class_info.name_class
    }
    subjects_data = []
    # Lấy thông tin môn học và giáo viên giảng dạy cho mỗi môn
    for distribution in distributions:
        teacher = db.query(Teacher).filter(Teacher.teacher_id == distribution.teacher_id).first()
        subject = db.query(Subject).filter(Subject.subject_id == teacher.subject_id).first()

        subjects_data.append({
            "subject_id": subject.subject_id,
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
# Teacher
# API lấy thông tin các lớp học mà giáo viên phụ trách dựa trên teacher_id
@app.get("/api/teacher/classes/{teacher_id}")
def get_teacher_classes(teacher_id: str, db: Session = Depends(get_db)):
    # Lấy thông tin giáo viên
    teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Không tìm thấy giáo viên")
    # Lấy thông tin các lớp mà giáo viên phụ trách từ bảng Distribution
    distributions = db.query(Distribution).filter(Distribution.teacher_id == teacher_id).all()
    if not distributions:
        raise HTTPException(status_code=404, detail="Giáo viên này không phụ trách lớp học nào")

    # Tạo danh sách các lớp
    classes_data = []
    for distribution in distributions:
        class_info = db.query(Class).filter(Class.class_id == distribution.class_id).first()
        if class_info:
            classes_data.append({
                "class_id": class_info.class_id,
                "name_class": class_info.name_class
            })

    return {
        "teacher_id": teacher.teacher_id,
        "teacher_name": teacher.name,
        "classes": classes_data
    }
# Admin
# API lấy toàn bộ thông tin học sinh
@app.get("/api/admin/students")
def get_all_students(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    classe = db.query(Class).filter(Class.class_id == Student.class_id).first()
    if not students:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không có học sinh nào")
    # Tạo danh sách thông tin học sinh
    student_list = []
    for student in students:
        student_info = {
            "student_id": student.student_id,
            "name": student.name,
            "birth_date": student.birth_date,
            "email": student.email,
            "phone_number": student.phone_number,
            "image": student.image,
            "name_class": classe.name_class,
        }
        student_list.append(student_info)
    return student_list
# API lấy toàn bộ thông tin giáo viên
@app.get("/api/admin/teachers")
def get_all_teachers(db: Session = Depends(get_db)):
    teachers = db.query(Teacher).all()
    if not teachers:
        raise HTTPException(status_code=404, detail="Không có giáo viên nào được tìm thấy")
    teacher_data = []
    for teacher in teachers:
        subject = db.query(Subject).filter(Subject.subject_id == teacher.subject_id).first()
        distributions = db.query(Distribution).filter(Distribution.teacher_id == teacher.teacher_id).all()
        if not distributions:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy lớp nào cho giáo viên {teacher.name}")
        class_info = []
        for distribution in distributions:
            class_data = db.query(Class).filter(Class.class_id == distribution.class_id).first()
            if class_data:
                class_info.append({
                    "class_id": class_data.class_id,
                    "name_class": class_data.name_class
                })
        teacher_data.append({
            "teacher_id": teacher.teacher_id,
            "name": teacher.name,
            "gender": teacher.gender,
            "birth_date": teacher.birth_date,
            "email": teacher.email,
            "phone_number": teacher.phone_number,
            "subject": subject.name_subject if subject else "Không rõ",
            "classes": class_info
        })

    return {
        "teachers": teacher_data
    }
    

# API lấy thông tin student theo lớp
@app.get("/api/admin/classes/students/{class_id}")
def get_classes(class_id: int, db: Session = Depends(get_db)):
    # Lấy thông tin lớp học
    classe = db.query(Class).filter(Class.class_id == class_id).first()
    if not classe:
        raise HTTPException(status_code=404, detail="Không tìm thấy class")
    
    # Lấy danh sách học sinh theo class_id
    students = db.query(Student).filter(Student.class_id == class_id).all()
    if not students:
        raise HTTPException(status_code=404, detail="Không có học sinh nào trong lớp này")
    
    # Tạo danh sách thông tin đầy đủ học sinh
    student_data = []
    for student in students:
        student_data.append({
            "student_id": student.student_id,
            "name": student.name,
            "gender": student.gender,
            "birth_date": student.birth_date,
            "email": student.email,
            "phone_number": student.phone_number,
        })

    return {
        "class_id": classe.class_id,
        "name_class": classe.name_class,
        "students": student_data
    }
# API thêm tài khoản học sinh mới
@app.post("/api/admin/create/students")
def create_student(
    student_id: str,
    name: str,
    gender: str,
    birth_date: datetime,
    email: str,
    phone_number: str,
    class_id: int,
    password: str,
    db: Session = Depends(get_db)
):
    # Kiểm tra lớp học có tồn tại không
    class_info = db.query(Class).filter(Class.class_id == class_id).first()
    if not class_info:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")
    # Tạo một học sinh mới
    new_student = Student(
        student_id = student_id,
        name=name,
        gender=gender,
        birth_date=birth_date,
        email=email,
        phone_number=phone_number,
        class_id=class_id,
        password = password,
        image='https://cdn.glitch.global/83bcea06-7c19-41ce-bb52-ae99ba3f0bd0/JaZBMzV14fzRI4vBWG8jymplSUGSGgimkqtJakOV.jpeg?vUB=1728536441877',
        first_login=True
    )
# Thêm học sinh mới vào cơ sở dữ liệu
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return {
        "message": "Tạo tài khoản học sinh thành công",
        "student_id": new_student.student_id
    }