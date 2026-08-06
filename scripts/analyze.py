#!/usr/bin/env python3
"""Analyze experiment records: manipulation check first, outcomes second.

Reads results/runs/*/record.json, prints tables, and writes
results/report.md. Analysis logic:

- Every (variant, task) cell is averaged over its repetitions first.
- Outcome comparisons vs control are PAIRED per task (delta on the same
  task), summarized with a bootstrap 95% CI over tasks (seed fixed).
- Behavior metrics answer the manipulation check: did the variant change
  HOW the agent worked at all? If these do not separate, outcome
  differences are noise - strengthen the manipulation before scaling up.
"""
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTROL = "control"
N_BOOT = 10000

BEHAVIOR_KEYS = [
    ("narration_chars", "narration chars"),
    ("reads_before_first_edit", "reads before 1st edit"),
    ("n_test_runs", "test runs"),
    ("todo_writes", "TodoWrite calls"),
    ("n_tool_calls", "tool calls"),
    ("n_files_touched", "files touched"),
]


def load_records():
    records = []
    for p in sorted((ROOT / "results" / "runs").glob("*/record.json")):
        try:
            records.append(json.loads(p.read_text()))
        except json.JSONDecodeError:
            print(f"warning: unreadable record {p}")
    return records


def mean(xs):
    xs = [x for x in xs if x is not None]
    return statistics.mean(xs) if xs else None


def fmt(x, nd=2):
    return "-" if x is None else f"{x:.{nd}f}"


def cell_means(records, value):
    """{variant: {task: mean over reps}} for a per-record value function."""
    bucket = defaultdict(lambda: defaultdict(list))
    for r in records:
        v = value(r)
        if v is not None:
            bucket[r["variant"]][r["task"]].append(v)
    return {var: {t: statistics.mean(vals) for t, vals in tasks.items()}
            for var, tasks in bucket.items()}


def bootstrap_ci(deltas, n_boot=N_BOOT, seed=0):
    rng = random.Random(seed)
    n = len(deltas)
    means = []
    for _ in range(n_boot):
        sample = [deltas[rng.randrange(n)] for _ in range(n)]
        means.append(statistics.mean(sample))
    means.sort()
    return means[int(0.025 * n_boot)], means[int(0.975 * n_boot)]


def md_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |",
             "|" + "|".join(["---"] * len(headers)) + "|"]
    lines += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return "\n".join(lines)


def main():
    records = load_records()
    if not records:
        raise SystemExit("no records found - run scripts/run_experiment.py first")

    variants = sorted({r["variant"] for r in records})
    task_type = {r["task"]: r.get("task_type") for r in records}
    n_by_cell = defaultdict(int)
    for r in records:
        n_by_cell[(r["variant"], r["task"])] += 1

    out = ["# AGENTS.md personality experiment - report", ""]
    out.append(f"{len(records)} runs, {len(variants)} variants, "
               f"{len(task_type)} tasks.")
    out.append("")

    # ---------- 1. headline outcomes ----------
    hidden = cell_means(records, lambda r: r["hidden_frac"])
    rows = []
    for var in variants:
        per_task = hidden.get(var, {})
        rs = [r for r in records if r["variant"] == var]
        rows.append([
            var,
            fmt(mean(list(per_task.values()))),
            fmt(mean([m for t, m in per_task.items()
                      if task_type.get(t) == "clear"])),
            fmt(mean([m for t, m in per_task.items()
                      if task_type.get(t) == "vague"])),
            fmt(mean([r["num_turns"] for r in rs]), 1),
            fmt(mean([r["total_cost_usd"] for r in rs]), 4),
            fmt(mean([r["visible_frac"] for r in rs])),
            sum(1 for r in rs if r.get("timed_out")),
            len(rs),
        ])
    out += ["## 1. Outcomes by variant", "",
            md_table(["variant", "hidden frac", "clear tasks", "vague tasks",
                      "turns", "cost $", "visible frac", "timeouts", "runs"],
                     rows), ""]

    # ---------- 2. paired deltas vs control ----------
    out += ["## 2. Paired deltas vs control (bootstrap 95% CI over tasks)", ""]
    if CONTROL not in hidden:
        out.append("(no control runs found - cannot compute paired deltas)")
    else:
        rows = []
        for var in variants:
            if var == CONTROL:
                continue
            shared = sorted(set(hidden[var]) & set(hidden[CONTROL]))
            deltas = [hidden[var][t] - hidden[CONTROL][t] for t in shared]
            if len(deltas) < 2:
                rows.append([var, len(shared), "-", "-", "-"])
                continue
            lo, hi = bootstrap_ci(deltas)
            sig = "yes" if (lo > 0 or hi < 0) else "no"
            rows.append([var, len(shared), f"{statistics.mean(deltas):+.3f}",
                         f"[{lo:+.3f}, {hi:+.3f}]", sig])
        out += [md_table(["variant", "paired tasks", "mean delta",
                          "95% CI", "CI excludes 0?"], rows), "",
                "A CI that excludes 0 with only ~10 tasks is a strong signal; "
                "a CI straddling 0 means the effect (if any) is below this "
                "pilot's detection power - not proof of no effect.", ""]

    # ---------- 3. manipulation check ----------
    out += ["## 3. Manipulation check - did behavior change at all?", ""]
    rows = []
    for var in variants:
        rs = [r["behavior"] for r in records if r["variant"] == var]
        rows.append([var] + [fmt(mean([b.get(k) for b in rs]), 1)
                             for k, _ in BEHAVIOR_KEYS])
    out += [md_table(["variant"] + [label for _, label in BEHAVIOR_KEYS], rows), "",
            "Read this table FIRST. If the behavior columns do not separate "
            "between variants (especially label vs behavior versions), the "
            "personality text did not change how the agent works, and any "
            "outcome differences above are noise.", ""]

    # ---------- 4. incomplete cells ----------
    expected = {(v, t) for v in variants for t in task_type}
    missing = sorted(c for c in expected if n_by_cell.get(c, 0) == 0)
    if missing:
        out += ["## 4. Missing cells", ""]
        out += [f"- {v} x {t}" for v, t in missing]
        out.append("")

    report = "\n".join(out)
    (ROOT / "results" / "report.md").write_text(report)
    print(report)
    print(f"\nreport written to {ROOT / 'results' / 'report.md'}")


if __name__ == "__main__":
    main()
