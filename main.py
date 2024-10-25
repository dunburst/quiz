from fastapi import FastAPI, HTTPException, status, Depends, Query,APIRouter    
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean, ForeignKey, VARCHAR, Text, Float, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import uuid
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from fastapi_pagination import Page, Params, paginate
from sqlalchemy.exc import IntegrityError



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
class Admin(Base):
    __tablename__ = "admin"
    admin_id = Column(String(36), primary_key=True, autoincrement=True)
    password = Column(VARCHAR(255), nullable=False)
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
    years = Column(String(36))
    total_student = Column(Integer )
    id_grades = Column(Integer,  ForeignKey('grades.grades_id'), nullable=False)
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
class Grades(Base):
    __tablename__ = "grades"
    id_grades = Column(Integer, primary_key=True, autoincrement=True)
    name_grades = Column(VARCHAR(255), nullable=False)
class Quiz(Base):
    __tablename__ = 'quiz'
    quiz_id = Column(String(36),primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String)
    due_date = Column(DateTime)
    time_limit = Column(Integer)
    question_count = Column(Integer)
    teacher_id = Column(Integer, ForeignKey('teacher.teacher_id'))

class Questions(Base):
    __tablename__ = 'questions'
    question_id = Column(String(36),primary_key=True, default=lambda: str(uuid.uuid4()))
    quiz_id = Column(String(36), ForeignKey('quiz.quiz_id'))
    question_text= Column(Text, nullable=False)
class Answer(Base):
    __tablename__ = 'answer'
    answer_id = Column(String(36),primary_key=True, default=lambda: str(uuid.uuid4()))
    question_id = Column(String(36), ForeignKey('questions.question_id'))
    answer = Column(Text)
    is_correct = Column(Boolean, default=True)
class Score(Base):
    __tablename__ = 'score'
    
    score_id = Column(String(36), primary_key=True, index=True)
    student_id = Column(String(36), ForeignKey('student.student_id'))  # student_id là String
    quiz_id = Column(String(36), ForeignKey('quiz.quiz_id'))  # quiz_id là String
    score = Column(Float)
    time_start = Column(DateTime)
    time_end = Column(DateTime)
    status = Column(String)
class Class_quiz(Base):
     __tablename__ = 'class_quiz'
     class_quiz_id = Column(String(36), primary_key=True, index=True)
     class_id = Column(Integer, ForeignKey('class.class_id'))   
     quiz_id = Column(String(36), ForeignKey('quiz.quiz_id'))

    
# Dependency để lấy session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# Hàm để cập nhật số lượng học sinh của lớp
def update_total_students(class_id: int, db: Session):
    total_students = db.query(Student).filter(Student.class_id == class_id).count()
    class_obj = db.query(Class).filter(Class.class_id == class_id).first()
    if class_obj:
        class_obj.total_student = total_students
        db.commit()
# Định nghĩa Pydantic Model cho body của request
class LoginRequest(BaseModel):
    user_id: str
    password: str

class ChangePasswordRequest(BaseModel):
    student_id: str = Field(..., title="ID của học sinh")
    new_password: str = Field(..., title="Mật khẩu mới")
    confirm_password: str = Field(..., title="Xác nhận mật khẩu mới")

class TeacherCreate(BaseModel):
    teacher_id: str
    name: str
    gender: str
    birth_date: datetime
    email: str
    phone_number: str
    subject_id: int
    password: str
    class_ids: List[int]  # Danh sách ID lớp học để phân công cho giáo viên

class StudentCreate(BaseModel):
    student_id: str
    name: str
    gender: str
    birth_date: datetime
    email: str
    phone_number: str
    class_id: int
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
      # Kiểm tra nếu là giáo viên
    admin = db.query(Admin).filter(Admin.admin_id == request.user_id).first()
    if admin:
        if admin.password != request.password:  # Kiểm tra mật khẩu
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sai mật khẩu")
        return {  # Trả về thông tin giáo viên
            "id": admin.admin_id
        }
    # Trả về lỗi nếu không tìm thấy người dùng
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy thông tin người dùng")
# API đổi mật khẩu cho học sinh lần đầu đăng nhập
@app.post("/api/change-password")
def change_password(request: ChangePasswordRequest, db: Session = Depends(get_db)):
    # Sử dụng request.student_id, request.new_password, request.confirm_password
    student = db.query(Student).filter(Student.student_id == request.student_id).first()
    
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Học sinh không tồn tại")
    
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mật khẩu xác nhận không đúng")

    student.first_login = False  # Đặt lại `first_login` thành False sau khi đổi mật khẩu
    student.password = request.new_password  # Lưu mật khẩu trực tiếp
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

