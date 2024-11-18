from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.sql import func, case
from pydantic import BaseModel
from datetime import datetime

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
    question_count: int
    class_assignments: List[ClassAssignment]  
    
class AnswerUpdate(BaseModel):
    answer_id: str
    answer: str
    is_correct: bool
    
class QuestionUpdate(BaseModel):
    question_id: str
    question_text: str
    answers: List[AnswerUpdate]
    
class UpdateQuestion(BaseModel):
    question: List[QuestionUpdate]
    
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
    questions: List[QuestionResponse]
    
class AnswerSubmission(BaseModel):
    question_id: str
    answer_id: str

class QuizSubmission(BaseModel):
    quiz_id: str  # Thêm quiz_id vào lớp QuizSubmission
    answers: List[AnswerSubmission]
    
class QuestionReview(BaseModel):
    question_id: str
    question_text: str
    student_answer: Optional[str]  # Answer text or None if not answered
    correct_answer: str
    correct: bool  
    
class QuizReviewResponse(BaseModel):
    quiz_id: str
    title: str
    score: float
    questions: List[QuestionReview]
    
class QuizDetailResponse1(BaseModel):
    quiz_id: str
    title: str
    time_limit: int
    questions: List[QuestionResponse]
    
class QuizSummaryResponse(BaseModel):
    quiz_id: str
    title: str
    students_with_scores: int
    due_date: datetime
    total_student: int
    average_score: float
    status: str 