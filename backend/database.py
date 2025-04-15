from typing import List
from uuid import uuid4
from pydantic import BaseModel
from datetime import datetime

# Simulated database (can replace with Firebase or SQLite later)
exams_db: List[dict] = []
submissions_db: List[dict] = []

def generate_id():
    return str(uuid4())