# API lấy thông tin các bài làm của sinh viên
@app.get("/quizzes/{student_id}")
def get_quizzes(student_id: str, db: Session = Depends(get_db)):  # Đổi student_id thành string
    # Lấy thông tin học sinh, bao gồm cả class_id của học sinh đó
    student = db.query(Student).filter(Student.student_id == student_id).first()  # Sử dụng student_id là String
    if not student:
        raise HTTPException(status_code=404, detail="Không tìm thấy học sinh")
    
    # Lấy tất cả các quiz được phân cho lớp của học sinh
    class_quiz_ids = db.query(Class_quiz.quiz_id).filter(Class_quiz.class_id == student.class_id).subquery()
    
    # Lấy các quiz từ bảng Quiz và đối chiếu với bảng Score
    quizzes = db.query(Quiz).filter(Quiz.quiz_id.in_(class_quiz_ids)).all()
    
    # Lấy điểm cho học sinh từ bảng Score
    scores = db.query(Score).filter(Score.student_id == student_id).all()
    
    # Tạo từ điển để ánh xạ quiz_id với score
    score_dict = {score.quiz_id: score.score for score in scores}

    # Kiểm tra xem có quiz nào không
    if not quizzes:
        raise HTTPException(status_code=404, detail="Chưa có bài quiz nào cho học sinh này")
    
    result = []
    for quiz in quizzes:
        # Lấy điểm tương ứng từ từ điển
        quiz_score = score_dict.get(quiz.quiz_id, None)
        status = "Còn hạn" if quiz.due_date > datetime.now() else "Hết hạn"
        result.append({
            "status": status,
            "title": quiz.title,
            "due_date": quiz.due_date.strftime("%d/%m/%Y"),
            "time_limit": f"{quiz.time_limit} phút",
            "question_count": quiz.question_count,
            "score": quiz_score  # Sử dụng điểm từ từ điển
        })
    
    return result
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
        raise HTTPException(status_code=404)
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
#Tạo quiz
class AnswerCreate(BaseModel):
    answer: str
    is_correct: bool
class QuestionCreate(BaseModel):
    question_text: str
    answers: List[AnswerCreate]

class ClassAssignment(BaseModel):
    class_id: int  # ID của lớp mà quiz sẽ được giao
class QuizCreate(BaseModel):

    title: str
    due_date: datetime
    time_limit: int
    teacher_id: str
    class_assignments: List[ClassAssignment]  

class AnswerUpdate(BaseModel):
    answer: str
    is_correct: bool
class QuestionUpdate(BaseModel):
    question_id: str
    question_text: str
    answers: List[AnswerUpdate]
class UpdateQuestion(BaseModel):
    question: List[QuestionUpdate]



class AnswerResponse(BaseModel):
    answer_id: str
    answer: str
    is_correct: bool

class QuestionResponse(BaseModel):
    question_id: str
    question_text: str
    answers: List[AnswerResponse]





#API lấy thông tin bài tập của giáo viên 

@app.get("/api/admin/quizzes", response_model=Page[dict])
def get_all_quizzes(db: Session = Depends(get_db), params: Params = Depends()):
    quizzes = db.query(Quiz).all()
    
    # Kiểm tra nếu không có quiz nào
    if not quizzes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không có quiz nào")
    
    # Tạo danh sách thông tin quiz
    quiz_list = []
    for quiz in quizzes:
        # Lấy thông tin giáo viên
        teacher = db.query(Teacher).filter(Teacher.teacher_id == quiz.teacher_id).first()
        
        # Lấy thông tin lớp từ bảng class_quiz
        class_quizzes = db.query(Class_quiz).filter(Class_quiz.quiz_id == quiz.quiz_id).all()
        class_ids = [class_quiz.class_id for class_quiz in class_quizzes] if class_quizzes else []
        
        # Lấy tên lớp từ bảng class
        class_names = db.query(Class.name_class).filter(Class.class_id.in_(class_ids)).all()
        class_names_list = [class_name[0] for class_name in class_names]  # Chuyển đổi từ tuple sang danh sách
        
        quiz_info = {
            "quiz_id": quiz.quiz_id,
            "title": quiz.title,
            "due_date": quiz.due_date,
            "time_limit": quiz.time_limit,
            "question_count": quiz.question_count,
            "class_ids": class_names_list  # Danh sách tên lớp liên quan
        }
        quiz_list.append(quiz_info)
    
    # Trả về dữ liệu với phân trang
    return paginate(quiz_list, params)

