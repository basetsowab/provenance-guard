#!/usr/bin/env python3
"""
Three trials of the five capstone criteria (criteria.md, C1-C5). ← CAPSTONE

Start the service with fault injection on, in another terminal:

    AI201_FAULT_INJECTION=1 python app.py

Then:

    python capstone_eval.py --label before

Writes results/capstone_<stamp>_<label>.md: the run-log table plus the raw
response and log lines behind every cell.

How each criterion is tested (one test per criterion per trial):

  C1  POST /submit with X-Fault: detector_slow. PASS if the status is 503 and
      the answer arrived in under 11 s, timed by this client.
  C2  POST /submit with X-Fault: detector_error. PASS if the answer is a 5xx
      JSON body with an `error` and a `message`, AND /ping still answers 200
      straight afterwards (the server didn't go down).
  C3  Three processing failures — detector_error, style_error, detector_slow.
      PASS if all three left an entry in logs/audit.jsonl (matched by a
      creator_id unique to this trial).
  C4  GET and POST to /does-not-exist. PASS if both return 404.
  C5  Five malformed /submit bodies: empty body, broken JSON, a JSON array,
      a JSON string, an empty object. PASS if all five are 4xx with an
      `error` reason, AND the request log shows the detector never ran for
      them (detector_ms is null) — "shouldn't reach the classifier".

The unit 8 rate limiter stays ON (5/minute per creator_id, or per address when
there is none). C5's bodies have no creator_id, so they count against the
address: five per trial, and a 65 s pause between trials keeps them under it.
"""

import argparse
import datetime as dt
import json
import time
import uuid

import requests

import audit
import config
import reqlog
from scenarios import CLEARLY_HUMAN

URL = f"http://{config.HOST}:{config.PORT}"
TEXT = CLEARLY_HUMAN[0]


def post(path, *, json_body=None, data=None, headers=None, content_type="application/json"):
    h = {"Content-Type": content_type, **(headers or {})}
    started = time.perf_counter()
    if json_body is not None:
        r = requests.post(URL + path, data=json.dumps(json_body), headers=h, timeout=60)
    else:
        r = requests.post(URL + path, data=data, headers=h, timeout=60)
    return r, time.perf_counter() - started


def body(r):
    try:
        return r.json()
    except ValueError:
        return {"_not_json": r.text[:80]}


def c1(trial):
    r, s = post("/submit", json_body={"text": TEXT, "creator_id": f"c1_{trial}"},
                headers={"X-Fault": "detector_slow"})
    ok = r.status_code == 503 and s < 11
    return ok, f"{r.status_code} in {s:.2f}s", f"{r.status_code} {s:.2f}s {json.dumps(body(r))}"


def c2(trial):
    r, s = post("/submit", json_body={"text": TEXT, "creator_id": f"c2_{trial}"},
                headers={"X-Fault": "detector_error"})
    b = body(r)
    clear = 500 <= r.status_code < 600 and bool(b.get("error")) and bool(b.get("message"))
    ping = requests.post(URL + "/ping", json={"message": "still up?"}, timeout=10)
    ok = clear and ping.status_code == 200
    return ok, f"{r.status_code} {b.get('error')}, ping {ping.status_code}", \
        f"{r.status_code} {json.dumps(b)}\n/ping -> {ping.status_code} {ping.text.strip()}"


def c3(trial):
    tag = f"c3_{trial}_{uuid.uuid4().hex[:6]}"
    faults = ["detector_error", "style_error", "detector_slow"]
    for i, f in enumerate(faults):
        post("/submit", json_body={"text": TEXT, "creator_id": f"{tag}_{i}"}, headers={"X-Fault": f})
    found = []
    entries = audit.read_entries()
    for i, f in enumerate(faults):
        hits = [e for e in entries if e.get("creator_id") == f"{tag}_{i}"]
        found.append((f, hits[-1] if hits else None))
    n = sum(1 for _, e in found if e)
    raw = "\n".join(f"{f}: {json.dumps(e) if e else 'NO AUDIT ENTRY'}" for f, e in found)
    return n == len(faults), f"{n}/{len(faults)} logged", raw


