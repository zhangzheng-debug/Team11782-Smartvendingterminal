#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2.6.9-B speech error visibility API test."""

import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:5000"


def post(path, body=None):
    data = json.dumps(body or {}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(BASE + path, data=data, headers={"Content-Type": "application/json", "Accept": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            return resp.getcode(), json.loads(resp.read().decode("utf-8", "replace") or "{}")
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8", "replace") or "{}")


def main():
    checks = []
    status, p = post("/api/speech/session_step", {"reset": True, "text": "二"})
    checks.append({"name": "no wake number feedback", "pass": status == 200 and p.get("executed") is False and bool(p.get("message")), "payload": p})
    post("/api/speech/cancel", {})
    status, p = post("/api/speech/session_step", {"button_wake": True, "text": "我要结账"})
    checks.append({"name": "button natural language rejected", "pass": status == 200 and p.get("executed") is False and p.get("error_reason") in {"natural_language_not_allowed", "no_number_detected"} and bool(p.get("message")), "payload": p})
    post("/api/speech/cancel", {})
    status, p = post("/api/speech/session_step", {"button_wake": True, "text": "乱七八糟"})
    checks.append({"name": "button unclear text feedback", "pass": status == 200 and p.get("executed") is False and p.get("error_reason") == "no_number_detected" and bool(p.get("message")), "payload": p})
    post("/api/speech/guard/start", {})
    status, p = post("/api/speech/guard/tick", {"text": "无关内容"})
    checks.append({"name": "guard no wake records feedback", "pass": status == 200 and p.get("executed") is False and bool(p.get("message")), "payload": p})
    post("/api/speech/guard/stop", {})
    pcount = sum(1 for c in checks if c["pass"])
    f = len(checks) - pcount
    print(json.dumps({"ok": f == 0, "checks": checks, "summary": {"total": len(checks), "pass": pcount, "fail": f}}, ensure_ascii=False, indent=2))
    print("SPEECH_ERROR_FEEDBACK_CHECKS=%d PASS=%d FAIL=%d" % (len(checks), pcount, f))
    return 0 if f == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
