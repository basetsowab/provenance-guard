# Capstone run log — before

- Produced by `capstone_eval.py::main`, 2026-11-15 18:51
- Detector timeout: 10s · rate limiting ON

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| C1. Slow model → 503 within 11 s | 3/3 | PASS (503 in 10.01s) | PASS (503 in 10.01s) | PASS (503 in 10.02s) | MET (3/3) |
| C2. Model crash → clear error, server stays up | 3/3 | PASS (503 detector_failed, ping 200) | PASS (503 detector_failed, ping 200) | PASS (503 detector_failed, ping 200) | MET (3/3) |
| C3. Processing failure → in the audit log | 3/3 | PASS (3/3 logged) | PASS (3/3 logged) | PASS (3/3 logged) | MET (3/3) |
| C4. Invalid endpoint → 404 | 3/3 | PASS (GET 404, POST 404) | PASS (GET 404, POST 404) | PASS (GET 404, POST 404) | MET (3/3) |
| C5. Empty/malformed JSON → 4xx with reason, never reaches classifier | 3/3 | PASS (5/5 4xx, 0 reached detector) | PASS (5/5 4xx, 0 reached detector) | PASS (5/5 4xx, 0 reached detector) | MET (3/3) |

## Raw output, every trial

### C1. Slow model → 503 within 11 s
**Run 1** — PASS

```
503 10.01s {"error": "detector_timeout", "message": "The checker took longer than 10 seconds, so this piece wasn't checked and nothing was recorded against it. Try again in a minute.", "request_id": "cbed04b7041f"}
```

**Run 2** — PASS

```
503 10.01s {"error": "detector_timeout", "message": "The checker took longer than 10 seconds, so this piece wasn't checked and nothing was recorded against it. Try again in a minute.", "request_id": "8f23d67a8be1"}
```

**Run 3** — PASS

```
503 10.02s {"error": "detector_timeout", "message": "The checker took longer than 10 seconds, so this piece wasn't checked and nothing was recorded against it. Try again in a minute.", "request_id": "b602128aaf89"}
```

### C2. Model crash → clear error, server stays up
**Run 1** — PASS

```
503 {"error": "detector_failed", "message": "The checker hit an error on this piece, so it wasn't checked and nothing was recorded against it. Try again; if it keeps happening, the text itself may be the trigger.", "request_id": "e8b778ceff9c"}
/ping -> 200 {
  "ok": true,
  "service": "provenance-guard",
  "you_sent": "still up?"
}
```

**Run 2** — PASS

```
503 {"error": "detector_failed", "message": "The checker hit an error on this piece, so it wasn't checked and nothing was recorded against it. Try again; if it keeps happening, the text itself may be the trigger.", "request_id": "89662145f244"}
/ping -> 200 {
  "ok": true,
  "service": "provenance-guard",
  "you_sent": "still up?"
}
```

**Run 3** — PASS

```
503 {"error": "detector_failed", "message": "The checker hit an error on this piece, so it wasn't checked and nothing was recorded against it. Try again; if it keeps happening, the text itself may be the trigger.", "request_id": "7dc130dc0a16"}
/ping -> 200 {
  "ok": true,
  "service": "provenance-guard",
  "you_sent": "still up?"
}
```

### C3. Processing failure → in the audit log
**Run 1** — PASS

```
detector_error: {"timestamp": "2026-11-15T23:48:50+00:00", "creator_id": "c3_1_e09018_0", "event": "rejected", "status": "rejected", "reason": "detector_failed", "http_status": 503, "detail": "RuntimeError: injected fault: detector_error", "text_length": 390}
style_error: {"timestamp": "2026-11-15T23:48:51+00:00", "creator_id": "c3_1_e09018_1", "event": "rejected", "status": "rejected", "reason": "internal_error", "http_status": 500, "route": "/submit", "detail": "ZeroDivisionError: injected fault: style_error"}
detector_slow: {"timestamp": "2026-11-15T23:49:01+00:00", "creator_id": "c3_1_e09018_2", "event": "rejected", "status": "rejected", "reason": "detector_timeout", "http_status": 503, "detail": "detector took longer than 10s and was abandoned", "text_length": 390}
```

