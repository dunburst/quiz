import os
from dotenv import load_dotenv

load_dotenv()  # Tải các biến môi trường từ file .env

SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30