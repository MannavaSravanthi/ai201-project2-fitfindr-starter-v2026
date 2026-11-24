"""
Structured run log — capstone, Milestone 3.

Every call to agent.run_agent() appends ONE JSON record to logs/runs.jsonl,
including runs that were rejected or crashed. The write happens in a
`finally`, so a failure can't show up only as a missing line.

Set FITFINDR_LOG to write to a different file (the capstone test runner does
this so each trial gets its own log).

    python runlog.py          print the last 10 records
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_PATH = Path(__file__).parent / "logs" / "runs.jsonl"


def log_path() -> Path:
    return Path(os.getenv("FITFINDR_LOG") or DEFAULT_PATH)


def write(record: dict) -> None:
    """Append one record. Never raises — logging must not break a run."""
    try:
        path = log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        stamped = {"ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"), **record}
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(stamped, ensure_ascii=False, default=str) + "\n")
    except Exception as exc:  # noqa: BLE001
        print(f"  [runlog] couldn't write a log record: {exc}", file=sys.stderr)


def read(path: Path | None = None) -> list[dict]:
    path = path or log_path()
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


if __name__ == "__main__":
    for record in read()[-10:]:
        print(json.dumps(record, ensure_ascii=False))
