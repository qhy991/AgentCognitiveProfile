#!/usr/bin/env python3
"""Run the CLAUDE.md personality experiment with Claude Code headless mode.

For every (task x variant x repetition) cell this script:
  1. copies the task's workspace into results/runs/<run_id>/workspace/
  2. writes the personality variant into that workspace as CLAUDE.md
  3. runs `claude -p <task prompt>` there (headless, stream-json output)
  4. grades the result against the task's hidden tests
  5. extracts behavior metrics from the transcript
  6. writes results/runs/<run_id>/record.json

Runs already holding a record.json are skipped, so the script is safe to
interrupt and re-run. Run order is shuffled (fixed seed) so no variant
systematically runs earlier than another.

Examples:
    # smoke test: 2 tasks, 2 variants, 1 rep
    python scripts/run_experiment.py --tasks t01_date_range,t07_log_summary \
        --variants control,intj_behavior --reps 1

    # full MVP (10 tasks x 5 variants x 3 reps = 150 runs)
    python scripts/run_experiment.py --reps 3 --parallel 2 --model haiku
"""
import argparse
import json
import os
import random
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from behavior_metrics import extract_metrics  # noqa: E402
from grade import grade_run  # noqa: E402
from grade_multi import grade_multi  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ALLOWED_TOOLS = "Bash,Read,Write,Edit,MultiEdit,Glob,Grep,LS,TodoWrite"


