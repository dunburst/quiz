

@app.post("/api/teacher/create/quiz/question")
def create_quiz_with_questions(
    quiz_data: QuizCreate,
    db: Session = Depends(get_db)
):
    # Check if the teacher exists
    teacher_info = db.query(Teacher).filter(Teacher.teacher_id == quiz_data.teacher_id).first()
    if not teacher_info:
        raise HTTPException(status_code=404, detail="Teacher not found")

    # Create a new quiz
    new_quiz = Quiz(
        title=quiz_data.title,
        due_date=quiz_data.due_date,
        time_limit=quiz_data.time_limit,
        question_count=len(quiz_data.questions),
        teacher_id=quiz_data.teacher_id
    )
    
    db.add(new_quiz)
    db.commit()
    db.refresh(new_quiz)

    # Add questions and answers
    for question_data in quiz_data.questions:
        new_question = Questions(
            quiz_id=new_quiz.quiz_id,
            question_text=question_data.question_text
        )
        db.add(new_question)
        db.commit()
        db.refresh(new_question)
        
        # Add answers for the question
        correct_answers = [ans for ans in question_data.answers if ans.is_correct]
        if len(correct_answers) != 1:
            raise HTTPException(status_code=400, detail="Each question must have exactly one correct answer.")
        
        for answer_data in question_data.answers:
            new_answer = Answer(
                question_id=new_question.question_id,
                answer=answer_data.answer,
                is_correct=answer_data.is_correct
            )
            db.add(new_answer)
        
        db.commit()

    return {
        "message": "Quiz created successfully",
        "quiz_id": new_quiz.quiz_id
    }