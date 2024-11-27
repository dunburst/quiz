from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

#Class create
class AnswerCreate(BaseModel):
    answer: str
    is_correct: bool
class QuestionCreate(BaseModel):
    question_id: Optional[str] = None
    question_text: str
    answers: List[AnswerCreate]
class ClassAssignment(BaseModel):
    class_id: Optional[int] = None 
class QuizWithQuestionsCreate(BaseModel):
    title: str
    due_date: datetime
    time_limit: int
    class_assignments: List[ClassAssignment]
    questions: List[QuestionCreate]

#Class update
class AnswerUpdate(BaseModel):
    answer_id: Optional[str] = None
    answer: Optional[str] = None
    is_correct: Optional[bool] = None
class QuestionUpdate(BaseModel):
    question_id: Optional[str] = None
    question_text: Optional[str] = None
    answers: List[AnswerUpdate]
class UpdateQuizAndQuestions(BaseModel):
    title: Optional[str]
    time_limit: Optional[int]
    due_date: Optional[datetime]
    class_assignments: List[ClassAssignment]
    questions: List[QuestionUpdate]

# Các mô hình dữ liệu
class AnswerResponse(BaseModel):
    answer_id: str
    answer: str
    is_correct: bool
class QuestionResponse(BaseModel):
    question_id: str
    question_text: str
    answers: List[AnswerResponse]
class QuizDetailResponse(BaseModel):
    quiz_id: str
    title: str
    time_limit: int
    due_date: Optional[datetime]
    question_count: int
    class_assignments: List[ClassAssignment]
    questions: List[QuestionResponse]


# Chọn đáp án
class AnswerSubmission(BaseModel):
    question_id: str
    answer_id: str
class QuizSubmission(BaseModel):
    quiz_id: str  
    answers: List[AnswerSubmission]

#Xem lại câu trả lời
class QuestionReview(BaseModel):
    question_id: str
    question_text: str
    student_answer: Optional[str]  
    correct_answer: str
    correct: bool  
class QuizReviewResponse(BaseModel):
    quiz_id: str
    title: str
    score: float
    questions: List[QuestionReview]

#Chi tiết quiz cho student
class AnswerResponse1(BaseModel):
    answer_id: str
    answer: str
class QuestionResponse1(BaseModel):
    question_id: str
    question_text: str
    answers: List[AnswerResponse1]
class QuizDetailResponse1(BaseModel):
    quiz_id: str
    title: str
    time_limit: int
    due_date: datetime
    questions: List[QuestionResponse1]

#Xem điểm của học sinh
class QuizSummaryResponse(BaseModel):
    quiz_id: str
    title: str
    students_with_scores: int
    due_date: datetime
    total_student: int
    average_score: float
    status: str 

class QuizRequest(BaseModel):
    quiz_id: str