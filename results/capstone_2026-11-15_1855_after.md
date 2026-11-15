# Capstone run log — after

- Produced by `capstone_eval.py::main`, 2026-11-15 18:55
- Detector timeout: 3s · rate limiting ON

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| C1. Slow model → 503 within 11 s | 3/3 | PASS (503 in 3.02s) | PASS (503 in 3.01s) | PASS (503 in 3.01s) | MET (3/3) |
| C2. Model crash → clear error, server stays up | 3/3 | PASS (503 detector_failed, ping 200) | PASS (503 detector_failed, ping 200) | PASS (503 detector_failed, ping 200) | MET (3/3) |
| C3. Processing failure → in the audit log | 3/3 | PASS (3/3 logged) | PASS (3/3 logged) | PASS (3/3 logged) | MET (3/3) |
| C4. Invalid endpoint → 404 | 3/3 | PASS (GET 404, POST 404) | PASS (GET 404, POST 404) | PASS (GET 404, POST 404) | MET (3/3) |
| C5. Empty/malformed JSON → 4xx with reason, never reaches classifier | 3/3 | PASS (5/5 4xx, 0 reached detector) | PASS (5/5 4xx, 0 reached detector) | PASS (5/5 4xx, 0 reached detector) | MET (3/3) |

## Raw output, every trial

### C1. Slow model → 503 within 11 s
**Run 1** — PASS

```
503 3.02s {"error": "detector_timeout", "message": "The checker took longer than 3 seconds, so this piece wasn't checked and nothing was recorded against it. Try again in a minute.", "request_id": "789c94728bec"}
```

**Run 2** — PASS

```
503 3.01s {"error": "detector_timeout", "message": "The checker took longer than 3 seconds, so this piece wasn't checked and nothing was recorded against it. Try again in a minute.", "request_id": "593559f4e42a"}
```

**Run 3** — PASS

```
503 3.01s {"error": "detector_timeout", "message": "The checker took longer than 3 seconds, so this piece wasn't checked and nothing was recorded against it. Try again in a minute.", "request_id": "f761d866ea6f"}
```

### C2. Model crash → clear error, server stays up
**Run 1** — PASS

```
503 {"error": "detector_failed", "message": "The checker hit an error on this piece, so it wasn't checked and nothing was recorded against it. Try again; if it keeps happening, the text itself may be the trigger.", "request_id": "24f3f7bead3f"}
/ping -> 200 {
  "ok": true,
  "service": "provenance-guard",
  "you_sent": "still up?"
}
```

**Run 2** — PASS

```
503 {"error": "detector_failed", "message": "The checker hit an error on this piece, so it wasn't checked and nothing was recorded against it. Try again; if it keeps happening, the text itself may be the trigger.", "request_id": "aead3f0d06e6"}
/ping -> 200 {
  "ok": true,
  "service": "provenance-guard",
  "you_sent": "still up?"
}
```

**Run 3** — PASS

```
503 {"error": "detector_failed", "message": "The checker hit an error on this piece, so it wasn't checked and nothing was recorded against it. Try again; if it keeps happening, the text itself may be the trigger.", "request_id": "35af51d107ef"}
/ping -> 200 {
  "ok": true,
  "service": "provenance-guard",
  "you_sent": "still up?"
}
```

### C3. Processing failure → in the audit log
**Run 1** — PASS

```
detector_error: {"timestamp": "2026-11-15T23:52:52+00:00", "creator_id": "c3_1_fff32f_0", "event": "rejected", "status": "rejected", "reason": "detector_failed", "http_status": 503, "detail": "RuntimeError: injected fault: detector_error", "text_length": 390}
style_error: {"timestamp": "2026-11-15T23:52:52+00:00", "creator_id": "c3_1_fff32f_1", "event": "rejected", "status": "rejected", "reason": "internal_error", "http_status": 500, "route": "/submit", "detail": "ZeroDivisionError: injected fault: style_error"}
detector_slow: {"timestamp": "2026-11-15T23:52:55+00:00", "creator_id": "c3_1_fff32f_2", "event": "rejected", "status": "rejected", "reason": "detector_timeout", "http_status": 503, "detail": "detector took longer than 3s and was abandoned", "text_length": 390}
```

**Run 2** — PASS

```
detector_error: {"timestamp": "2026-11-15T23:54:04+00:00", "creator_id": "c3_2_3ad675_0", "event": "rejected", "status": "rejected", "reason": "detector_failed", "http_status": 503, "detail": "RuntimeError: injected fault: detector_error", "text_length": 390}
style_error: {"timestamp": "2026-11-15T23:54:04+00:00", "creator_id": "c3_2_3ad675_1", "event": "rejected", "status": "rejected", "reason": "internal_error", "http_status": 500, "route": "/submit", "detail": "ZeroDivisionError: injected fault: style_error"}
detector_slow: {"timestamp": "2026-11-15T23:54:07+00:00", "creator_id": "c3_2_3ad675_2", "event": "rejected", "status": "rejected", "reason": "detector_timeout", "http_status": 503, "detail": "detector took longer than 3s and was abandoned", "text_length": 390}
```

**Run 3** — PASS

```
detector_error: {"timestamp": "2026-11-15T23:55:15+00:00", "creator_id": "c3_3_e2e953_0", "event": "rejected", "status": "rejected", "reason": "detector_failed", "http_status": 503, "detail": "RuntimeError: injected fault: detector_error", "text_length": 390}
style_error: {"timestamp": "2026-11-15T23:55:15+00:00", "creator_id": "c3_3_e2e953_1", "event": "rejected", "status": "rejected", "reason": "internal_error", "http_status": 500, "route": "/submit", "detail": "ZeroDivisionError: injected fault: style_error"}
detector_slow: {"timestamp": "2026-11-15T23:55:18+00:00", "creator_id": "c3_3_e2e953_2", "event": "rejected", "status": "rejected", "reason": "detector_timeout", "http_status": 503, "detail": "detector took longer than 3s and was abandoned", "text_length": 390}
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
empty body    400 error=invalid_json request_id=3bc1cf5d841c detector_ms=None
broken JSON   400 error=invalid_json request_id=93672ad21ae5 detector_ms=None
JSON array    400 error=invalid_json request_id=ad3a305b95a3 detector_ms=None
JSON string   400 error=invalid_json request_id=aaf7761ececb detector_ms=None
empty object  400 error=missing_creator_id request_id=4d6a56cbc138 detector_ms=None
```

**Run 2** — PASS

```
empty body    400 error=invalid_json request_id=09576217d5db detector_ms=None
broken JSON   400 error=invalid_json request_id=52b4782eb81c detector_ms=None
JSON array    400 error=invalid_json request_id=5f5ff6d897e0 detector_ms=None
JSON string   400 error=invalid_json request_id=a64d98374318 detector_ms=None
empty object  400 error=missing_creator_id request_id=d054279ae8dc detector_ms=None
```

**Run 3** — PASS

```
empty body    400 error=invalid_json request_id=c8df9eee1921 detector_ms=None
broken JSON   400 error=invalid_json request_id=9798df7a2045 detector_ms=None
JSON array    400 error=invalid_json request_id=bce1c1acfb41 detector_ms=None
JSON string   400 error=invalid_json request_id=d922fce7d834 detector_ms=None
empty object  400 error=missing_creator_id request_id=cc9dd44b5c9a detector_ms=None
```
