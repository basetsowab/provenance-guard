"""
Internal-failure hardening for /submit. ← CAPSTONE (shape B)

Unit 8 made the service refuse bad *input*. This module covers the service's
own parts breaking:

  • run_with_timeout()  — the detector gets a time limit. A hung or slow model
                          call becomes a 503 instead of a caller left waiting.
  • fault()             — deliberate fault injection, so every bad path can be
                          triggered on demand and tested three times.

Fault injection is OFF unless AI201_FAULT_INJECTION=1. When it's on, a request
can ask for a fault with the header `X-Fault: <name>`, or every request gets
the one named in AI201_FAULT. Names:

    detector_error     the detector raises RuntimeError mid-call
    detector_slow      the detector sleeps past the time limit
    style_error        the style signal raises (an "unexpected" exception)
    audit_unwritable   writing the decision to the audit log raises OSError
"""

import os
import threading
import time

from flask import has_request_context, request

import config

FAULTS = {"detector_error", "detector_slow", "style_error", "audit_unwritable"}


class DetectorTimeout(RuntimeError):
    """The detector didn't answer within config.DETECTOR_TIMEOUT_S."""


def active_fault() -> str | None:
    """The fault this request asked for, or None. Always None unless enabled."""
    if not config.FAULT_INJECTION_ENABLED:
        return None
    name = None
    if has_request_context():
        name = request.headers.get("X-Fault")
    name = (name or os.getenv("AI201_FAULT") or "").strip()
    return name if name in FAULTS else None


def fault(name: str) -> None:
    """Raise or stall here if this request asked for fault `name`."""
    if active_fault() != name:
        return
    if name == "detector_error":
        raise RuntimeError("injected fault: detector_error")
    if name == "detector_slow":
        time.sleep(config.DETECTOR_TIMEOUT_S + 2)
    if name == "style_error":
        raise ZeroDivisionError("injected fault: style_error")
    if name == "audit_unwritable":
        raise OSError("injected fault: audit log is not writable")


def run_with_timeout(fn, *args, timeout: float):
    """
    Run fn(*args) on a separate thread and wait at most `timeout` seconds.

    Returns (result, seconds_taken). Re-raises whatever fn raised. Raises
    DetectorTimeout if it's still running at the deadline.

    A fresh daemon thread per call rather than a pool: a call that hangs keeps
    its own thread busy, but can't starve the next request of a worker. The
    hung thread is abandoned, not killed — Python can't kill a thread — so it
    finishes (or doesn't) in the background.
    """
    box: dict = {}
    # The request context doesn't follow us onto the new thread, so read the
    # fault name now and hand it over.
    injected = active_fault()

    def target():
        try:
            if injected == "detector_error":
                raise RuntimeError("injected fault: detector_error")
            if injected == "detector_slow":
                time.sleep(timeout + 2)
            box["result"] = fn(*args)
        except BaseException as exc:  # noqa: BLE001 — handed back to the caller
            box["error"] = exc

    started = time.perf_counter()
    worker = threading.Thread(target=target, daemon=True, name="detector-call")
    worker.start()
    worker.join(timeout)
    elapsed = time.perf_counter() - started

    if worker.is_alive():
        raise DetectorTimeout(
            f"detector took longer than {timeout:.0f}s and was abandoned"
        )
    if "error" in box:
        raise box["error"]
    return box["result"], elapsed
