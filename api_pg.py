
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from models import Job, Schedule, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://scheduler:scheduler@db:5432/scheduler"
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