# API endpoint for creating a quiz
@app.post("/api/teacher/create/quiz")
def create_quiz(quiz_data: QuizCreate, db: Session = Depends(get_db)):
    # Kiểm tra xem teacher_id có tồn tại không
    teacher_info = db.query(Teacher).filter(Teacher.teacher_id == quiz_data.teacher_id).first()
    if not teacher_info:
        raise HTTPException(status_code=404, detail="Không tìm thấy giáo viên")
    
    # Tạo một quiz mới
    new_quiz = Quiz(
        title=quiz_data.title,
        due_date=quiz_data.due_date,
        time_limit=quiz_data.time_limit,
        question_count=0,  # Ban đầu là 0, sẽ cập nhật sau khi thêm câu hỏi
        teacher_id=quiz_data.teacher_id
    )
    
    db.add(new_quiz)
    db.commit()
    db.refresh(new_quiz)

    # Giao bài cho từng lớp
    for assignment in quiz_data.class_assignments:
        # Kiểm tra xem lớp có tồn tại không
        class_obj = db.query(Class).filter(Class.class_id == assignment.class_id).first()
        if not class_obj:
            raise HTTPException(status_code=404, detail=f"Lớp với ID {assignment.class_id} không tồn tại")

        # Tạo bản ghi mới trong bảng class_quiz
        new_class_quiz = Class_quiz(
            class_quiz_id=str(uuid.uuid4()),  # Tạo ID duy nhất cho bản ghi
            class_id=assignment.class_id,
            quiz_id=new_quiz.quiz_id
        )
        
        db.add(new_class_quiz)

    db.commit()  # Lưu tất cả thay đổi

    return {
        "message": "Tạo quiz và giao bài cho lớp thành công",
        "quiz_id": new_quiz.quiz_id
    }
#API tạo câu hỏi
@app.post("/api/quiz/{quiz_id}/create/questions")
def create_questions_for_quiz(
    quiz_id: str, 
    question_data: QuestionCreate, 
    db: Session = Depends(get_db)
):
    # Kiểm tra xem quiz có tồn tại không
    quiz_info = db.query(Quiz).filter(Quiz.quiz_id == quiz_id).first()
    if not quiz_info:
        raise HTTPException(status_code=404, detail="Không tìm thấy quiz")
    # Tạo câu hỏi mới cho quiz
    new_question = Questions(
        quiz_id=quiz_id,
        question_text=question_data.question_text
    )
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    # Kiểm tra câu trả lời đúng
    correct_answers = [ans for ans in question_data.answers if ans.is_correct]
    if len(correct_answers) != 1:
        raise HTTPException(status_code=400, detail="Mỗi câu hỏi phải có đúng một câu trả lời chính xác.")
    # Tạo câu trả lời cho câu hỏi
    for answer_data in question_data.answers:
        new_answer = Answer(
            question_id=new_question.question_id,
            answer=answer_data.answer,
            is_correct=answer_data.is_correct
        )
        db.add(new_answer)
    db.commit()

    # Cập nhật số lượng câu hỏi cho quiz
    quiz_info.question_count += 1
    db.commit()

    return {
        "message": "Tạo câu hỏi và câu trả lời thành công",
        "question_id": new_question.question_id
    }
