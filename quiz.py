from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from database import get_db
from models import Teacher, Subject, Admin, Class, Distribution, Quiz, Class_quiz, Questions, Answer, Student, Choice
from auth import hash_password, get_current_user
import uuid
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from fastapi_pagination import Page, Params, paginate
router = APIRouter()
class AnswerCreate(BaseModel):
    answer: str
    is_correct: bool
class QuestionCreate(BaseModel):
    question_text: str
    answers: List[AnswerCreate]
class ClassAssignment(BaseModel):
    class_id: int
class QuizCreate(BaseModel):
    title: str
    due_date: datetime
    time_limit: int
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
@router.get("/api/teachers/quizzes", response_model=Page[dict], tags=["Quizzes"])
def get_teacher_quizzes(
    db: Session = Depends(get_db), 
    params: Params = Depends(),
    current_user: Teacher = Depends(get_current_user)  # Ensure the current user is a teacher
):
    # Ensure the user is a teacher
    if not isinstance(current_user, Teacher):
        raise HTTPException(status_code=403, detail="Access forbidden: Only teachers can view their quizzes")
    # Fetch quizzes assigned to the current teacher
    quizzes = db.query(Quiz).filter(Quiz.teacher_id == current_user.teacher_id).all()
    # Check if there are no quizzes
    if not quizzes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No quizzes found")
    # Prepare a list of quizzes with additional information
    quiz_list = []
    for quiz in quizzes:
        class_quizzes = db.query(Class_quiz).filter(Class_quiz.quiz_id == quiz.quiz_id).all()
        class_ids = [class_quiz.class_id for class_quiz in class_quizzes] if class_quizzes else []
        class_names = db.query(Class.name_class).filter(Class.class_id.in_(class_ids)).all()
        class_names_list = [class_name[0] for class_name in class_names]  # Convert from tuple to list
        quiz_info = {
            "quiz_id": quiz.quiz_id,
            "title": quiz.title,
            "due_date": quiz.due_date,
            "time_limit": quiz.time_limit,
            "question_count": quiz.question_count,
            "class_ids": class_names_list 
        }
        quiz_list.append(quiz_info)
    # Return paginated quiz list
    return paginate(quiz_list, params)
#API create quiz
@router.post("/api/post/quizzes", tags=["Quizzes"])
def create_quiz(
    quiz_data: QuizCreate, 
    db: Session = Depends(get_db), 
    current_user: Teacher = Depends(get_current_user)
):
    if not isinstance(current_user, Teacher):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only teachers can create quizzes.")
    new_quiz = Quiz(
        title=quiz_data.title,
        due_date=quiz_data.due_date,
        time_limit=quiz_data.time_limit,
        question_count=0,  
        teacher_id=current_user.teacher_id
    )
    db.add(new_quiz)
    db.commit()
    db.refresh(new_quiz)
    for assignment in quiz_data.class_assignments:
        class_obj = db.query(Class).filter(Class.class_id == assignment.class_id).first()
        if not class_obj:
            raise HTTPException(status_code=404, detail=f"Class with ID {assignment.class_id} does not exist")
        new_class_quiz = Class_quiz(
            class_quiz_id=str(uuid.uuid4()), 
            class_id=assignment.class_id,
            quiz_id=new_quiz.quiz_id
        )
        db.add(new_class_quiz)
    db.commit() 
    return {
        "message": "Quiz created and assigned to classes successfully",
        "quiz_id": new_quiz.quiz_id
    }
    
# API tạo câu hỏi
@router.post("/api/post/answer/{quiz_id}", tags=["Quizzes"])
def create_questions_for_quiz(
    quiz_id: str, 
    question_data: QuestionCreate, 
    db: Session = Depends(get_db),
    current_user: Teacher = Depends(get_current_user)
):
    quiz_info = db.query(Quiz).filter(
        Quiz.quiz_id == quiz_id,
        Quiz.teacher_id == current_user.teacher_id
    ).first()
    if not quiz_info:
        raise HTTPException(status_code=404, detail="Không tìm thấy quiz hoặc bạn không sở hữu quiz này")
    new_question = Questions(
        quiz_id=quiz_id,
        question_text=question_data.question_text
    )
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    correct_answers = [ans for ans in question_data.answers if ans.is_correct]
    if len(correct_answers) != 1:
        raise HTTPException(status_code=400, detail="Mỗi câu hỏi phải có đúng một câu trả lời chính xác.")
    for answer_data in question_data.answers:
        new_answer = Answer(
            question_id=new_question.question_id,
            answer=answer_data.answer,
            is_correct=answer_data.is_correct
        )
        db.add(new_answer)
    db.commit()
    quiz_info.question_count += 1
    db.commit()
    return {
        "message": "Tạo câu hỏi và câu trả lời thành công",
        "question_id": new_question.question_id
    }
