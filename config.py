import os
from dotenv import load_dotenv

load_dotenv()  # Tải các biến môi trường từ file .env

SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
AVATAR_UPLOAD_PATH = "C:\\Users\\Hi\\OneDrive\\Tài liệu\\GitHub\\fe_quiz\\public"
imageprofile = "https://cdn.glitch.global/83bcea06-7c19-41ce-bb52-ae99ba3f0bd0/JaZBMzV14fzRI4vBWG8jymplSUGSGgimkqtJakOV.jpeg?vUB=1728536441877"