def c4(trial):
    g = requests.get(URL + "/does-not-exist", timeout=10)
    p = requests.post(URL + "/does-not-exist", json={"x": trial}, timeout=10)
    ok = g.status_code == 404 and p.status_code == 404
    return ok, f"GET {g.status_code}, POST {p.status_code}", \
        f"GET {g.status_code} {g.text.strip()[:160]}\nPOST {p.status_code} {p.text.strip()[:160]}"


C5_BODIES = [
    ("empty body", b""),
    ("broken JSON", b'{"text": "hello", "creator_id": '),
    ("JSON array", b'["text", "creator_id"]'),
    ("JSON string", b'"just a string"'),
    ("empty object", b"{}"),
]


def c5(trial):
    lines, ok_count, ids = [], 0, []
    for name, raw in C5_BODIES:
        r, _ = post("/submit", data=raw)
        b = body(r)
        rid = r.headers.get("X-Request-ID")
        ids.append(rid)
        good = 400 <= r.status_code < 500 and bool(b.get("error"))
        ok_count += good
        lines.append((name, r.status_code, b.get("error"), rid))
    records = {rec.get("request_id"): rec for rec in reqlog.read()}
    reached = [rid for rid in ids if (records.get(rid) or {}).get("detector_ms") is not None]
    ok = ok_count == len(C5_BODIES) and not reached
    raw = "\n".join(f"{n:<13} {s} error={e} request_id={rid} detector_ms="
                    f"{(records.get(rid) or {}).get('detector_ms')}" for n, s, e, rid in lines)
    return ok, f"{ok_count}/5 4xx, {len(reached)} reached detector", raw


CRITERIA = [
    ("C1. Slow model → 503 within 11 s", "3/3", c1),
    ("C2. Model crash → clear error, server stays up", "3/3", c2),
    ("C3. Processing failure → in the audit log", "3/3", c3),
    ("C4. Invalid endpoint → 404", "3/3", c4),
    ("C5. Empty/malformed JSON → 4xx with reason, never reaches classifier", "3/3", c5),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="")
    ap.add_argument("--trials", type=int, default=3)
    ap.add_argument("--pause", type=float, default=65, help="seconds between trials")
    args = ap.parse_args()

    health = requests.get(URL + "/health", timeout=5).json()
    print(f"service up · detector_loaded={health.get('detector_loaded')}")

    results = {name: [] for name, _, _ in CRITERIA}
    for trial in range(1, args.trials + 1):
        print(f"\ntrial {trial}")
        for name, _, fn in CRITERIA:
            ok, short, raw = fn(trial)
            results[name].append((ok, short, raw))
            print(f"  {'PASS' if ok else 'FAIL'}  {name}: {short}")
        if trial < args.trials:
            print(f"  (pausing {args.pause:.0f}s so the rate limiter's minute resets)")
            time.sleep(args.pause)

    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    path = config.RESULTS_DIR / f"capstone_{stamp}{'_' + args.label if args.label else ''}.md"
    heads = " | ".join(f"Run {i}" for i in range(1, args.trials + 1))
    out = [f"# Capstone run log{' — ' + args.label if args.label else ''}", "",
           f"- Produced by `capstone_eval.py::main`, {dt.datetime.now():%Y-%m-%d %H:%M}",
           f"- Detector timeout: {config.DETECTOR_TIMEOUT_S:.0f}s · rate limiting ON", "",
           f"| Criterion | Target | {heads} | Verdict |",
           f"|---|---|{'|'.join(['---'] * args.trials)}|---|"]
    for name, target, _ in CRITERIA:
        cells = [f"{'PASS' if ok else 'FAIL'} ({short})" for ok, short, _ in results[name]]
        n = sum(ok for ok, _, _ in results[name])
        verdict = "MET" if n == args.trials else "MISSED"
        out.append(f"| {name} | {target} | {' | '.join(cells)} | {verdict} ({n}/{args.trials}) |")
    out += ["", "## Raw output, every trial", ""]
    for name, _, _ in CRITERIA:
        out.append(f"### {name}")
        for i, (ok, _, raw) in enumerate(results[name], 1):
            out += [f"**Run {i}** — {'PASS' if ok else 'FAIL'}", "", "```", raw, "```", ""]
    config.RESULTS_DIR.mkdir(exist_ok=True)
    path.write_text("\n".join(out), encoding="utf-8")
    print(f"\nWrote {path.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
