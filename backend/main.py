from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import Exam, Submission
from database import exams_db, submissions_db, generate_id

app = FastAPI()

# CORS (for frontend connection)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ Submission Routes ------------------

@app.post("/submission/add")
def add_submission(sub: Submission):
    entry = sub.dict()
    entry["id"] = generate_id()
    submissions_db.append(entry)
    return {"message": "Submission added", "data": entry}

@app.get("/submission/all")
def get_submissions():
    return {"submissions": submissions_db}

@app.delete("/submission/{submission_id}")
def delete_submission(submission_id: str):
    global submissions_db
    submissions_db = [s for s in submissions_db if s["id"] != submission_id]
    return {"message": "Submission deleted"}

# ------------------ Exam Routes ------------------

@app.post("/exam/add")
def add_exam(exam: Exam):
    entry = exam.dict()
    entry["id"] = generate_id()
    exams_db.append(entry)
    return {"message": "Exam added", "data": entry}

@app.get("/exam/all")
def get_exams():
    return {"exams": exams_db}

@app.delete("/exam/{exam_id}")
def delete_exam(exam_id: str):
    global exams_db
    exams_db = [e for e in exams_db if e["id"] != exam_id]
    return {"message": "Exam deleted"}

# ------------------ Health Check ------------------

@app.get("/")
def root():
    return {"message": "Trackademics Backend Running 🚀"}