@app.put("/api/quiz/update-question/{quiz_id}")
def update_question_for_quiz(
    quiz_id: str,  # Nhận quiz_id từ đường dẫn
    update_data: UpdateQuestion,  # Lấy toàn bộ dữ liệu từ body
    db: Session = Depends(get_db)
):
    # Kiểm tra xem quiz có tồn tại không
    quiz_info = db.query(Quiz).filter(Quiz.quiz_id == quiz_id).first()
    if not quiz_info:
        raise HTTPException(status_code=404, detail="Không tìm thấy quiz")

    # Duyệt qua từng câu hỏi để xử lý
    for question_data in update_data.question:
        # Kiểm tra xem câu hỏi có tồn tại không
        question_info = db.query(Questions).filter(
            Questions.question_id == question_data.question_id, 
            Questions.quiz_id == quiz_id  # Sử dụng quiz_id từ URL
        ).first()
        if not question_info:
            raise HTTPException(status_code=404, detail=f"Câu hỏi {question_data.question_id} không tồn tại.")

        # Cập nhật nội dung câu hỏi
        question_info.question_text = question_data.question_text

        # Kiểm tra xem câu trả lời đúng có chính xác một đáp án không
        correct_answers = [ans for ans in question_data.answers if ans.is_correct]
        if len(correct_answers) != 1:
            raise HTTPException(status_code=400, detail=f"Câu hỏi {question_data.question_id} phải có đúng một câu trả lời chính xác.")

        # Xóa tất cả câu trả lời cũ của câu hỏi
        db.query(Answer).filter(Answer.question_id == question_data.question_id).delete()
        db.commit()

        # Thêm các câu trả lời mới cho câu hỏi
        for answer_data in question_data.answers:
            new_answer = Answer(
                question_id=question_data.question_id,
                answer=answer_data.answer,
                is_correct=answer_data.is_correct
            )
            db.add(new_answer)
        
        db.commit()  # Chỉ cần commit sau khi thêm tất cả câu trả lời cho câu hỏi

    return {
        "message": "Cập nhật câu hỏi và câu trả lời thành công"
    }
#API lấy question trong quiz
@app.get("/api/quiz/{quiz_id}/questions", response_model=List[QuestionResponse])
def get_questions_for_quiz(quiz_id: str, db: Session = Depends(get_db)):
    # Kiểm tra xem quiz có tồn tại không
    quiz_info = db.query(Quiz).filter(Quiz.quiz_id == quiz_id).first()
    if not quiz_info:
        raise HTTPException(status_code=404, detail="Không tìm thấy quiz")

    # Lấy tất cả câu hỏi liên quan đến quiz
    questions = db.query(Questions).filter(Questions.quiz_id == quiz_id).all()
    if not questions:
        return []  # Nếu không có câu hỏi nào, trả về danh sách trống

    # Tạo danh sách câu hỏi và câu trả lời
    question_responses = []
    for question in questions:
        answers = db.query(Answer).filter(Answer.question_id == question.question_id).all()
        answer_data = [
            {
                "answer_id": answer.answer_id,
                "answer": answer.answer,
                "is_correct": answer.is_correct,
            } for answer in answers
        ]
        
        question_responses.append({
            "question_id": question.question_id,
            "question_text": question.question_text,
            "answers": answer_data,
        })

    return question_responses

# class UpdateClassQuizRequest(BaseModel):
#     class_id: int
# @app.put("/api/admin/class_quiz/{quiz_id}")
# def update_class_for_quiz(quiz_id: str, update_class_quiz_request: UpdateClassQuizRequest, db: Session = Depends(get_db)):
#     # Kiểm tra xem bản ghi class_quiz có tồn tại không
#     class_quiz_record = db.query(Class_quiz).filter(Class_quiz.quiz_id == quiz_id).first()
    
#     if not class_quiz_record:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bản ghi không tồn tại")

#     # Cập nhật class_id
#     class_quiz_record.class_id = update_class_quiz_request.class_id
#     db.commit()

#     return {
#         "message": "Cập nhật lớp thành công",
#         "quiz_id": quiz_id,
#         "new_class_id": update_class_quiz_request.class_id
#     }



