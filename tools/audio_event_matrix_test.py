#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys
import time
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:5000"
GOOD_DEV = "plughw:CARD=III,DEV=0"

EVENTS = [
    "system_ready",
    "scan_success",
    "unknown_product",
    "scan_failed",
    "capture_start",
    "capture_success",
    "capture_busy",
    "capture_failed",
    "remove_last",
    "cart_clear",
    "total_query",
    "payment_wait",
    "payment_success",
    "voice_ready",
    "voice_processing",
    "voice_success",
    "voice_failed",
    "input_routed_scan",
]


def post(path, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        BASE + path,
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8", "replace") or "{}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            parsed = json.loads(body or "{}")
        except Exception:
            parsed = {"ok": False, "raw": body}
        return e.code, parsed
    except Exception as e:
        return 0, {"ok": False, "error": str(e)}


def get(path):
    try:
        with urllib.request.urlopen(BASE + path, timeout=8) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8", "replace") or "{}")
    except Exception as e:
        return 0, {"ok": False, "error": str(e)}


def check(name, passed, **extra):
    item = {"name": name, "pass": bool(passed)}
    item.update(extra)
    return item


def main():
    checks = []

    status, data = post("/api/audio/set", {"output_device": GOOD_DEV, "input_device": GOOD_DEV})
    checks.append(check("set good audio device", status == 200 and data.get("ok"), status=status, response=data))

    for event in EVENTS:
        status, data = post("/api/audio/test_output", {"event": event})
        checks.append(check(
            "event " + event,
            status == 200 and data.get("ok") is True and data.get("success") is True,
            status=status,
            audio_ok=data.get("ok"),
            event=data.get("event"),
            message=(data.get("latest_audio") or {}).get("message", ""),
        ))

    status, data = get("/api/state")
    audio = data.get("audio") or {}
    checks.append(check(
        "state exposes latest audio event",
        status == 200 and bool(audio.get("latest_event")),
        status=status,
        latest_event=audio.get("latest_event"),
        latest_success=audio.get("latest_success"),
    ))

    start = time.time()
    burst_ok = True
    for i in range(10):
        status, data = post("/api/audio/test_output", {"event": "scan_success"})
        burst_ok = burst_ok and status == 200 and "ok" in data
    elapsed_ms = int((time.time() - start) * 1000)
    checks.append(check("burst 10 audio events no hang", burst_ok and elapsed_ms < 20000, elapsed_ms=elapsed_ms))

    bad_dev = "plughw:CARD=NOTREAL,DEV=0"
    status, data = post("/api/audio/set", {"output_device": bad_dev, "input_device": GOOD_DEV})
    checks.append(check("set bad output device for negative test", status == 200 and data.get("ok"), status=status))
    status, data = post("/api/audio/test_output", {"event": "scan_success"})
    checks.append(check(
        "bad output device returns JSON no 500",
        status == 200 and data.get("ok") is False,
        status=status,
        response=data,
    ))
    status, data = post("/api/scan", {"barcode": "UNKNOWN_AUDIO_NEGATIVE_TEST"})
    checks.append(check(
        "business survives bad audio output",
        status == 200 and data.get("error_reason") == "unknown_barcode",
        status=status,
        ok=data.get("ok"),
        error_reason=data.get("error_reason"),
        audio_ok=data.get("audio_ok"),
    ))
    post("/api/audio/set", {"output_device": GOOD_DEV, "input_device": GOOD_DEV})

    total = len(checks)
    passed = sum(1 for c in checks if c["pass"])
    result = {"ok": passed == total, "checks": checks, "summary": {"total": total, "pass": passed, "fail": total - passed}}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("AUDIO_EVENT_MATRIX_CHECKS=%d PASS=%d FAIL=%d" % (total, passed, total - passed))
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
