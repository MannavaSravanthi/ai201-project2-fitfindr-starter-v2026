"""
Capstone test runner.

    python run_capstone.py --cost              10 normal runs → what one run costs
    python run_capstone.py --label before      the 20 labelled queries × 3 trials,
                                               scored against the 5 criteria in criteria.md
    python run_capstone.py --label after       same, after the improvement

The cache is turned OFF, so every trial is a real model call. Each trial writes
its own log (logs/capstone_<label>_trial<N>.jsonl), and the scores are computed
FROM those logs — the log is the evidence, this script just counts it.

This runs FitFindr; it doesn't change it.
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

os.environ["AI201_CACHE"] = "0"  # must happen before config is imported

import config  # noqa: E402
import runlog  # noqa: E402
from capstone_queries import TEST_QUERIES  # noqa: E402

ROOT = Path(__file__).parent
NORMAL_QUERY = "vintage graphic tee under $30"


def run_queries(queries: list[str], log_file: Path) -> list[dict]:
    """Run each query through run_agent, logging to log_file. Returns the log records."""
    from agent import run_agent
    from utils.data_loader import get_example_wardrobe

    log_file.parent.mkdir(exist_ok=True)
    log_file.unlink(missing_ok=True)
    os.environ["FITFINDR_LOG"] = str(log_file)
    for query in queries:
        try:
            run_agent(query, get_example_wardrobe())
        except Exception as exc:  # noqa: BLE001 — the crash is already in the log
            print(f"  CRASH on {query!r}: {exc}", file=sys.stderr)
    return runlog.read(log_file)


# ── scoring: one function per criterion, reading only the log ──────────────

def _rejected(r):
    return r["outcome"] == "off_topic" and not r["search_called"]


def _good_message(msg):
    return (
        bool(msg)
        and "clothing" in msg.lower()
        and re.search(r"['\"][^'\"]+['\"]", msg) is not None
        and not msg.startswith("No listings matched")
    )


def score(records: list[dict]) -> dict:
    label = dict(TEST_QUERIES)
    off = [r for r in records if label.get(r["query"]) == "off_topic"]
    on = [r for r in records if label.get(r["query"]) == "on_topic"]
    rejected = [r for r in records if r["outcome"] == "off_topic"]
    with_results = [r for r in on if r["search_called"] and r["results_count"] > 0]
    return {
        1: (sum(_rejected(r) for r in off), len(off)),
        2: (sum(r["search_called"] for r in on), len(on)),
        3: (sum(r["model_calls"] == 0 and not r["search_called"] for r in rejected), len(rejected)),
        4: (sum(_good_message(r["error"]) for r in rejected), len(rejected)),
        5: (sum(r["outcome"] == "ok" and r["fit_card_chars"] >= 150 for r in with_results), len(with_results)),
    }


CRITERIA = {
    1: ("Off-topic queries are rejected", "≥ 8 of 10", lambda k, n: k >= 8),
    2: ("Real clothing queries get through", "≥ 9 of 10", lambda k, n: k >= 9),
    3: ("A rejection costs nothing (0 model, 0 search calls)", "every rejection", lambda k, n: k == n),
    4: ("Rejection message has 'clothing' + an example in quotes", "every rejection", lambda k, n: k == n),
    5: ("Normal path still ends with a fit card ≥ 150 chars", "every passing query with results", lambda k, n: n > 0 and k == n),
}


def run_trials(label: str, trials: int) -> None:
    queries = [q for q, _ in TEST_QUERIES]
    per_trial = []
    for t in range(1, trials + 1):
        log_file = ROOT / "logs" / f"capstone_{label}_trial{t}.jsonl"
        print(f"\n=== trial {t} of {trials} → {log_file.name}", file=sys.stderr)
        records = run_queries(queries, log_file)
        per_trial.append((records, score(records)))
        print(f"  {len(records)} log records for {len(queries)} queries", file=sys.stderr)

    lines = [
        f"# Capstone run — {label}",
        "",
        f"- {time.strftime('%Y-%m-%d %H:%M')} · model `{config.MODEL}` · cache off · "
        f"{len(queries)} labelled queries from `capstone_queries.py` × {trials} trials",
        "- Produced by `run_capstone.py::run_trials`, calling `agent.py::run_agent`; "
        "scored from the logs in `logs/capstone_" + label + "_trial*.jsonl`",
        "- Log records per trial: " + ", ".join(f"{len(r)}/{len(queries)}" for r, _ in per_trial),
        "",
        "| Criterion | Target | " + " | ".join(f"Run {i}" for i in range(1, trials + 1)) + " | Verdict |",
        "|---|---|" + "---|" * trials + "---|",
    ]
    for c, (name, target, ok) in CRITERIA.items():
        cells = [f"{s[c][0]}/{s[c][1]}" for _, s in per_trial]
        met = all(ok(*s[c]) for _, s in per_trial)
        lines.append(f"| {c}. {name} | {target} | " + " | ".join(cells) + f" | {'MET' if met else 'MISSED'} |")

    lines += ["", "## Every query, every trial", "",
              "| Query | Label | " + " | ".join(f"Run {i}" for i in range(1, trials + 1)) + " |",
              "|---|---|" + "---|" * trials]
    label_of = dict(TEST_QUERIES)
    for q in queries:
        cells = []
        for records, _ in per_trial:
            r = next((x for x in records if x["query"] == q), None)
            if r is None:
                cells.append("no log record")
            else:
                extra = f", card {r['fit_card_chars']} chars" if r["fit_card"] else ""
                cells.append(f"{r['outcome']}, {r['model_calls']} calls{extra}")
        lines.append(f"| {q} | {label_of[q]} | " + " | ".join(cells) + " |")

    out = ROOT / "results" / f"capstone_{label}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:16]))
    print(f"\nWrote {out}", file=sys.stderr)


def run_cost(n: int = 10) -> None:
    log_file = ROOT / "logs" / "capstone_cost.jsonl"
    records = run_queries([NORMAL_QUERY] * n, log_file)
    ok = [r for r in records if r["outcome"] == "ok"]
    if not ok:
        print("No successful runs — nothing to average. Check the log.")
        return
    avg = lambda key: round(sum(r[key] for r in ok) / len(ok), 1)  # noqa: E731
    summary = {
        "query": NORMAL_QUERY,
        "successful_runs": len(ok),
        "of": n,
        "avg_model_calls": avg("model_calls"),
        "avg_prompt_tokens": avg("prompt_tokens"),
        "avg_output_tokens": avg("output_tokens"),
        "avg_total_tokens": round(avg("prompt_tokens") + avg("output_tokens"), 1),
        "avg_duration_ms": avg("duration_ms"),
        "min_duration_ms": min(r["duration_ms"] for r in ok),
        "max_duration_ms": max(r["duration_ms"] for r in ok),
    }
    out = ROOT / "results" / "capstone_cost.json"
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"\nWrote {out} (raw records: {log_file})", file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", default="before")
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--cost", action="store_true")
    args = parser.parse_args()
    run_cost() if args.cost else run_trials(args.label, args.trials)
