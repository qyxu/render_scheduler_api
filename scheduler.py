
import pandas as pd
from ortools.sat.python import cp_model
from jobboss_data import load_jobs_from_jobboss
from visualizer import draw_gantt_chart

def run_scheduler(output_json=False):
    jobs = load_jobs_from_jobboss()
    model = cp_model.CpModel()
    max_time = 50

    starts, ends, intervals = [], [], []
    job_vars = {}
    machine_to_intervals = {}

    for i, job in jobs.iterrows():
        start = model.NewIntVar(0, max_time, f'start_{i}')
        end = model.NewIntVar(0, max_time, f'end_{i}')
        interval = model.NewIntervalVar(start, job["duration"], end, f'interval_{i}')
        starts.append(start)
        ends.append(end)
        intervals.append(interval)
        job_vars[job["job_id"]] = {"start": start, "end": end, "interval": interval}
        machine_to_intervals.setdefault(job["machine_required"], []).append(interval)

    # Enforce no-overlap per machine
    for intervals in machine_to_intervals.values():
        model.AddNoOverlap(intervals)

    # Add job dependency (simulate: job 1 must finish before job 3)
    if len(jobs) >= 4:
        model.Add(starts[3] >= ends[1])  # Job 3 starts after Job 1 ends

    # Add setup/changeover penalty between jobs on same machine
    setup_costs = []
    setup_penalty = 1  # 1 time unit cost for material change
    for i in range(len(jobs)):
        for j in range(i + 1, len(jobs)):
            if jobs.loc[i, "machine_required"] == jobs.loc[j, "machine_required"]:
                if jobs.loc[i, "skill_required"] != jobs.loc[j, "skill_required"]:
                    t = model.NewBoolVar(f"setup_trigger_{i}_{j}")
                    model.Add(starts[j] >= ends[i]).OnlyEnforceIf(t)
                    setup = model.NewIntVar(0, setup_penalty, f"setup_{i}_{j}")
                    model.Add(setup == setup_penalty).OnlyEnforceIf(t)
                    setup_costs.append(setup)

    # Priority handling: higher priority gets lower penalty weight
    lateness_vars = []
    weighted_penalties = []
    for i in range(len(jobs)):
        due = jobs.loc[i, "due_date"]
        priority = jobs.loc[i, "priority"]
        late = model.NewIntVar(0, max_time, f'lateness_{i}')
        model.Add(ends[i] <= due + late)
        lateness_vars.append(late)
        weighted = model.NewIntVar(0, max_time * 10, f'weighted_late_{i}')
        model.AddMultiplicationEquality(weighted, [late, priority])
        weighted_penalties.append(weighted)

    # Objective: weighted tardiness + setup transitions
    model.Minimize(sum(weighted_penalties + setup_costs))

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        result = []
        for i in range(len(jobs)):
            result.append({
                "job_id": jobs.loc[i, "job_id"],
                "start": solver.Value(starts[i]),
                "end": solver.Value(ends[i]),
                "priority": jobs.loc[i, "priority"]
            })
        schedule_df = pd.DataFrame(result)
        print(schedule_df)
        draw_gantt_chart(schedule_df)
        return schedule_df.to_dict(orient="records") if output_json else None
    else:
        print("No solution found.")
        return {"status": "unsolvable"} if output_json else None
