from fastapi import FastAPI, HTTPException, status, Depends
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean, ForeignKey, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import uuid
from datetime import datetime
# Kết nối MySQL
DATABASE_URL = "mysql+pymysql://root:12345@localhost:3306/quiz"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
app = FastAPI()
# Định nghĩa các bảng sử dụng SQLAlchemy
class User(Base):
    __tablename__ = "user"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    password = Column(VARCHAR(255), nullable=False)

class Subject(Base):
    __tablename__ = "subject"
    subject_id = Column(Integer, primary_key=True, autoincrement=True)
    name_subject = Column(VARCHAR(255), nullable=False)
class Teacher(Base):
    __tablename__ = "teacher"
    teacher_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(VARCHAR(255), nullable=False)
    birth_date = Column(DateTime, nullable=False)
    email = Column(VARCHAR(255), nullable=False)
    phone_number = Column(VARCHAR(15))
    image = Column(VARCHAR(255))
    subject_id = Column(Integer, ForeignKey('Subject.subject_id'), nullable=False)
    user_id = Column(String(36), ForeignKey('User.id'), nullable=False)
class Class(Base):
    __tablename__ = "class"
    class_id = Column(Integer, primary_key=True, autoincrement=True)
    name_class = Column(VARCHAR(255), nullable=False)
class Student(Base):
    __tablename__ = "student"
    student_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(VARCHAR(255), nullable=False)
    birth_date = Column(DateTime, nullable=False)
    email = Column(VARCHAR(255), nullable=False)
    phone_number = Column(VARCHAR(15))
    image = Column(VARCHAR(255))
    class_id = Column(Integer, ForeignKey('Class.class_id'), nullable=False)
    user_id = Column(String(36), ForeignKey('User.id'), nullable=False)
    first_login = Column(Boolean, default=True)
class Distribution(Base):
    __tablename__ = "distribution"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    class_id = Column(Integer, ForeignKey('Class.class_id'), nullable=False)
    teacher_id = Column(String(36), ForeignKey('Teacher.teacher_id'), nullable=False)
# Dependency để lấy session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# API đăng nhập và trả về thông tin người dùng dựa trên id (student_id hoặc teacher_id)
@app.post("/login")
def login(user_id: str, password: str, db: Session = Depends(get_db)):
    # Kiểm tra nếu là học sinh
    student = db.query(Student).filter(Student.student_id == user_id).first()
    if student:
        user = db.query(User).filter(User.id == student.user_id).first()
        if user.password != password:  # Kiểm tra mật khẩu trực tiếp
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
    teacher = db.query(Teacher).filter(Teacher.teacher_id == user_id).first()
    if teacher:
        user = db.query(User).filter(User.id == teacher.user_id).first()
        if user.password != password:  # Kiểm tra mật khẩu trực tiếp
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sai mật khẩu")
        
        return {
            "id": teacher.teacher_id,
            "name": teacher.name,
            "email": teacher.email,
            "phone_number": teacher.phone_number
        }
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy thông tin người dùng")
# API đổi mật khẩu cho học sinh lần đầu đăng nhập
@app.post("/change-password")
def change_password(student_id: str, new_password: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Học sinh không tồn tại")
    
    # Lấy user tương ứng và đổi mật khẩu
    user = db.query(User).filter(User.id == student.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Người dùng không tồn tại")
    user.password = new_password  # Lưu mật khẩu trực tiếp
    student.first_login = False  # Đặt lại `first_login` thành False sau khi đổi mật khẩu
    db.commit()
    return {"message": "Đổi mật khẩu thành công"}
# API lấy toàn bộ thông tin học sinh
@app.get("/get/students")
def get_all_students(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    # Nếu không có học sinh nào trong cơ sở dữ liệu
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
            "class_id": student.class_id,
            "user_id": student.user_id,
            "first_login": student.first_login
        }
        student_list.append(student_info)
    return student_list
@app.get("/get/class/{class_id}")
def get_class(class_id: int, db: Session = Depends(get_db)):
    class_info = db.query(Class).filter(Class.class_id == class_id).first()
    if not class_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy lớp học")
    
    return {
        "class_id": class_info.class_id,
        "name_class": class_info.name_class
    }
