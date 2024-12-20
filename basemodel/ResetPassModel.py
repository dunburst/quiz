from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
# Model Pydantic để đặt lại mật khẩu
class ResetPasswordRequest(BaseModel):
    email: str
    reset_code: str
    new_password: str
    confirm_password: str
