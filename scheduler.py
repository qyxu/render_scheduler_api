
from sqlalchemy.orm import Session
from models import Job
from ortools.sat.python import cp_model

def run_scheduler_from_db(db: Session):
    jobs = db.query(Job).all()
    if not jobs:
        return []

    model = cp_model.CpModel()
    max_time = 50
    job_vars = {}

    for i, job in enumerate(jobs):
        start = model.NewIntVar(0, max_time, f"start_{job.job_id}")
        end = model.NewIntVar(0, max_time, f"end_{job.job_id}")
        interval = model.NewIntervalVar(start, job.duration, end, f"interval_{job.job_id}")
        job_vars[job.job_id] = {"start": start, "end": end, "interval": interval, "machine": job.machine_required}

    # No-overlap per machine
    machines = {}
    for job_id, data in job_vars.items():
        machines.setdefault(data["machine"], []).append(data["interval"])
    for intervals in machines.values():
        model.AddNoOverlap(intervals)

    # Objective: minimize total end time
    ends = [data["end"] for data in job_vars.values()]
    model.Minimize(sum(ends))

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

   if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        return [
            {
                "job_id": job_id,
                "start": solver.Value(data["start"]),
                "end": solver.Value(data["end"]),
                "version": "v1"
            }
            for job_id, data in job_vars.items()
        ]
    return []