# Admin
# API lấy toàn bộ thông tin học sinh
@app.get("/api/admin/students", response_model=Page[dict])
def get_all_students(db: Session = Depends(get_db), params: Params = Depends()):
    students = db.query(Student).all()
    
    # Kiểm tra nếu không có học sinh nào
    if not students:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không có học sinh nào")
    
    # Tạo danh sách thông tin học sinh
    student_list = []
    for student in students:
        # Lấy thông tin lớp của học sinh
        classe = db.query(Class).filter(Class.class_id == student.class_id).first()
        
        student_info = {
            "student_id": student.student_id,
            "name": student.name,
            "birth_date": student.birth_date,
            "phone_number": student.phone_number,
            "name_class": classe.name_class if classe else "Không rõ",
            "gender": student.gender
        }
        student_list.append(student_info)
    
    # Trả về dữ liệu với phân trang
    return paginate(student_list, params)
# API lấy toàn bộ thông tin giáo viên
@app.get("/api/admin/teachers", response_model=Page[dict])
def get_all_teachers(db: Session = Depends(get_db), params: Params = Depends()):
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
    
    return paginate(teacher_data, params)
#API lấy thông tin cả giáo viên và học sinh theo lớp
@app.get("/api/admin/classes/details/{class_id}")
def get_class_details(class_id: int, db: Session = Depends(get_db)):
    # Lấy thông tin lớp học
    classe = db.query(Class).filter(Class.class_id == class_id).first()
    if not classe:
        raise HTTPException(status_code=404, detail="Không tìm thấy class")
    students = db.query(Student).filter(Student.class_id == class_id).all()
    if not students:
        raise HTTPException(status_code=404, detail="Không tìm thấy học sinh cho lớp này")
    distribution = db.query(Distribution).filter(Distribution.class_id == class_id).all()
    if not distribution:
        raise HTTPException(status_code=404, detail="Không tìm thấy giáo viên cho lớp này")
    # Tạo danh sách thông tin đầy đủ học sinh
    student_data = []
    for student in students:
        student_data.append({
            "student_id": student.student_id,
            "name": student.name,
            "gender": student.gender,
            "birth_date": student.birth_date,
            "phone_number": student.phone_number,
            "image": student.image
        })
    # Tạo danh sách thông tin đầy đủ giáo viên
    teacher_data = []
    for dist in distribution:
        teacher = db.query(Teacher).filter(Teacher.teacher_id == dist.teacher_id).first()
        subject = db.query(Subject).filter(Teacher.subject_id == teacher.subject_id).first()
        if teacher:
            teacher_data.append({
                "teacher_id": teacher.teacher_id,
                "name": teacher.name,
                "gender": teacher.gender,
                "birth_date": teacher.birth_date,
                "email": teacher.email,
                "name_subject": subject.name_subject,
                "phone_number": teacher.phone_number,
            })

    return {
        "class_id": classe.class_id,
        "name_class": classe.name_class,
        "teachers": teacher_data,
        "students": student_data
    }
# API thêm tài khoản học sinh mới
@app.post("/api/admin/create/students")
def create_student(
    student_data: StudentCreate,  # Nhận dữ liệu từ body
    db: Session = Depends(get_db)
):
    # Kiểm tra xem class_id có tồn tại không
    class_info = db.query(Class).filter(Class.class_id == student_data.class_id).first()
    if not class_info:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")
    
    # Kiểm tra student_id đã tồn tại chưa
    existing_student = db.query(Student).filter(Student.student_id == student_data.student_id).first()
    if existing_student:
        raise HTTPException(status_code=400, detail="Mã học sinh đã tồn tại")
    
    # Tạo mới một học sinh
    new_student = Student(
        student_id=student_data.student_id,
        name=student_data.name,
        gender=student_data.gender,
        birth_date=student_data.birth_date,
        email=student_data.email,
        phone_number=student_data.phone_number,
        class_id=student_data.class_id,
        password=student_data.password,  # Bạn có thể băm mật khẩu tại đây
        image='https://cdn.glitch.global/83bcea06-7c19-41ce-bb52-ae99ba3f0bd0/JaZBMzV14fzRI4vBWG8jymplSUGSGgimkqtJakOV.jpeg?vUB=1728536441877',
        first_login=True
    )
    
    try:
        db.add(new_student)
        db.commit()  # Lưu thông tin học sinh mới
        db.refresh(new_student)  # Làm mới đối tượng học sinh để có thông tin cập nhật
    except IntegrityError:
        db.rollback()  # Rollback nếu có lỗi trùng lặp
        raise HTTPException(status_code=400, detail="Duplicate entry for student_id")
    
    # Sau khi tạo xong sinh viên, bạn có thể thêm logic khác nếu cần
    
    return {
        "message": "Tạo tài khoản học sinh thành công",
        "student_id": new_student.student_id
    }
