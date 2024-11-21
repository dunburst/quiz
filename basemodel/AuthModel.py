from datetime import datetime, timedelta
from pydantic import BaseModel
from passlib.context import CryptContext
import os
from typing import Optional, Union

class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[str] = None 

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    first_login: Optional[bool] = None 
    image: Optional[str] = None 

class ChangeRespone(BaseModel):
    new_password: str
    confirm_password: str