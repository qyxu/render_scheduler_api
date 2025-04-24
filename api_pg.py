
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Job, Schedule
from schemas import JobCreate, JobOut, ScheduleCreate, ScheduleOut
from datetime import datetime
import os
DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Job Shop Scheduler API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/jobs", response_model=JobOut)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    db_job = Job(**job.dict())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

@app.get("/jobs", response_model=list[JobOut])
def get_jobs(db: Session = Depends(get_db)):
    return db.query(Job).all()

@app.post("/schedule", response_model=ScheduleOut)
def create_schedule(schedule: ScheduleCreate, db: Session = Depends(get_db)):
    db_schedule = Schedule(**schedule.dict(), created_at=datetime.utcnow())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

@app.get("/schedule", response_model=list[ScheduleOut])
def get_schedule(db: Session = Depends(get_db)):
    return db.query(Schedule).all()
