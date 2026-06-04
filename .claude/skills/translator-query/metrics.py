#!/usr/bin/env python3
"""Session metrics for the translator-query skill experiment.

Captures, per Claude Code session:
  * token usage (input / output / cache-creation / cache-read), parsed from the
    session transcript JSONL that Claude Code writes locally (works even on a
    Max / subscription plan, where /cost reports nothing).
  * time-to-first-answer (wall clock, from the skill's own markers).
  * total session time.

Concurrency model
-----------------
Two sessions may run in different terminals against the same project dir, so we
never guess the "newest" transcript. Instead:

  * ``start`` mints a UUID nonce, stores wall-clock state keyed by that nonce,
    and prints ``METRICS_NONCE=<uuid>``. Because tool output is recorded into the
    calling session's transcript, the nonce ends up in *only* that transcript.
  * the skill threads the nonce explicitly into ``first-answer --nonce <uuid>``.
  * ``finalize`` is invoked by the SessionEnd hook, which provides the exact
    ``transcript_path`` and ``session_id`` on stdin (authoritative). It scans
    that transcript for the nonce, loads the matching state, sums tokens from the
    same transcript, and appends one CSV row.

Pure standard library; no TCT import, so it stays fast.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
STATE_DIR = SKILL_DIR / ".metrics_state"
# benchmarks/results lives at the repo root: .../text-query/benchmarks/results
REPO_ROOT = SKILL_DIR.parents[2]  # .claude/skills/translator-query -> repo root
CSV_PATH = REPO_ROOT / "benchmarks" / "results" / "tct_session_metrics.csv"

NONCE_PREFIX = "METRICS_NONCE="

CSV_COLUMNS = [
    "session_id",
    "nonce",
    "timestamp_utc",
    "tct_version",
    "experiment_label",
    "query",
    "model",
    "num_assistant_turns",
    "input_tokens",
    "output_tokens",
    "cache_creation_tokens",
    "cache_read_tokens",
    "total_tokens",
    "time_to_first_answer_s",
    "total_session_time_s",
    "transcript_span_s",
]


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _now() -> float:
    return time.time()


def _state_path(nonce: str) -> Path:
    return STATE_DIR / f"{nonce}.json"


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return {}


def _detect_tct_version() -> str:
    """Best-effort TCT package version (does not import TCT)."""
    try:
        from importlib import metadata
    except ImportError:  # pragma: no cover - py<3.8
        return "unknown"
    for dist in ("tct", "TCT", "translator-component-toolkit"):
        try:
            return metadata.version(dist)
        except metadata.PackageNotFoundError:
            continue
    return "unknown"


def _iter_transcript(transcript_path: Path):
    """Yield parsed JSON objects from a transcript JSONL, skipping bad lines."""
    try:
        with transcript_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except ValueError:
                    continue
    except OSError:
        return


def _parse_iso(ts: str) -> float | None:
    if not ts:
        return None
    try:
        # tolerate trailing Z
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def summarize_transcript(transcript_path: Path) -> dict:
    """Sum token usage and collect timing/model info from a transcript."""
    totals = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_creation_tokens": 0,
        "cache_read_tokens": 0,
    }
    num_assistant_turns = 0
    models: list[str] = []
    timestamps: list[float] = []

    for obj in _iter_transcript(transcript_path):
        ts = _parse_iso(obj.get("timestamp", ""))
        if ts is not None:
            timestamps.append(ts)

        message = obj.get("message")
        if not isinstance(message, dict):
            continue
        usage = message.get("usage")
        if not isinstance(usage, dict):
            continue

        num_assistant_turns += 1
        totals["input_tokens"] += int(usage.get("input_tokens", 0) or 0)
        totals["output_tokens"] += int(usage.get("output_tokens", 0) or 0)
        totals["cache_creation_tokens"] += int(
            usage.get("cache_creation_input_tokens", 0) or 0
        )
        totals["cache_read_tokens"] += int(
            usage.get("cache_read_input_tokens", 0) or 0
        )
        model = message.get("model")
        if model and model not in models:
            models.append(model)

    total_tokens = sum(totals.values())
    span = (max(timestamps) - min(timestamps)) if timestamps else 0.0
    return {
        **totals,
        "total_tokens": total_tokens,
        "num_assistant_turns": num_assistant_turns,
        "model": "|".join(models),
        "transcript_span_s": round(span, 3),
    }


def find_nonce_in_transcript(transcript_path: Path) -> str | None:
    """Return the METRICS_NONCE emitted by `start` within this transcript."""
    pattern = re.compile(re.escape(NONCE_PREFIX) + r"([0-9a-fA-F-]{36})")
    for obj in _iter_transcript(transcript_path):
        # The nonce is in a tool_result; just search the serialized line.
        m = pattern.search(json.dumps(obj))
        if m:
            return m.group(1)
    return None


# --------------------------------------------------------------------------- #
# subcommands
# --------------------------------------------------------------------------- #
def cmd_start(args: argparse.Namespace) -> int:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    nonce = str(uuid.uuid4())
    state = {
        "nonce": nonce,
        "query": args.query or "",
        "experiment_label": os.environ.get("TCT_EXPERIMENT_VERSION", ""),
        "start_epoch": _now(),
        "first_answer_epoch": None,
    }
    _state_path(nonce).write_text(json.dumps(state, indent=2))
    # This line is captured into the calling session's transcript only.
    print(f"{NONCE_PREFIX}{nonce}")
    return 0


def cmd_first_answer(args: argparse.Namespace) -> int:
    path = _state_path(args.nonce)
    state = _read_json(path)
    if not state:
        print(f"metrics: no state for nonce {args.nonce}", file=sys.stderr)
        return 1
    if state.get("first_answer_epoch") is None:
        state["first_answer_epoch"] = _now()
        path.write_text(json.dumps(state, indent=2))
    return 0


def _read_hook_stdin() -> dict:
    if sys.stdin is None or sys.stdin.isatty():
        return {}
    try:
        data = sys.stdin.read()
    except OSError:
        return {}
    if not data.strip():
        return {}
    try:
        return json.loads(data)
    except ValueError:
        return {}


def cmd_finalize(args: argparse.Namespace) -> int:
    hook = _read_hook_stdin()
    transcript_path = args.transcript_path or hook.get("transcript_path")
    session_id = args.session_id or hook.get("session_id", "")

    if not transcript_path:
        print("metrics finalize: no transcript_path available", file=sys.stderr)
        return 1
    transcript_path = Path(transcript_path).expanduser()
    if not transcript_path.exists():
        print(f"metrics finalize: transcript not found: {transcript_path}",
              file=sys.stderr)
        return 1

    nonce = args.nonce or find_nonce_in_transcript(transcript_path)
    state = _read_json(_state_path(nonce)) if nonce else {}

    summary = summarize_transcript(transcript_path)

    start_epoch = state.get("start_epoch")
    first_epoch = state.get("first_answer_epoch")
    now = _now()

    ttfa = round(first_epoch - start_epoch, 3) if (start_epoch and first_epoch) else ""
    total_time = round(now - start_epoch, 3) if start_epoch else summary["transcript_span_s"]

    row = {
        "session_id": session_id or transcript_path.stem,
        "nonce": nonce or "",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "tct_version": _detect_tct_version(),
        "experiment_label": state.get("experiment_label", "")
        or os.environ.get("TCT_EXPERIMENT_VERSION", ""),
        "query": state.get("query", ""),
        "model": summary["model"],
        "num_assistant_turns": summary["num_assistant_turns"],
        "input_tokens": summary["input_tokens"],
        "output_tokens": summary["output_tokens"],
        "cache_creation_tokens": summary["cache_creation_tokens"],
        "cache_read_tokens": summary["cache_read_tokens"],
        "total_tokens": summary["total_tokens"],
        "time_to_first_answer_s": ttfa,
        "total_session_time_s": total_time,
        "transcript_span_s": summary["transcript_span_s"],
    }

    _append_csv_row(row)

    # Clean up the state file so it isn't double-counted.
    if nonce:
        try:
            _state_path(nonce).unlink()
        except OSError:
            pass

    print(f"metrics: wrote session row to {CSV_PATH}")
    return 0


def _append_csv_row(row: dict) -> None:
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_header = not CSV_PATH.exists()
    with CSV_PATH.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS)
        if write_header:
            writer.writeheader()
        writer.writerow({k: row.get(k, "") for k in CSV_COLUMNS})


# --------------------------------------------------------------------------- #
# entrypoint
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="translator-query session metrics")
    sub = parser.add_subparsers(dest="command", required=True)

    p_start = sub.add_parser("start", help="mark session start; prints METRICS_NONCE")
    p_start.add_argument("--query", default="", help="the user's question")
    p_start.set_defaults(func=cmd_start)

    p_first = sub.add_parser("first-answer", help="mark time of first answer")
    p_first.add_argument("--nonce", required=True, help="nonce printed by `start`")
    p_first.set_defaults(func=cmd_first_answer)

    p_final = sub.add_parser("finalize", help="parse transcript and write CSV row")
    p_final.add_argument("--transcript-path", dest="transcript_path", default=None,
                         help="override (else read from hook stdin)")
    p_final.add_argument("--session-id", dest="session_id", default=None)
    p_final.add_argument("--nonce", default=None,
                         help="override (else discovered from transcript)")
    p_final.set_defaults(func=cmd_finalize)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
