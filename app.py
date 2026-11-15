#!/usr/bin/env python3
"""
Provenance Guard — the web service.

    python app.py

Then, in another terminal:

    curl -X POST http://127.0.0.1:5000/ping \
      -H "Content-Type: application/json" \
      -d '{"message": "hello"}'

That's the example route. It works right now, before you've written anything.
**Leave it alone** — it's your control. When something breaks later, check that
`/ping` still answers: if it does, the problem is in your handler; if it
doesn't, it's the service itself.

Routes:

    POST /ping        the worked example. Already works. Don't edit it
    POST /submit      ← YOU BUILD THIS (Milestone 3, 4, 5)
    POST /appeal      ← YOU BUILD THIS (Milestone 5)
    GET  /log         the audit log. Already works
    GET  /health      is the service up, and is the model loaded
"""

import uuid

from flask import Flask, g, jsonify, request

import audit
import config
import guard

app = Flask(__name__)

# Refuse request bodies far bigger than any allowed text before parsing them.
app.config["MAX_CONTENT_LENGTH"] = 1_000_000  # bytes


@app.errorhandler(413)
def body_too_large(exc):
    """A body over MAX_CONTENT_LENGTH gets a JSON answer and a log entry."""
    audit.log_rejection(creator_id="unknown", reason="body_too_large", http_status=413)
    return jsonify({
        "error": "body_too_large",
        "message": f"Request is too large. 'text' must be at most {config.MAX_TEXT_CHARS} characters.",
    }), 413


# ── Rate limiting — UNIT 8 ────────────────────────────────────────────────────
# Off until you turn it on. In unit 8, Milestone 1:
#
#   1. Set RATE_LIMITING_ENABLED = True in config.py (or AI201_RATE_LIMITS=1)
#   2. Choose your numbers there
#   3. Uncomment the @limiter.limit(...) line on /submit below
#
# The order doesn't matter. While limiting is off, that decorator is a no-op
# that quietly does nothing, so uncommenting it early costs you nothing — but
# it also means no 429 until you've done step 1.
#
# The storage backend is preconfigured, which stops Flask-Limiter printing a
# warning on every start. In-memory is right for one laptop and wrong for
# anything real — a restart forgets every count.

class _LimiterOff:
    """
    Stands in for the real limiter while rate limiting is off.

    It makes @limiter.limit(...) a decorator that returns the route
    untouched, so uncommenting the line before you flip the setting is
    harmless instead of a crash on startup.
    """

    def limit(self, *args, **kwargs):
        return lambda view: view


limiter = _LimiterOff()
if config.RATE_LIMITING_ENABLED:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    def rate_limit_key():
        """
        Who a request counts against.

        Falling back to the caller's address is the easy version. Unit 8's
        stretch asks about per-creator limits instead — and the difference
        matters: one script can look like a thousand callers, and one household
        can look like one.
        """
        payload = request.get_json(silent=True)
        # A body that parses as JSON but isn't an object — a bare list or
        # string — has no .get. Without this guard the key function raises
        # BEFORE the route runs, and a malformed request becomes a 500 that
        # looks like your handler crashed when your handler never ran.
        if not isinstance(payload, dict):
            return get_remote_address()
        creator = payload.get("creator_id")
        return creator if isinstance(creator, str) and creator.strip() else get_remote_address()

    limiter = Limiter(
        key_func=rate_limit_key,
        app=app,
        storage_uri=config.RATE_LIMIT_STORAGE,
        default_limits=[],
    )

    @app.errorhandler(429)
    def rate_limited(exc):
        """
        A rejected request still leaves a trace.

        ⚠️ An attack that shows up only as an absence is one you'll never find.
        """
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            payload = {}
        audit.log_rejection(
            creator_id=payload.get("creator_id", "unknown"),
            reason="rate_limited",
            limit=str(exc.description),
        )
        return jsonify({
            "error": "rate_limited",
            "message": "Too many submissions. Try again shortly.",
            "limit": str(exc.description),
        }), 429


# ── The worked example. Already works. Don't edit. ────────────────────────────

@app.post("/ping")
def ping():
    """
    Everything a route needs, in six lines.

    JSON arrives as a dict. You pull things out of it. You return a dict and
    the framework turns it into a response. That's the whole idea.
    """
    payload = request.get_json(silent=True) or {}
    return jsonify({
        "ok": True,
        "you_sent": payload.get("message"),
        "service": "provenance-guard",
    })


