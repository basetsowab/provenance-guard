"""
The request log. ← CAPSTONE

One JSON record per HTTP request, written to logs/requests.jsonl, whatever the
request's outcome — a decision, a refusal, a timeout or a crash.

The audit log (audit.py) records *decisions about content*: what was judged,
the scores, appeals. This records *what the service did*: which route, how
long it took, how long the detector took, what came in, what went out, and
whether the audit write failed. That's the record you need to count failures
and measure cost afterwards without adding code first.

Fields in every record:

    timestamp     UTC, ISO 8601, when the request finished
    request_id    also sent back as the X-Request-ID header and in error JSON
    method, route
    status        HTTP status code returned
    duration_ms   wall-clock time for the whole request
    detector_ms   time inside the detector call (null if it didn't run)
    input         creator_id, text_length, text_preview (first 40 chars), fault
    output        the error reason, or content_id / guess / scores
    audit_error   set when writing the audit log failed (null otherwise)
    exception     the exception, when the request crashed (null otherwise)

The text itself is not stored — a 40-character preview is enough to tell runs
apart, and a log full of people's writing is a liability.

    python reqlog.py           summary of logs/requests.jsonl
"""

import json
import sys
import threading
from datetime import datetime, timezone

import config

_lock = threading.Lock()


def write(record: dict) -> None:
    """Append one record. A failure to write is reported, never raised."""
    record = {"timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
              **record}
    try:
        config.REQUEST_LOG.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(record, ensure_ascii=False, default=str)
        with _lock:
            with config.REQUEST_LOG.open("a", encoding="utf-8") as f:
                f.write(line + "\n")
    except OSError as exc:
        print(f"[reqlog] couldn't write request log: {exc} — record: {record}",
              file=sys.stderr, flush=True)


def read(limit: int | None = None) -> list[dict]:
    """Read records back, oldest first. Malformed lines are skipped."""
    if not config.REQUEST_LOG.exists():
        return []
    out = []
    for line in config.REQUEST_LOG.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out[-limit:] if limit else out


if __name__ == "__main__":
    records = read()
    print(f"{len(records)} records in {config.REQUEST_LOG}")
    by_status: dict = {}
    for r in records:
        key = (r.get("route"), r.get("status"), (r.get("output") or {}).get("error"))
        by_status[key] = by_status.get(key, 0) + 1
    for (route, status, error), n in sorted(by_status.items(), key=str):
        print(f"  {n:>4}  {route:<10} {status}  {error or ''}")