#API sửa thông tin học sinh
@app.put("/api/admin/update/student/{student_id}")
def update_student(
    student_id: str,
    name: str = None,
    gender: str = None,
    birth_date: datetime = None,
    email: str = None,
    phone_number: str = None,
    class_id: int = None,
    password: str = None,
    db: Session = Depends(get_db)
):
    # Tìm học sinh cần cập nhật
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Học sinh không tồn tại")

    # Cập nhật thông tin học sinh
    if name:
        student.name = name
    if gender:
        student.gender = gender
    if birth_date:
        student.birth_date = birth_date
    if email:
        student.email = email
    if phone_number:
        student.phone_number = phone_number
    if class_id:
        # Kiểm tra xem lớp học có tồn tại không
        class_info = db.query(Class).filter(Class.class_id == class_id).first()
        if not class_info:
            raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")
        # Cập nhật class_id và cập nhật số học sinh của lớp cũ và lớp mới
        old_class_id = student.class_id
        student.class_id = class_id
        update_total_students(old_class_id, db)
        update_total_students(class_id, db)
    if password:
        student.password = password  # Có thể băm mật khẩu nếu cần

    # Lưu thay đổi vào cơ sở dữ liệu
    db.commit()
    db.refresh(student)

    return {
        "message": "Cập nhật tài khoản học sinh thành công",
        "student_id": student.student_id
    }
# API tìm kiếm học sinh với phân trang
@app.get("/api/admin/students/search", response_model=Page[dict])
def search_students(name: str, db: Session = Depends(get_db), params: Params = Depends()):
    students = db.query(Student).filter(Student.name.ilike(f"%{name}%")).all()
    
    if not students:
        raise HTTPException(status_code=404, detail="Không tìm thấy học sinh nào")
    
    # Lấy thông tin học sinh và lớp
    student_data = []
    for student in students:
        classe = db.query(Class).filter(Class.class_id == student.class_id).first()
        
        student_info = {
            "student_id": student.student_id,
            "name": student.name,
            "birth_date": student.birth_date,
            "phone_number": student.phone_number,
            "name_class": classe.name_class if classe else "Không rõ",
            "gender": student.gender
        }
        student_data.append(student_info)
    
    # Trả về kết quả phân trang
    return paginate(student_data, params)
# API thêm tài khoản giáo viên mới
router = APIRouter()


@app.post("/api/admin/create/teachers")
def create_teacher(
    teacher_data: TeacherCreate,  # Receive request body as JSON
    db: Session = Depends(get_db)
):
    # Check if subject_id exists
    subject = db.query(Subject).filter(Subject.subject_id == teacher_data.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Không tìm thấy môn học")
    
    # Check if teacher_id already exists
    existing_teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_data.teacher_id).first()
    if existing_teacher:
        raise HTTPException(status_code=400, detail="Mã giáo viên đã tồn tại")
    
    # Create new teacher
    new_teacher = Teacher(
        teacher_id=teacher_data.teacher_id,
        name=teacher_data.name,
        gender=teacher_data.gender,
        birth_date=teacher_data.birth_date,
        email=teacher_data.email,
        phone_number=teacher_data.phone_number,
        subject_id=teacher_data.subject_id,
        password=teacher_data.password,
        image='https://cdn.glitch.global/83bcea06-7c19-41ce-bb52-ae99ba3f0bd0/JaZBMzV14fzRI4vBWG8jymplSUGSGgimkqtJakOV.jpeg?vUB=1728536441877'
    )
    
    try:
        db.add(new_teacher)
        db.commit()  # Commit to save the teacher
        db.refresh(new_teacher)  # Refresh the instance to get updated info
    except IntegrityError:
        db.rollback()  # Rollback the transaction in case of error
        raise HTTPException(status_code=400, detail="Duplicate entry for teacher_id")
    
    # Assign the teacher to classes (second part)
    for class_id in teacher_data.class_ids:
        _class = db.query(Class).filter(Class.class_id == class_id).first()
        if not _class:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy lớp với ID {class_id}")
        
        new_distribution = Distribution(
            class_id=class_id,
            teacher_id=new_teacher.teacher_id  # Use the saved teacher_id
        )
        db.add(new_distribution)
    
    db.commit()  # Commit to save the class assignments
    
    return {
        "message": "Tạo tài khoản giáo viên và phân công lớp thành công",
        "teacher_id": new_teacher.teacher_id
    }
