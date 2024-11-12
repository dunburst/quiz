from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from database import get_db
from models import Student, Teacher, Admin, Class, Subject
from pydantic import BaseModel
from passlib.context import CryptContext
from typing import Optional, Union
import uuid
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, role: str, subject_id:Optional[int] = None, class_id:Optional[int] = None, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "role": role, "subject_id": subject_id, "class_id":class_id })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[str] = None 
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        if user_id is None or role is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id, role=role)
    except JWTError:
        raise credentials_exception
    if token_data.role == "student":
        user = db.query(Student).filter(Student.student_id == token_data.user_id).first()
    elif token_data.role == "teacher":
        user = db.query(Teacher).filter(Teacher.teacher_id == token_data.user_id).first()
    elif token_data.role == "admin":
        user = db.query(Admin).filter(Admin.admin_id == token_data.user_id).first()
    else:
        raise credentials_exception
    if user is None:
        raise credentials_exception
    return user

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    first_login: Optional[bool] = None 
    image: Optional[str] = None 
@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Kiểm tra học sinh
    student = db.query(Student).filter(Student.mastudent == form_data.username).first()
    if student and verify_password(form_data.password, student.password):
        access_token = create_access_token(data={"sub": student.student_id}, role="student", class_id = student.class_id)
        return {"access_token": access_token, "token_type": "bearer", "role": "student", "first_login": student.first_login, "image": student.image}
    # Kiểm tra giáo viên
    teacher = db.query(Teacher).filter(Teacher.mateacher == form_data.username).first()
    if teacher and verify_password(form_data.password, teacher.password):
        access_token = create_access_token(data={"sub": teacher.teacher_id}, role="teacher", subject_id = teacher.subject_id)
        return {"access_token": access_token, "token_type": "bearer", "role": "teacher", "image": teacher.image}
    # Kiểm tra quản trị viên
    admin = db.query(Admin).filter(Admin.admin_id == form_data.username).first()
    if admin and verify_password(form_data.password, admin.password):
        access_token = create_access_token(data={"sub": admin.admin_id}, role="admin")
        return {"access_token": access_token, "token_type": "bearer", "role": "admin"}
    # Nếu thông tin không đúng
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
class ChangeRespone(BaseModel):
    new_password: str
    confirm_password: str
@router.post("/api/change-password")
def change_password(
    request: ChangeRespone,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user)
):
    if not isinstance(current_user, (Student, Teacher)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chỉ học sinh mới có thể thay đổi mật khẩu")
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mật khẩu xác nhận không đúng")
    if current_user.first_login is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Người dùng này đã thay đổi mật khẩu rồi")
    current_user.password = hash_password(request.new_password)
    current_user.first_login = False
    db.commit()
    return {"message": "Đổi mật khẩu thành công"}

@router.get("/users/me")
def read_users_me(current_user: BaseModel = Depends(get_current_user), db: Session = Depends(get_db)):
    if isinstance(current_user, Student):
        classes = db.query(Class).filter(Class.class_id == current_user.class_id).first()
        return {"user_id": current_user.student_id, 
                "role": "student", 
                "mastudent": current_user.mastudent,
                "gender" :current_user.gender,
                "name" : current_user.name, 
                "birth_date" : current_user.birth_date, 
                "email" : current_user.email, 
                "phone_number": current_user.phone_number, 
                "image" : current_user.image, 
                "name_class" : classes.name_class,
                "first_login": current_user.first_login}
    elif isinstance(current_user, Teacher):
        subjects = db.query(Subject).filter(Subject.subject_id == current_user.subject_id).first()
        return {"user_id": current_user.teacher_id,
                "role": "teacher", 
                "mateacher": current_user.mateacher,
                "gender" :current_user.gender,
                "name" : current_user.name, 
                "birth_date" : current_user.birth_date, 
                "email" : current_user.email, 
                "phone_number": current_user.phone_number, 
                "image" : current_user.image, 
                "name_subject" : subjects.name_subject}
    elif isinstance(current_user, Admin):
        return {"user_id": current_user.admin_id, "role": "admin"}
    else:
        raise HTTPException(status_code=400, detail="Invalid user role")
        
# Model để nhận thông tin cập nhật
class UpdateUserRequest(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    image: Optional[str] = None
@router.put("/users/put/me", response_model=BaseModel)
def update_user(
    request: UpdateUserRequest,
    db: Session = Depends(get_db),
    current_user: BaseModel = Depends(get_current_user)
):
    if isinstance(current_user, Student):
        if request.name:
            current_user.name = request.name
        if request.gender:
            current_user.gender = request.gender
        if request.birth_date:
            current_user.birth_date = request.birth_date
        if request.email:
            current_user.email = request.email
        if request.phone_number:
            current_user.phone_number = request.phone_number
        if request.image:
            current_user.image = request.image
        db.commit()
        classes = db.query(Class).filter(Class.class_id == current_user.class_id).first()
        return {
            "user_id": current_user.student_id,
            "role": "student",
            "mastudent": current_user.mastudent,
            "gender": current_user.gender,
            "name": current_user.name,
            "birth_date": current_user.birth_date,
            "email": current_user.email,
            "phone_number": current_user.phone_number,
            "image": current_user.image,
            "name_class": classes.name_class if classes else "Unknown",
            "first_login": current_user.first_login
        }
    elif isinstance(current_user, Teacher):
        if request.name:
            current_user.name = request.name
        if request.gender:
            current_user.gender = request.gender
        if request.birth_date:
            current_user.birth_date = request.birth_date
        if request.email:
            current_user.email = request.email
        if request.phone_number:
            current_user.phone_number = request.phone_number
        if request.image:
            current_user.image = request.image
        db.commit()
        subjects = db.query(Subject).filter(Subject.subject_id == current_user.subject_id).first()
        return {
            "user_id": current_user.teacher_id,
            "role": "teacher",
            "mateacher": current_user.mateacher,
            "gender": current_user.gender,
            "name": current_user.name,
            "birth_date": current_user.birth_date,
            "email": current_user.email,
            "phone_number": current_user.phone_number,
            "image": current_user.image,
            "name_subject": subjects.name_subject if subjects else "Unknown"
        }
    elif isinstance(current_user, Admin):
        if request.name:
            current_user.name = request.name
        if request.email:
            current_user.email = request.email
        if request.phone_number:
            current_user.phone_number = request.phone_number
        if request.image:
            current_user.image = request.image
        db.commit()

        return {"user_id": current_user.admin_id, "role": "admin", "name": current_user.name, "email": current_user.email, "phone_number": current_user.phone_number, "image": current_user.image}
    else:
        raise HTTPException(status_code=400, detail="Invalid user role")