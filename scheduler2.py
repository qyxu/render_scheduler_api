from ortools.sat.python import cp_model

def run_scheduler_v2(jobs):
    model = cp_model.CpModel()
    max_time = 50
    jobs = sorted(jobs, key=lambda x: x.duration)  # prioritize short jobs
    job_vars = {}

    for i, job in enumerate(jobs):
        start = model.NewIntVar(0, max_time, f"start_{job.job_id}")
        end = model.NewIntVar(0, max_time, f"end_{job.job_id}")
        interval = model.NewIntervalVar(start, job.duration, end, f"interval_{job.job_id}")
        job_vars[job.job_id] = {"start": start, "end": end, "interval": interval, "machine": job.machine_required}

    machines = {}
    for job_id, data in job_vars.items():
        machines.setdefault(data["machine"], []).append(data["interval"])
    for intervals in machines.values():
        model.AddNoOverlap(intervals)

    model.Minimize(sum(v["end"] for v in job_vars.values()))
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        return [{"job_id": jid, "start": solver.Value(v["start"]), "end": solver.Value(v["end"]), "version": "v2"} for jid, v in job_vars.items()]
    return []
