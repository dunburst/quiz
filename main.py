import uuid
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from passlib.context import CryptContext

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Cơ sở dữ liệu mẫu về người dùng với ID
fake_users_db = {
    "first_user": {
        "id": "HS001",
        "hashed_password": pwd_context.hash("password1"),
        "name": "Khoa",
        "years": "12",
        "gender": "female",
        "is_first_login": True
    }
}

# Mô hình dữ liệu Pydantic cho đăng nhập
class User(BaseModel):
    id: str
    password: str
# Mô hình dữ liệu Pydantic cho đổi mật khẩu
class ChangePassword(BaseModel):
    id: str
    old_password: str
    new_password: str
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
def get_password_hash(password):
    return pwd_context.hash(password)
@app.post("/login")
def login(user: User):
    user_db = fake_users_db.get(user.id)
    if not user_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Người dùng không tồn tại")
    
    if not verify_password(user.password, user_db["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sai mật khẩu")
    
    # Kiểm tra nếu is_first_login == True, chỉ trả về id
    if user_db["is_first_login"]:
        return {"id": user_db["id"]}

    # Nếu is_first_login == False, trả về thông tin người dùng đầy đủ
    return {
        "id": user_db["id"],
        "name": user_db["name"],
        "years": user_db["years"],
        "gender": user_db["gender"],
        "is_first_login": user_db["is_first_login"]
    }
# API Đổi mật khẩu cho lần đầu đăng nhập
@app.post("/change-password")
def change_password(data: ChangePassword):
    user_db = fake_users_db.get(data.id)
    if not user_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Người dùng không tồn tại")
    
    if not verify_password(data.old_password, user_db["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sai mật khẩu cũ")
    
    if not user_db["is_first_login"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Người dùng không cần đổi mật khẩu")
    # Cập nhật mật khẩu mới
    user_db["hashed_password"] = get_password_hash(data.new_password)
    user_db["is_first_login"] = False  # Đánh dấu người dùng đã hoàn thành đổi mật khẩu

    return {"message": "Đổi mật khẩu thành công", "id": user_db["id"]}