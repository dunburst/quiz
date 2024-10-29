from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth import router as auth_router
from student import router as student_router
from teacher import router as teacher_router
from classes import router as class_router
from quiz import router as quiz_router
from database import Base, engine
import uvicorn


app = FastAPI()

# Cấu hình CORS
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)
app.include_router(auth_router)
app.include_router(student_router)
app.include_router(teacher_router)
app.include_router(class_router)
app.include_router(quiz_router)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)