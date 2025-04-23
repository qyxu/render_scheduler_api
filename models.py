
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, unique=True)
    duration = Column(Integer)
    due_date = Column(Integer)
    machine_required = Column(String)
    skill_required = Column(String)

class Schedule(Base):
    __tablename__ = 'schedules'

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String)
    start = Column(Integer)
    end = Column(Integer)
    created_at = Column(DateTime)