def parse_result_line(transcript):
    try:
        lines = Path(transcript).read_text(
            encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return {}
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "result":
            return ev
    return {}


def run_one(task_dir, variant_path, rep, args):
    task = task_dir.name
    variant = variant_path.stem
    run_id = f"{task}__{variant}__r{rep}"
    run_dir = ROOT / "results" / "runs" / run_id
    record_path = run_dir / "record.json"
    if record_path.exists() and not args.force:
        return run_id, "already done, skipped"

    ws = run_dir / "workspace"
    if ws.exists():
        shutil.rmtree(ws)
    run_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(task_dir / "workspace", ws)
    (ws / args.memory_filename).write_text(
        variant_path.read_text(encoding="utf-8"), encoding="utf-8")

    prompt = (task_dir / "prompt.txt").read_text(encoding="utf-8")
    cmd = [
        args.claude_bin, "-p", prompt,
        "--output-format", "stream-json", "--verbose",
        "--max-turns", str(args.max_turns),
    ]
    if args.model:
        cmd += ["--model", args.model]
    if args.yolo:
        cmd += ["--dangerously-skip-permissions"]
    else:
        cmd += ["--allowedTools", ALLOWED_TOOLS]

    transcript = run_dir / "transcript.jsonl"
    timed_out = False
    exit_code = None
    t0 = time.time()
    with open(transcript, "w") as out, open(run_dir / "stderr.log", "w") as err:
        try:
            proc = subprocess.run(cmd, cwd=str(ws), stdout=out, stderr=err,
                                  stdin=subprocess.DEVNULL,
                                  timeout=args.timeout)
            exit_code = proc.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
        except FileNotFoundError:
            raise SystemExit(
                f"error: `{args.claude_bin}` not found. Install Claude Code "
                "and log in first (npm install -g @anthropic-ai/claude-code).")
    wall_s = round(time.time() - t0, 1)

    result_ev = parse_result_line(transcript)
    meta = json.loads((task_dir / "meta.json").read_text())

    # Use multi-dimension grading if task specifies it
    if meta.get("grading") == "multi":
        scores = grade_multi(ws, task_dir)
        hidden_frac = scores["overall"]
        hidden_passed = -1  # multi-dimension doesn't have pass/fail counts
        hidden_total = -1
    else:
        scores = grade_run(ws, task_dir)
        hidden_frac = scores["hidden"]["frac"]
        hidden_passed = scores["hidden"]["passed"]
        hidden_total = scores["hidden"]["total"]

    behavior = extract_metrics(transcript)

    record = {
        "run_id": run_id,
        "task": task,
        "task_type": meta.get("type"),
        "variant": variant,
        "rep": rep,
        "model": behavior.get("model") or args.model,
        "hidden_frac": hidden_frac,
        "hidden_passed": hidden_passed,
        "hidden_total": hidden_total,
        "visible_frac": (scores.get("visible") or {}).get("frac") if isinstance(scores, dict) and "visible" in scores else None,
        "timed_out": timed_out,
        "agent_exit_code": exit_code,
        "agent_is_error": result_ev.get("is_error"),
        "num_turns": result_ev.get("num_turns"),
        "total_cost_usd": result_ev.get("total_cost_usd"),
        "duration_ms": result_ev.get("duration_ms"),
        "wall_s": wall_s,
        "behavior": behavior,
    }
    # Add multi-dimension scores if available
    if isinstance(scores, dict) and "correctness" in scores:
        record["multi_scores"] = {
            "correctness": scores["correctness"],
            "performance": scores["performance"],
            "minimality": scores["minimality"],
            "quality": scores["quality"],
            "overall": scores["overall"],
        }
    record_path.write_text(json.dumps(record, indent=2))
    return run_id, (f"hidden={record['hidden_frac']:.2f} "
                    f"turns={record['num_turns']} timeout={timed_out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tasks", help="comma-separated task ids (default: all)")
    ap.add_argument("--variants", help="comma-separated variant names (default: all)")
    ap.add_argument("--reps", type=int, default=3, help="repetitions per cell (default 3)")
    ap.add_argument("--model", default=None,
                    help="passed to `claude --model` (e.g. haiku, sonnet, or a full model id); "
                         "default: your Claude Code default model")
    ap.add_argument("--parallel", type=int, default=2,
                    help="concurrent claude processes (default 2; raise carefully, rate limits)")
    ap.add_argument("--max-turns", type=int, default=50)
    ap.add_argument("--timeout", type=int, default=900,
                    help="wall-clock seconds per run (default 900)")
    ap.add_argument("--memory-filename", default="CLAUDE.md",
                    help="filename the variant is written as (default CLAUDE.md; "
                         "use AGENTS.md for harnesses that read that instead)")
    ap.add_argument("--claude-bin", default="claude")
    ap.add_argument("--yolo", action="store_true",
                    help="use --dangerously-skip-permissions instead of an allowlist "
                         "(only inside a container/VM you trust)")
    ap.add_argument("--force", action="store_true", help="re-run cells that already have records")
    args = ap.parse_args()

    all_tasks = sorted(p for p in (ROOT / "tasks").iterdir() if (p / "meta.json").exists())
    all_variants = sorted((ROOT / "variants").glob("*.md"))
    tasks = [p for p in all_tasks
             if not args.tasks or p.name in args.tasks.split(",")]
    variants = [p for p in all_variants
                if not args.variants or p.stem in args.variants.split(",")]
    if not tasks or not variants:
        raise SystemExit("no tasks or variants matched the filters")

    cells = [(t, v, r) for t in tasks for v in variants
             for r in range(1, args.reps + 1)]
    random.Random(0).shuffle(cells)
    print(f"{len(tasks)} tasks x {len(variants)} variants x {args.reps} reps "
          f"= {len(cells)} runs (parallel={args.parallel})")

    done = 0
    t_start = time.time()
    with ThreadPoolExecutor(max_workers=args.parallel) as pool:
        futures = {pool.submit(run_one, t, v, r, args): (t.name, v.stem, r)
                   for t, v, r in cells}
        for fut in as_completed(futures):
            done += 1
            try:
                run_id, note = fut.result()
            except SystemExit:
                raise
            except Exception as e:  # keep the batch alive on one bad run
                run_id, note = "__".join(map(str, futures[fut])), f"ERROR {e}"
            print(f"[{done}/{len(cells)} {time.time() - t_start:6.0f}s] {run_id}: {note}",
                  flush=True)
    print("done. Next: python scripts/analyze.py")


if __name__ == "__main__":
    main()