#Update lại
@router.put("/api/put/quizzes/{quiz_id}", tags=["Quizzes"]) 
def update_question_for_quiz(
    quiz_id: str, 
    update_data: UpdateQuestion,  
    db: Session = Depends(get_db),
    current_user: Teacher = Depends(get_current_user)  
):
    quiz = db.query(Quiz).filter(Quiz.quiz_id == quiz_id, Quiz.teacher_id == current_user.teacher_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Không tìm thấy quiz hoặc bạn không sở hữu quiz này")
    for question_data in update_data.question:
        # Tìm câu hỏi tương ứng
        question_info = db.query(Questions).filter(
            Questions.question_id == question_data.question_id, 
            Questions.quiz_id == quiz_id 
        ).first()
        if not question_info:
            raise HTTPException(status_code=404, detail=f"Câu hỏi {question_data.question_id} không tồn tại.")
        question_info.question_text = question_data.question_text
        correct_answers = [ans for ans in question_data.answers if ans.is_correct]
        if len(correct_answers) != 1:
            raise HTTPException(status_code=400, detail=f"Câu hỏi {question_data.question_id} phải có đúng một câu trả lời chính xác.")
        db.query(Answer).filter(Answer.question_id == question_data.question_id).delete()
        new_answers = [
            Answer(
                question_id=question_data.question_id,
                answer=answer_data.answer,
                is_correct=answer_data.is_correct
            )
            for answer_data in question_data.answers
        ]
        db.bulk_save_objects(new_answers)  
        db.commit()  
    return {
        "message": "Cập nhật câu hỏi và câu trả lời thành công"
    }
    
#API lấy thông tin chi tiết về các question
@router.get("/api/quizzes/{quiz_id}", response_model=List[QuestionResponse], tags=["Quizzes"])
def get_questions_for_quiz(
    quiz_id: str, 
    db: Session = Depends(get_db),
    current_user: Teacher = Depends(get_current_user) 
):
    quiz = db.query(Quiz).filter(
        Quiz.quiz_id == quiz_id, 
        Quiz.teacher_id == current_user.teacher_id
    ).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Không tìm thấy quiz hoặc bạn không sở hữu quiz này")
    questions = db.query(Questions).filter(Questions.quiz_id == quiz_id).all()
    if not questions:
        return [] 
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

# Chọn đáp án
class AnswerSubmission(BaseModel):
    question_id: str
    answer_id: str

class QuizSubmission(BaseModel):
    quiz_id: str  # Thêm quiz_id vào lớp QuizSubmission
    answers: List[AnswerSubmission]

@router.post("/api/quiz/submit", tags=["Quizzes"])
def submit_quiz(
    quiz_data: QuizSubmission,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Kiểm tra xem học sinh có đăng ký vào quiz này không
    class_quiz = db.query(Class_quiz).join(Class).filter(
        Class.class_id == current_user.class_id, Class_quiz.quiz_id == quiz_data.quiz_id
    ).first()
    if not class_quiz:
        raise HTTPException(status_code=403, detail="Student not enrolled in this quiz")
    # Lưu đáp án của học sinh
    for answer in quiz_data.answers:
        new_choice = Choice(
            choice_id=str(uuid.uuid4()),
            answer_id=answer.answer_id,
            student_id=current_user.student_id
        )
        db.add(new_choice)

    db.commit()
    # Tính điểm
    correct_answers = db.query(Answer.answer_id).join(Questions).filter(
        Questions.quiz_id == quiz_data.quiz_id, Answer.is_correct == True
    ).all()
    correct_answer_ids = {ans.answer_id for ans in correct_answers}
    student_answer_ids = {answer.answer_id for answer in quiz_data.answers}
    correct_count = len(correct_answer_ids.intersection(student_answer_ids))
    total_questions = db.query(Questions).filter(Questions.quiz_id == quiz_data.quiz_id).count()
    score = (correct_count / total_questions) * 10  
    new_score = Score(
        score_id=str(uuid.uuid4()),
        student_id=current_user.student_id,
        quiz_id=quiz_data.quiz_id,
        time_start=datetime.now(),  
        time_end=datetime.now(),
        status="Completed",
        score=score
    )
    db.add(new_score)
    db.commit()
    return {
        "message": "Quiz submitted successfully",
        "score": score
    }
    
#Xem lại câu trả lời
class QuestionReview(BaseModel):
    question_id: str
    question_text: str
    student_answer: Optional[str]  # Answer text or None if not answered
    correct_answer: str
    is_correct: bool  
class QuizReviewResponse(BaseModel):
    quiz_id: str
    title: str
    score: float
    questions: List[QuestionReview]
@router.get("/api/quiz/{quiz_id}/review", response_model=QuizReviewResponse, tags=["Quizzes"])
def review_quiz(
    quiz_id: str,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Check if the quiz exists
    quiz = db.query(Quiz).filter(Quiz.quiz_id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    # Retrieve the student's score for the quiz
    student_score = db.query(Score).filter(
        Score.student_id == current_user.student_id, Score.quiz_id == quiz_id
    ).first()
    if not student_score:
        raise HTTPException(status_code=403, detail="No record of this quiz for the student")
    # Retrieve all questions for the quiz
    questions = db.query(Questions).filter(Questions.quiz_id == quiz_id).all()
    # Fetch the student's chosen answers
    student_choices = db.query(Choice.answer_id, Answer.question_id).join(Answer).filter(
        Choice.student_id == current_user.student_id,
        Answer.question_id.in_([q.question_id for q in questions])
    ).all()
    student_answer_map = {choice.question_id: choice.answer_id for choice in student_choices}
    # Construct the response with question details and correct answers
    questions_review = []
    for question in questions:
        # Fetch the correct answer for each question
        correct_answer = db.query(Answer).filter(
            Answer.question_id == question.question_id,
            Answer.is_correct == True
        ).first()
        # Fetch student's chosen answer text if they answered the question
        student_answer_id = student_answer_map.get(question.question_id)
        student_answer = db.query(Answer).filter(
            Answer.answer_id == student_answer_id
        ).first() if student_answer_id else None 
        # Check if the student's answer was correct
        is_correct = student_answer_id == correct_answer.answer_id if student_answer else False
        questions_review.append(QuestionReview(
            question_id=question.question_id,
            question_text=question.question_text,
            student_answer=student_answer.answer if student_answer else None,
            correct_answer=correct_answer.answer,
            is_correct=is_correct
        ))
    # Return the review data
    return QuizReviewResponse(
        quiz_id=quiz.quiz_id,
        title=quiz.title,
        score=student_score.score,
        questions=questions_review
    )