@app.get("/health")
def health():
    """Is the service up, and has the model been downloaded yet?"""
    import detector

    loaded = detector._model is not None
    return jsonify({
        "ok": True,
        "detector_model": config.DETECTOR_MODEL,
        "detector_loaded": loaded,
        "rate_limiting": config.RATE_LIMITING_ENABLED,
        "log_entries": len(audit.read_entries()),
    })


# ── YOU BUILD THIS ────────────────────────────────────────────────────────────

@app.post("/submit")
@limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute;{config.RATE_LIMIT_PER_DAY}/day")
def submit():
    """
    Take a piece of text, decide about it, log the decision, answer.
    ← TODO — Milestones 3, 4 and 5

    Expects JSON:
        {"text": "...", "creator_id": "..."}

    Should return JSON with, at minimum:
        {"content_id": "...", "guess": "...", "confidence": 0.0, "label": "...",
         "model_score": 0.0, "style_score": 0.0}

    ⚠️ **Both signal scores go in the response, not just the log.** Unit 8's
    `run_attacks.py` and `run_eval.py` read `model_score` and `style_score`
    straight off this response and put them in your reports. Leave them out and
    every row of next unit's evidence says `null` — which is exactly the
    diagnostic you need to name a stage and a mechanism. You do not want to
    find that out after running the attack set.

    ─────────────────────────────────────────────────────────────────────────
    Build it in three passes. Do not skip ahead — the ordering is how you tell
    a broken route from a broken signal.

    **Milestone 3 — the route answers.**
      1. Return a hardcoded response. Confirm `curl` gets it back before you
         add any logic at all.
      2. Then pull `text` and `creator_id` out of the payload.
      3. Then call ONE signal — `detector.model_signal(text)` — and put the
         real number in. Leave confidence and label as placeholders.
      4. Log every submission with `audit.log_decision(...)`. The content_id
         matters: `/appeal` needs it, and a student who skips it rebuilds this
         whole flow later.

    **Milestone 4 — the second signal and the score.**
      5. Add `stylometry.style_signal(text)`.
      6. Combine them with `scoring.combine_signals(...)`.
      7. Log BOTH signal scores alongside the combined one, and put them in the
         response too. Next unit you can't diagnose anything without them.

    **Milestone 5 — the label.**
      8. `scoring.score_to_label(...)` and put the real label in the response.

    ─────────────────────────────────────────────────────────────────────────
    Worth deciding early, because unit 8's attack set will decide it for you:
    what should this do when `text` is missing, empty, or enormous? A crash on
    a malformed input is one of the most common real failures there is.
    """
    import detector
    import scoring
    import stylometry

    payload = request.get_json(silent=True)

    # ── Bad input: refuse with a reason and leave a trace, never crash ──
    if not isinstance(payload, dict):
        return _reject("unknown", "invalid_json", 400,
                       "Send a JSON object with 'text' and 'creator_id'.")

    creator_id = payload.get("creator_id")
    text = payload.get("text")

    if not isinstance(creator_id, str) or not creator_id.strip():
        return _reject("unknown", "missing_creator_id", 400,
                       "'creator_id' is required and must be a non-empty string.")
    creator_id = creator_id.strip()
    if len(creator_id) > config.MAX_CREATOR_ID_CHARS:
        return _reject(creator_id[:config.MAX_CREATOR_ID_CHARS], "creator_id_too_long", 400,
                       f"'creator_id' must be at most {config.MAX_CREATOR_ID_CHARS} characters.")

    if not isinstance(text, str) or not text.strip():
        return _reject(creator_id, "missing_text", 400,
                       "'text' is required and must be a non-empty string.")
    if len(text) > config.MAX_TEXT_CHARS:
        return _reject(creator_id, "text_too_long", 413,
                       f"'text' must be at most {config.MAX_TEXT_CHARS} characters.",
                       text_length=len(text))
    if len(stylometry.words(text)) < config.MIN_WORDS:
        return _reject(creator_id, "text_too_short", 422,
                       f"'text' needs at least {config.MIN_WORDS} words to be checked.",
                       text_length=len(text))

    # ── Signal one: how predictable the text is to a language model ──
    # Capstone: the call runs under a time limit, and any exception from it is
    # a named 503 — not Flask's HTML 500, and not a caller left waiting.
    try:
        # A cold load (10-20s) isn't a hang, so it happens outside the limit.
        if detector._model is None:
            detector.warm_up()
        model_score, detector_s = guard.run_with_timeout(
            detector.model_signal, text, timeout=config.DETECTOR_TIMEOUT_S)
        g.detector_ms = round(detector_s * 1000)
    except detector.DetectorUnavailable as exc:
        return _reject(creator_id, "detector_unavailable", 503,
                       "The checker isn't available right now. Try again shortly.",
                       detail=str(exc))
    except ValueError:
        return _reject(creator_id, "text_too_short", 422,
                       "'text' is too short to check. A few sentences at least.",
                       text_length=len(text))
    except guard.DetectorTimeout as exc:
        return _reject(creator_id, "detector_timeout", 503,
                       f"The checker took longer than {config.DETECTOR_TIMEOUT_S:.0f} "
                       "seconds, so this piece wasn't checked and nothing was "
                       "recorded against it. Try again in a minute.",
                       detail=str(exc), text_length=len(text))
    except Exception as exc:  # noqa: BLE001 — any other detector crash
        return _reject(creator_id, "detector_failed", 503,
                       "The checker hit an error on this piece, so it wasn't "
                       "checked and nothing was recorded against it. Try again; "
                       "if it keeps happening, the text itself may be the trigger.",
                       detail=f"{type(exc).__name__}: {exc}", text_length=len(text))

    # ── Signal two: the shape of the text ──
    guard.fault("style_error")   # capstone test hook; a no-op unless injected
    style_score = stylometry.style_signal(text)

    # ── One number, then words a person can read ──
    combined = scoring.combine_signals(model_score, style_score)
    guess, label = scoring.score_to_label(combined)

    content_id = str(uuid.uuid4())
    # Capstone: a decision that never reached the audit log can't be appealed
    # (/appeal looks the id up there), so handing out its content_id would be
    # a promise the service can't keep. Refuse instead, and say so.
    try:
        guard.fault("audit_unwritable")
        audit.log_decision(
            content_id=content_id,
            creator_id=creator_id,
            guess=guess,
            model_score=model_score,
            style_score=style_score,
            combined_score=combined,
            label=label,
            status="decided",
            text_length=len(text),
        )
    except OSError as exc:
        g.audit_error = f"{type(exc).__name__}: {exc}"
        g.outcome = {"error": "audit_unavailable"}
        return jsonify({
            "error": "audit_unavailable",
            "message": ("Your text was checked, but the result couldn't be saved, "
                        "so no result is being given — an unsaved result couldn't "
                        "be appealed. Nothing was recorded against you. Try again "
                        "in a minute."),
            "request_id": g.get("request_id"),
        }), 503

    g.outcome = {"content_id": content_id, "guess": guess,
                 "combined_score": combined, "model_score": model_score,
                 "style_score": style_score}

    # `confidence` is the combined score: 0.0 = confidently human,
    # 1.0 = confidently AI, middle values = unsure.
    return jsonify({
        "content_id": content_id,
        "creator_id": creator_id,
        "guess": guess,
        "confidence": combined,
        "label": label,
        "model_score": model_score,
        "style_score": style_score,
        "status": "decided",
    })


