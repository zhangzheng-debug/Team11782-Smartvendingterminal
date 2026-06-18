#!/usr/bin/env python3
import json
import sys
import time
import urllib.error
import urllib.request


BASE = "http://127.0.0.1:5000"


def req(method, path, body=None, timeout=12):
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            status = resp.getcode()
            raw = resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        status = exc.code
        raw = exc.read().decode("utf-8", "replace")
    payload = json.loads(raw or "{}")
    return status, payload


def main():
    checks = []
    time.sleep(2.0)
    successes = 0
    accepted_errors = {"capture_busy", "capture_cooldown", "capture_timeout", "capture_failed"}

    for i in range(10):
        status, payload = req("POST", "/api/capture", {}, timeout=15)
        reason = payload.get("error_reason") or payload.get("error") or ""
        passed = status == 200 and "ok" in payload and "success" in payload and reason in accepted_errors.union({""})
        passed = passed and "capture_count" in payload and "cleanup_deleted_count" in payload
        if payload.get("ok") is True:
            successes += 1
            passed = passed and bool(payload.get("image_path")) and bool(payload.get("image_url"))
        else:
            passed = passed and reason in accepted_errors
        checks.append({
            "step": "capture_%02d" % (i + 1),
            "pass": bool(passed),
            "status": status,
            "ok": payload.get("ok"),
            "success": payload.get("success"),
            "error_reason": reason,
            "message": payload.get("message"),
            "capture_count": payload.get("capture_count"),
            "cleanup_deleted_count": payload.get("cleanup_deleted_count"),
        })

    status, state = req("GET", "/api/state", None)
    state_pass = status == 200 and state.get("ok") is True and bool(state.get("latest_capture"))
    state_pass = state_pass and "capture_count" in state and "capture_total_size_mb" in state
    checks.append({
        "step": "state_after_capture_stress",
        "pass": bool(state_pass),
        "status": status,
        "latest_capture": state.get("latest_capture"),
        "capture_count": state.get("capture_count"),
        "capture_total_size_mb": state.get("capture_total_size_mb"),
    })

    status, cleanup = req("POST", "/api/captures/cleanup", {})
    cleanup_pass = status == 200 and cleanup.get("ok") is True and "deleted_count" in cleanup
    cleanup_pass = cleanup_pass and "remaining_count" in cleanup and "total_size_mb" in cleanup
    checks.append({
        "step": "captures_cleanup_api",
        "pass": bool(cleanup_pass),
        "status": status,
        "deleted_count": cleanup.get("deleted_count"),
        "remaining_count": cleanup.get("remaining_count"),
        "total_size_mb": cleanup.get("total_size_mb"),
        "message": cleanup.get("message"),
    })

    no_500 = all(int(c.get("status") or 0) != 500 for c in checks)
    enough_success = successes >= 1
    passes = sum(1 for c in checks if c["pass"])
    fails = len(checks) - passes
    ok = no_500 and enough_success and fails == 0
    result = {
        "ok": ok,
        "successes": successes,
        "no_500": no_500,
        "checks": checks,
        "summary": {"total": len(checks), "pass": passes, "fail": fails},
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("CAPTURE_STRESS_CHECKS=%d PASS=%d FAIL=%d SUCCESSES=%d NO_500=%s" % (len(checks), passes, fails, successes, no_500))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
