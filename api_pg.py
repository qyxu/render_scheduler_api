
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from models import Job, Schedule, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/jobs")
def get_jobs(db: Session = Depends(get_db)):
    return db.query(Job).all()

@app.post("/jobs")
def create_job(job: Job, db: Session = Depends(get_db)):
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@app.get("/schedule")
def get_schedule(db: Session = Depends(get_db)):
    return db.query(Schedule).all()

@app.post("/schedule")
def create_schedule_entry(schedule: Schedule, db: Session = Depends(get_db)):
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule

from scheduler import run_scheduler  # this should contain run_scheduler(output_json=True)

@app.post("/run-scheduler")
def run_scheduler_endpoint(db: Session = Depends(get_db)):
    schedule = run_scheduler(output_json=True)
    if not schedule:
        raise HTTPException(status_code=400, detail="No schedule generated")

    db.query(Schedule).delete()  # Clear previous
    for entry in schedule:
        new_sched = Schedule(
            job_id=entry["job_id"],
            start=entry["start"],
            end=entry["end"],
            created_at=datetime.utcnow()
        )
        db.add(new_sched)
    db.commit()
    return {"status": "success", "jobs_scheduled": len(schedule)}
