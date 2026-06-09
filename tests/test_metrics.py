"""Tests for the translator-query session metrics script."""

import csv
import importlib.util
import json
from pathlib import Path

import pytest

METRICS_PATH = (
    Path(__file__).resolve().parents[1]
    / ".claude"
    / "skills"
    / "translator-query"
    / "metrics.py"
)


def _load_metrics():
    spec = importlib.util.spec_from_file_location("tct_metrics", METRICS_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


metrics = _load_metrics()


def _write_transcript(path: Path, nonce: str) -> None:
    """A minimal transcript: a tool_result carrying the nonce + two assistant
    messages with usage."""
    lines = [
        {
            "timestamp": "2026-06-04T23:40:00.000Z",
            "type": "user",
            "message": {
                "content": [
                    {
                        "type": "tool_result",
                        "content": f"METRICS_NONCE={nonce}\n",
                    }
                ]
            },
        },
        {
            "timestamp": "2026-06-04T23:40:05.000Z",
            "type": "assistant",
            "message": {
                "model": "claude-opus-4-8",
                "usage": {
                    "input_tokens": 10,
                    "output_tokens": 20,
                    "cache_creation_input_tokens": 100,
                    "cache_read_input_tokens": 1000,
                },
            },
        },
        {
            "timestamp": "2026-06-04T23:40:15.000Z",
            "type": "assistant",
            "message": {
                "model": "claude-opus-4-8",
                "usage": {
                    "input_tokens": 5,
                    "output_tokens": 30,
                    "cache_creation_input_tokens": 0,
                    "cache_read_input_tokens": 2000,
                },
            },
        },
    ]
    path.write_text("\n".join(json.dumps(line) for line in lines))


def test_summarize_transcript(tmp_path):
    t = tmp_path / "session.jsonl"
    _write_transcript(t, "abc")
    s = metrics.summarize_transcript(t)
    assert s["input_tokens"] == 15
    assert s["output_tokens"] == 50
    assert s["cache_creation_tokens"] == 100
    assert s["cache_read_tokens"] == 3000
    assert s["total_tokens"] == 3165
    assert s["num_assistant_turns"] == 2
    assert s["model"] == "claude-opus-4-8"
    assert s["transcript_span_s"] == pytest.approx(15.0)


def test_summarize_dedups_multiline_message(tmp_path):
    """Claude Code emits several JSONL lines per assistant response, all sharing
    one message.id and repeating the same usage. summarize_transcript must count
    each response once (element-wise max), not sum every line."""
    lines = [
        # One logical response spread over 3 lines (e.g. thinking + text +
        # tool_use). Streaming makes output_tokens grow; the rest is constant.
        {
            "timestamp": "2026-06-04T23:40:05.000Z",
            "type": "assistant",
            "message": {
                "id": "msg_dup",
                "model": "claude-opus-4-8",
                "usage": {
                    "input_tokens": 3,
                    "output_tokens": 10,
                    "cache_creation_input_tokens": 500,
                    "cache_read_input_tokens": 9000,
                },
            },
        },
        {
            "timestamp": "2026-06-04T23:40:06.000Z",
            "type": "assistant",
            "message": {
                "id": "msg_dup",
                "model": "claude-opus-4-8",
                "usage": {
                    "input_tokens": 3,
                    "output_tokens": 25,
                    "cache_creation_input_tokens": 500,
                    "cache_read_input_tokens": 9000,
                },
            },
        },
        {
            "timestamp": "2026-06-04T23:40:07.000Z",
            "type": "assistant",
            "message": {
                "id": "msg_dup",
                "model": "claude-opus-4-8",
                "usage": {
                    "input_tokens": 3,
                    "output_tokens": 40,
                    "cache_creation_input_tokens": 500,
                    "cache_read_input_tokens": 9000,
                },
            },
        },
        # A second, distinct response.
        {
            "timestamp": "2026-06-04T23:40:10.000Z",
            "type": "assistant",
            "message": {
                "id": "msg_two",
                "model": "claude-opus-4-8",
                "usage": {
                    "input_tokens": 2,
                    "output_tokens": 7,
                    "cache_creation_input_tokens": 0,
                    "cache_read_input_tokens": 11000,
                },
            },
        },
    ]
    t = tmp_path / "session.jsonl"
    t.write_text("\n".join(json.dumps(line) for line in lines))

    s = metrics.summarize_transcript(t)
    # Two real responses, not four lines.
    assert s["num_assistant_turns"] == 2
    # max(output) of msg_dup is 40, plus 7 from msg_two.
    assert s["output_tokens"] == 47
    # input/cache counted once per message id, not once per line.
    assert s["input_tokens"] == 5
    assert s["cache_creation_tokens"] == 500
    assert s["cache_read_tokens"] == 20000
    assert s["total_tokens"] == 20552


def test_find_nonce_in_transcript(tmp_path):
    nonce = "11111111-2222-3333-4444-555555555555"
    t = tmp_path / "session.jsonl"
    _write_transcript(t, nonce)
    assert metrics.find_nonce_in_transcript(t) == nonce


def test_full_flow(tmp_path, monkeypatch):
    """start -> first-answer -> finalize writes one correct CSV row."""
    state_dir = tmp_path / "state"
    csv_path = tmp_path / "out.csv"
    monkeypatch.setattr(metrics, "STATE_DIR", state_dir)
    monkeypatch.setattr(metrics, "CSV_PATH", csv_path)
    # deterministic, ordered clock
    clock = iter([1000.0, 1003.0, 1030.0])
    monkeypatch.setattr(metrics, "_now", lambda: next(clock))

    # start
    import argparse

    metrics.cmd_start(argparse.Namespace(query="what microbes relate to acne?"))
    state_files = list(state_dir.glob("*.json"))
    assert len(state_files) == 1
    nonce = state_files[0].stem

    # first-answer
    rc = metrics.cmd_first_answer(argparse.Namespace(nonce=nonce))
    assert rc == 0

    # finalize against a transcript carrying that nonce
    transcript = tmp_path / "session.jsonl"
    _write_transcript(transcript, nonce)
    rc = metrics.cmd_finalize(
        argparse.Namespace(
            transcript_path=str(transcript),
            session_id="sess-123",
            nonce=None,
        )
    )
    assert rc == 0

    rows = list(csv.DictReader(csv_path.open()))
    assert len(rows) == 1
    row = rows[0]
    assert row["session_id"] == "sess-123"
    assert row["nonce"] == nonce
    assert row["query"] == "what microbes relate to acne?"
    assert row["total_tokens"] == "3165"
    assert row["time_to_first_answer_s"] == "3.0"
    assert row["total_session_time_s"] == "30.0"
    # state file cleaned up after finalize
    assert not (state_dir / f"{nonce}.json").exists()


def test_finalize_missing_transcript(tmp_path, monkeypatch):
    monkeypatch.setattr(metrics, "CSV_PATH", tmp_path / "out.csv")
    import argparse

    rc = metrics.cmd_finalize(
        argparse.Namespace(
            transcript_path=str(tmp_path / "nope.jsonl"),
            session_id=None,
            nonce=None,
        )
    )
    assert rc == 1