def _reject(creator_id, reason, http_status, message, **extra):
    """Log a refused request, then tell the caller why it was refused."""
    g.outcome = {"error": reason}
    try:
        guard.fault("audit_unwritable")
        audit.log_rejection(creator_id=creator_id, reason=reason,
                            http_status=http_status, **extra)
    except OSError as exc:
        # The refusal still goes out; the request log keeps the record.
        g.audit_error = f"{type(exc).__name__}: {exc}"
    return jsonify({"error": reason, "message": message}), http_status


# ── Capstone: nothing leaves as Flask's HTML error page ──────────────────────

@app.errorhandler(Exception)
def unexpected_error(exc):
    """
    Anything a route didn't catch.

    Without this an exception anywhere in /submit — the style signal, the
    scoring — answers with Flask's HTML 500 page and leaves no audit entry.
    Now it answers JSON with a request_id the caller can quote, and it's
    recorded in both logs. HTTP errors (404, 405, ...) keep their own status
    but answer in JSON too.
    """
    from werkzeug.exceptions import HTTPException

    if isinstance(exc, HTTPException):
        g.outcome = {"error": exc.name.lower().replace(" ", "_")}
        return jsonify({"error": g.outcome["error"],
                        "message": exc.description}), exc.code

    detail = f"{type(exc).__name__}: {exc}"
    g.outcome = {"error": "internal_error"}
    g.exception = detail
    payload = request.get_json(silent=True)
    creator = payload.get("creator_id") if isinstance(payload, dict) else None
    try:
        audit.log_rejection(creator_id=creator if isinstance(creator, str) else "unknown",
                            reason="internal_error", http_status=500,
                            route=request.path, detail=detail)
    except OSError as log_exc:
        g.audit_error = f"{type(log_exc).__name__}: {log_exc}"
    app.logger.exception("unhandled error on %s", request.path)
    return jsonify({
        "error": "internal_error",
        "message": ("Something went wrong inside the service, so this piece "
                    "wasn't checked and nothing was recorded against you. Try "
                    "again; if it keeps happening, quote the request_id."),
        "request_id": g.get("request_id"),
    }), 500