#API sửa thông tin giáo viên
@app.put("/api/admin/update/teacher/{teacher_id}")
def update_teacher(
    teacher_id: str,
    name: str = None,
    gender: str = None,
    birth_date: datetime = None,
    email: str = None,
    phone_number: str = None,
    subject_id: int = None,
    password: str = None,
    class_ids: List[int] = None,  # Cập nhật phân công lớp học
    db: Session = Depends(get_db)
):
    # Tìm giáo viên cần cập nhật
    teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Giáo viên không tồn tại")

    # Cập nhật thông tin giáo viên
    if name:
        teacher.name = name
    if gender:
        teacher.gender = gender
    if birth_date:
        teacher.birth_date = birth_date
    if email:
        teacher.email = email
    if phone_number:
        teacher.phone_number = phone_number
    if subject_id:
        subject = db.query(Subject).filter(Subject.subject_id == subject_id).first()
        if not subject:
            raise HTTPException(status_code=404, detail="Không tìm thấy môn học")
        teacher.subject_id = subject_id
    if password:
        teacher.password = password  # Có thể băm mật khẩu nếu cần

    # Cập nhật danh sách lớp phân công nếu có
    if class_ids is not None:
        # Xóa các phân công lớp hiện tại
        db.query(Distribution).filter(Distribution.teacher_id == teacher_id).delete()
        for class_id in class_ids:
            _class = db.query(Class).filter(Class.class_id == class_id).first()
            if not _class:
                raise HTTPException(status_code=404, detail=f"Không tìm thấy lớp với ID {class_id}")
            new_distribution = Distribution(
                class_id=class_id,
                teacher_id=teacher_id
            )
            db.add(new_distribution)

    # Lưu thay đổi vào cơ sở dữ liệu
    db.commit()
    db.refresh(teacher)

    return {
        "message": "Cập nhật tài khoản giáo viên thành công",
        "teacher_id": teacher.teacher_id
    }
# API tìm kiếm theo tên giáo viên
@app.get("/api/admin/teachers/search", response_model=Page[dict])
def search_teachers(name: str, db: Session = Depends(get_db), params: Params = Depends()):
    query = db.query(Teacher).filter(Teacher.name.ilike(f"%{name}%"))
    
    # Lấy tổng số lượng giáo viên để phân trang
    teachers = query.offset((params.page - 1) * params.size).limit(params.size).all()

    if not teachers:
        raise HTTPException(status_code=404, detail="Không tìm thấy giáo viên nào")
    
    teacher_data = []
    for teacher in teachers:
        subject = db.query(Subject).filter(Subject.subject_id == teacher.subject_id).first()
        distributions = db.query(Distribution).filter(Distribution.teacher_id == teacher.teacher_id).all()

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
    
    # Trả về dữ liệu đã phân trang
    return paginate(teacher_data, params)

#Api lấy class theo khối
@app.get("/api/admin/grades/classes")
def get_all_grades_and_classes(db: Session = Depends(get_db)):
    # Query all grades
    grades = db.query(Grades).all()
    if not grades:
        raise HTTPException(status_code=404, detail="Không tìm thấy khối nào")
    grades_data = []
    # Loop through each grade and find the classes associated with it
    for grade in grades:
        classes = db.query(Class).filter(Class.id_grades == grade.id_grades).all()
        # Prepare class details for each grade
        class_data = []
        for classe in classes:
            class_data.append({
                "class_id": classe.class_id,
                "name_class": classe.name_class,
                "total_student": classe.total_student
            })
        # Prepare grade details along with associated classes
        grades_data.append({
            "grade_id": grade.id_grades,
            "grade_name": grade.name_grades,
            "classes": class_data
        })
    # Return the complete data structure
    return {
        "grades": grades_data
    }
