#!/usr/bin/env python3
"""
A real session against the running service, then the cost number. ← CAPSTONE

Start the service first, in another terminal, with fault injection on:

    AI201_FAULT_INJECTION=1 python app.py           (bash)
    $env:AI201_FAULT_INJECTION=1; python app.py      (PowerShell)

Then:

    python capstone_session.py            10 normal submissions + 5 bad-path ones
    python capstone_session.py --cost     just the cost summary from the log

Every request lands in logs/requests.jsonl via reqlog.py. The cost summary is
read back from that file — it measures what the service recorded, not what
this script timed on its side.
"""

import argparse
import csv
import statistics
import sys

import requests

import config
import reqlog
from scenarios import CLEARLY_AI, CLEARLY_HUMAN

URL = f"http://{config.HOST}:{config.PORT}"


def normal_texts() -> list[str]:
    """Ten valid pieces: 3 machine-written, 5 public-domain human, 2 attack-set."""
    with open(config.ROOT / "attack_set" / "attacks.csv", encoding="utf-8") as f:
        attacks = [row["text"] for row in csv.DictReader(f)][:2]
    return (CLEARLY_AI + CLEARLY_HUMAN + attacks)[:10]


def bad_path() -> list[tuple[str, dict, dict]]:
    """(name, body, headers) for one of each failure the extension handles."""
    text = CLEARLY_HUMAN[0]
    return [
        ("detector raises", {"text": text, "creator_id": "cap_fault"}, {"X-Fault": "detector_error"}),
        ("detector hangs", {"text": text, "creator_id": "cap_fault"}, {"X-Fault": "detector_slow"}),
        ("style signal raises", {"text": text, "creator_id": "cap_fault"}, {"X-Fault": "style_error"}),
        ("audit log unwritable", {"text": text, "creator_id": "cap_fault"}, {"X-Fault": "audit_unwritable"}),
        ("missing text", {"creator_id": "cap_fault"}, {}),
    ]


def send(body: dict, headers: dict) -> requests.Response:
    return requests.post(f"{URL}/submit", json=body, headers=headers, timeout=60)


def cost_summary() -> None:
    """Average cost of a normal /submit, from the request log."""
    records = [r for r in reqlog.read()
               if r.get("route") == "/submit" and r.get("status") == 200
               and not (r.get("input") or {}).get("fault")]
    if not records:
        print("No successful /submit records in the log yet.")
        return
    last = records[-10:]
    total = [r["duration_ms"] for r in last]
    det = [r["detector_ms"] for r in last if r.get("detector_ms") is not None]
    print(f"Cost of one /submit — last {len(last)} successful requests in {config.REQUEST_LOG.name}")
    print(f"  wall-clock per request   mean {statistics.mean(total):.0f} ms   "
          f"median {statistics.median(total):.0f} ms   min {min(total)}   max {max(total)}")
    if det:
        print(f"  inside the detector      mean {statistics.mean(det):.0f} ms   "
              f"({statistics.mean(det) / statistics.mean(total):.0%} of the request)")
    print("  API spend                $0 — the model runs locally, no hosted API is called")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cost", action="store_true", help="only print the cost summary")
    args = parser.parse_args()
    if args.cost:
        cost_summary()
        return

    try:
        health = requests.get(f"{URL}/health", timeout=5).json()
    except requests.RequestException as exc:
        sys.exit(f"The service isn't answering on {URL} — start it first ({exc}).")
    print(f"service up · detector_loaded={health.get('detector_loaded')}\n")

    print("Normal submissions")
    for i, text in enumerate(normal_texts(), 1):
        r = send({"text": text, "creator_id": f"cap_user_{i}"}, {})
        j = r.json()
        print(f"  {i:>2}. {r.status_code}  {j.get('guess', j.get('error')):<8} "
              f"confidence={j.get('confidence')}  id={r.headers.get('X-Request-ID')}")

    print("\nBad path (needs AI201_FAULT_INJECTION=1 on the service)")
    for name, body, headers in bad_path():
        r = send(body, headers)
        j = r.json() if r.headers.get("Content-Type", "").startswith("application/json") else {}
        print(f"  {name:<22} {r.status_code}  {j.get('error', '(not JSON!)')}")

    print()
    cost_summary()


if __name__ == "__main__":
    main()
