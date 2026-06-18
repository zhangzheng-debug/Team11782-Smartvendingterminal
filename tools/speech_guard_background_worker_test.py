#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2.6.10 voice guard background/tick behavior test."""

import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:5000"


def request(method, path, body=None, timeout=35):
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.getcode(), json.loads(resp.read().decode("utf-8", "replace") or "{}")
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8", "replace") or "{}")


def get(path):
    return request("GET", path)


def post(path, body=None):
    return request("POST", path, body or {})


def main():
    checks = []
    post("/api/speech/guard/stop", {})
    post("/api/cart/clear", {})

    status, start = post("/api/speech/guard/start", {})
    checks.append({"name": "guard starts", "pass": status == 200 and start.get("voice_guard_enabled") is True, "payload": start})

    status, state = get("/api/state")
    checks.append({"name": "state readable while guard running", "pass": status == 200 and state.get("voice_guard_enabled") is True, "payload": {"status": state.get("voice_guard_status")}})

    status, scan = post("/api/scan", {"barcode": "SKU006"})
    checks.append({"name": "scan works while guard running", "pass": status == 200 and scan.get("success") is True, "payload": scan})

    status, tick = post("/api/speech/guard/tick", {"text": "四号结账"})
    checks.append({"name": "no wake no action", "pass": status == 200 and tick.get("executed") is False, "payload": tick})

    status, tick = post("/api/speech/guard/tick", {"text": "小售小售一号查询总价"})
    checks.append({"name": "wake numbered phrase executes", "pass": status == 200 and tick.get("executed") is True and tick.get("digit") == "1", "payload": tick})

    status, cleanup = post("/api/speech/guard/cleanup", {})
    checks.append({"name": "recording cleanup bounded", "pass": status == 200 and cleanup.get("ok") is True and int(cleanup.get("voice_guard_recording_count", 0)) <= 5, "payload": cleanup})

    status, stop = post("/api/speech/guard/stop", {})
    checks.append({"name": "guard stops", "pass": status == 200 and stop.get("voice_guard_enabled") is False, "payload": stop})

    post("/api/cart/clear", {})
    passed = sum(1 for c in checks if c["pass"])
    failed = len(checks) - passed
    print(json.dumps({"ok": failed == 0, "checks": checks, "summary": {"total": len(checks), "pass": passed, "fail": failed}}, ensure_ascii=False, indent=2))
    print("SPEECH_GUARD_BACKGROUND_WORKER_CHECKS=%d PASS=%d FAIL=%d" % (len(checks), passed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

