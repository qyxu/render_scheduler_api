from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class JobCreate(BaseModel):
    job_id: str
    duration: int
    due_date: int
    machine_required: str
    skill_required: str

class JobOut(JobCreate):
    id: int
    class Config:
        orm_mode = True

class ScheduleCreate(BaseModel):
    job_id: str
    start: int
    end: int

class ScheduleOut(ScheduleCreate):
    id: int
    created_at: Optional[datetime]
    class Config:
        orm_mode = True