@app.post("/appeal")
def appeal():
    """
    A writer says you got it wrong. ← TODO — Milestone 5

    Expects JSON:
        {"content_id": "...", "reasoning": "..."}

    Should:
      1. Check the content_id actually exists — `audit.entries_for(id)` tells
         you. A typo here fails silently and looks like a broken endpoint,
         which is the single most common way this milestone eats an hour.
      2. Record the appeal with `audit.log_appeal(...)`, which moves the item
         to `under_review`.
      3. Confirm to the writer. No automatic re-checking needed.

    This is the smallest endpoint in the project and the one that matters most
    to the person on the other end. It's the only thing standing between a
    wrong accusation and nothing at all.
    """
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "invalid_json",
                        "message": "Send a JSON object with 'content_id' and 'reasoning'."}), 400

    content_id = payload.get("content_id")
    reasoning = payload.get("reasoning")

    if not isinstance(content_id, str) or not content_id.strip():
        return jsonify({"error": "missing_content_id",
                        "message": "'content_id' is required."}), 400
    content_id = content_id.strip()

    if not isinstance(reasoning, str) or not reasoning.strip():
        return jsonify({"error": "missing_reasoning",
                        "message": "Tell us briefly why you think the result is wrong."}), 400
    reasoning = reasoning.strip()
    if len(reasoning) > config.MAX_REASONING_CHARS:
        return jsonify({"error": "reasoning_too_long",
                        "message": f"Please keep it under {config.MAX_REASONING_CHARS} characters."}), 413

    # Only an original decision counts as "exists". Appeal entries alone don't.
    history = audit.entries_for(content_id)
    decision = next((e for e in history if e.get("event") is None), None)
    if decision is None:
        return jsonify({"error": "content_not_found",
                        "message": f"No submission found with content_id '{content_id}'."}), 404

    entry = audit.log_appeal(
        content_id=content_id,
        creator_id=decision.get("creator_id", "unknown"),
        reasoning=reasoning,
    )

    return jsonify({
        "content_id": content_id,
        "status": "under_review",
        "previous_status": history[-1].get("status"),
        "original_guess": decision.get("guess"),
        "appealed_at": entry["timestamp"],
        "message": (
            "Thanks. Your appeal has been recorded and a person will review "
            "this piece. Nothing about it changes while that happens."
        ),
    })


# ── Already works ─────────────────────────────────────────────────────────────

@app.get("/log")
def get_log():
    """
    The audit log, most recent last.

        curl "http://127.0.0.1:5000/log?limit=10"

    You need this in unit 8 to paste entries into your README, and you need it
    now to see whether your logging is actually working.
    """
    limit = request.args.get("limit", type=int)
    entries = audit.read_entries(limit=limit)
    return jsonify({"count": len(entries), "entries": entries})


def main():
    print(f"Provenance Guard on http://{config.HOST}:{config.PORT}")
    print(f"  detector model:  {config.DETECTOR_MODEL}")
    print(f"  rate limiting:   {'ON' if config.RATE_LIMITING_ENABLED else 'off (unit 8)'}")
    print(f"  audit log:       {config.AUDIT_LOG}")
    print()
    print("Check it's alive:")
    print(f'  curl -X POST http://{config.HOST}:{config.PORT}/ping \\')
    print('    -H "Content-Type: application/json" \\')
    print("    -d '{\"message\": \"hello\"}'")
    print()
    if config.FAULT_INJECTION_ENABLED:
        print("  ⚠️  fault injection ON — requests may send X-Fault (see guard.py)")
    if config.WARM_UP_ON_START:
        # Load the model now, so the detector time limit only ever sees warm
        # calls. A cold load is 10-20s and would look exactly like a hang.
        import detector
        try:
            print(f"  warming up: {detector.warm_up()}")
        except detector.DetectorUnavailable as exc:
            print(f"  warm-up failed, /submit will answer 503: {exc}")
    print()
    # debug=True hands out an interactive debugger, so it's local-only — see config.py
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)


if __name__ == "__main__":
    main()
