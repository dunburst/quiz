from typing import List, Optional, Dict, Union
from pydantic import BaseModel
import uuid
from datetime import datetime


class NotificationResponse(BaseModel):
    noti_id: str
    context: str
    time: datetime
    teacher_id: Optional[str] = None
    student_id: Optional[str] = None