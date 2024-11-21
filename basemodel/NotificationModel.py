from typing import List, Optional, Union
from pydantic import BaseModel
from database import get_db
from datetime import datetime

class NotificationResponse(BaseModel):
    noti_id: str
    context: str
    time: datetime
    teacher_id: Optional[str] = None
    student_id: Optional[str] = None