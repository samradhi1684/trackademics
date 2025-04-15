from pydantic import BaseModel
from datetime import datetime

class Exam(BaseModel):
    title: str
    subject: str
    date: datetime
    description: str
    status: str
    type: str

class Submission(BaseModel):
    title: str
    subject: str
    deadline: datetime
    description: str
    status: str  # e.g., "pending", "done"
