"""
utils/log_utils.py
Save execution logs to the /logs directory
"""
import os
import json
import datetime


LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")


def save_log(log_entries: list[dict], query: str) -> str:
    """Save execution log as JSON file. Returns file path."""
    os.makedirs(LOGS_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"run_{ts}.json"
    path = os.path.join(LOGS_DIR, fname)
    payload = {
        "query": query,
        "timestamp": ts,
        "steps": len(log_entries),
        "entries": log_entries,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return path


def list_logs() -> list[dict]:
    """Return metadata for all saved logs."""
    os.makedirs(LOGS_DIR, exist_ok=True)
    logs = []
    for fname in sorted(os.listdir(LOGS_DIR), reverse=True):
        if fname.endswith(".json"):
            fpath = os.path.join(LOGS_DIR, fname)
            try:
                with open(fpath) as f:
                    data = json.load(f)
                logs.append({
                    "file": fname,
                    "path": fpath,
                    "query": data.get("query", "")[:80],
                    "timestamp": data.get("timestamp", ""),
                    "steps": data.get("steps", 0),
                })
            except Exception:
                pass
    return logs


def load_log(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)