**Run 2** — PASS

```
detector_error: {"timestamp": "2026-11-15T23:50:16+00:00", "creator_id": "c3_2_d9a648_0", "event": "rejected", "status": "rejected", "reason": "detector_failed", "http_status": 503, "detail": "RuntimeError: injected fault: detector_error", "text_length": 390}
style_error: {"timestamp": "2026-11-15T23:50:16+00:00", "creator_id": "c3_2_d9a648_1", "event": "rejected", "status": "rejected", "reason": "internal_error", "http_status": 500, "route": "/submit", "detail": "ZeroDivisionError: injected fault: style_error"}
detector_slow: {"timestamp": "2026-11-15T23:50:26+00:00", "creator_id": "c3_2_d9a648_2", "event": "rejected", "status": "rejected", "reason": "detector_timeout", "http_status": 503, "detail": "detector took longer than 10s and was abandoned", "text_length": 390}
```

**Run 3** — PASS

```
detector_error: {"timestamp": "2026-11-15T23:51:41+00:00", "creator_id": "c3_3_11feed_0", "event": "rejected", "status": "rejected", "reason": "detector_failed", "http_status": 503, "detail": "RuntimeError: injected fault: detector_error", "text_length": 390}
style_error: {"timestamp": "2026-11-15T23:51:41+00:00", "creator_id": "c3_3_11feed_1", "event": "rejected", "status": "rejected", "reason": "internal_error", "http_status": 500, "route": "/submit", "detail": "ZeroDivisionError: injected fault: style_error"}
detector_slow: {"timestamp": "2026-11-15T23:51:51+00:00", "creator_id": "c3_3_11feed_2", "event": "rejected", "status": "rejected", "reason": "detector_timeout", "http_status": 503, "detail": "detector took longer than 10s and was abandoned", "text_length": 390}
```

### C4. Invalid endpoint → 404
**Run 1** — PASS

```
GET 404 {
  "error": "not_found",
  "message": "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.
POST 404 {
  "error": "not_found",
  "message": "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.
```

**Run 2** — PASS

```
GET 404 {
  "error": "not_found",
  "message": "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.
POST 404 {
  "error": "not_found",
  "message": "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.
```

**Run 3** — PASS

```
GET 404 {
  "error": "not_found",
  "message": "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.
POST 404 {
  "error": "not_found",
  "message": "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.
```

### C5. Empty/malformed JSON → 4xx with reason, never reaches classifier
**Run 1** — PASS

```
empty body    400 error=invalid_json request_id=ef73e293a171 detector_ms=None
broken JSON   400 error=invalid_json request_id=8c74fddb4303 detector_ms=None
JSON array    400 error=invalid_json request_id=90b78109cbc0 detector_ms=None
JSON string   400 error=invalid_json request_id=95dc33ecd048 detector_ms=None
empty object  400 error=missing_creator_id request_id=bbd24af3876a detector_ms=None
```

**Run 2** — PASS

```
empty body    400 error=invalid_json request_id=9efdbd815729 detector_ms=None
broken JSON   400 error=invalid_json request_id=c28d6b20a2e3 detector_ms=None
JSON array    400 error=invalid_json request_id=94b706a04da3 detector_ms=None
JSON string   400 error=invalid_json request_id=761454ea6a84 detector_ms=None
empty object  400 error=missing_creator_id request_id=cfc69ab8f9e5 detector_ms=None
```

**Run 3** — PASS

```
empty body    400 error=invalid_json request_id=8e331cbbc02c detector_ms=None
broken JSON   400 error=invalid_json request_id=a2053a8d4095 detector_ms=None
JSON array    400 error=invalid_json request_id=d18112e97a59 detector_ms=None
JSON string   400 error=invalid_json request_id=d397f145dc50 detector_ms=None
empty object  400 error=missing_creator_id request_id=b82668e7278e detector_ms=None
```
