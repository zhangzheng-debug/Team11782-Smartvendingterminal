#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2.6.8 voice guard mode API test."""

import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:5000"


def request(method, path, body=None):
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.getcode(), json.loads(resp.read().decode("utf-8", "replace") or "{}")
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8", "replace") or "{}")


def post(path, body=None):
    return request("POST", path, body or {})


def get(path):
    return request("GET", path)


def main():
    checks = []
    status, payload = post("/api/speech/guard/start", {})
    checks.append({"name": "start", "pass": status == 200 and payload.get("voice_guard_enabled") is True and payload.get("voice_guard_status") == "listening_wake", "payload": payload})
    status, payload = post("/api/speech/guard/tick", {"text": "乱七八糟"})
    checks.append({"name": "tick no wake no action", "pass": status == 200 and payload.get("executed") is False and payload.get("voice_guard_status") == "listening_wake", "payload": payload})
    status, payload = post("/api/speech/guard/tick", {"text": "小售小售"})
    checks.append({"name": "tick wake only", "pass": status == 200 and payload.get("stage") == "wake_detected" and payload.get("executed") is False, "payload": payload})
    status, payload = post("/api/speech/guard/tick", {"text": "小售小售一"})
    checks.append({"name": "tick wake plus 1", "pass": status == 200 and payload.get("executed") is True and payload.get("intent") == "query_total_price", "payload": payload})
    status, payload = post("/api/scan", {"barcode": "SKU006"})
    checks.append({"name": "scan works while guard running", "pass": status == 200 and payload.get("ok") is True, "payload": payload})
    status, payload = post("/api/speech/guard/cleanup", {})
    checks.append({"name": "cleanup", "pass": status == 200 and payload.get("ok") is True and payload.get("voice_guard_recording_count", 0) <= 5, "payload": payload})
    status, payload = post("/api/speech/guard/stop", {})
    checks.append({"name": "stop", "pass": status == 200 and payload.get("voice_guard_enabled") is False, "payload": payload})
    post("/api/cart/clear", {})
    passed = sum(1 for c in checks if c["pass"])
    failed = len(checks) - passed
    print(json.dumps({"ok": failed == 0, "checks": checks, "summary": {"total": len(checks), "pass": passed, "fail": failed}}, ensure_ascii=False, indent=2))
    print("SPEECH_GUARD_MODE_CHECKS=%d PASS=%d FAIL=%d" % (len(checks), passed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
