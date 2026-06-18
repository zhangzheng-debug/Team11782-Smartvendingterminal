#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2.6.9 button voice path must parse digits only."""

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
    cases = [
        ("一", "1", "query_total_price", True),
        ("yi", "1", "query_total_price", True),
        ("四", "4", "checkout", True),
        ("shi", "4", "checkout", True),
        ("小售小售一", "1", "query_total_price", True),
        ("我要结账", "", "", False),
        ("删除上一件", "", "", False),
        ("乱七八糟", "", "", False),
    ]
    for text, digit, intent, should_execute in cases:
        post("/api/speech/cancel", {})
        post("/api/cart/clear", {})
        if intent in {"remove_last", "clear_cart", "checkout"}:
            post("/api/cart/add", {"product_id": "SKU006", "quantity": 1})
        status, payload = post("/api/speech/session_step", {"button_wake": True, "text": text})
        got_digit = payload.get("digit") or (payload.get("numeric") or {}).get("digit") or ""
        got_intent = payload.get("intent") or (payload.get("numeric") or {}).get("intent") or ""
        executed = payload.get("executed") is True
        passed = status == 200 and executed == should_execute
        if should_execute:
            passed = passed and got_digit == digit and got_intent == intent
        else:
            passed = passed and payload.get("error_reason") in {"no_number_detected", "natural_language_not_allowed", None}
        checks.append({"name": text, "pass": passed, "status": status, "digit": got_digit, "intent": got_intent, "executed": executed, "message": payload.get("message", ""), "error_reason": payload.get("error_reason")})
    post("/api/cart/clear", {})
    passed = sum(1 for c in checks if c["pass"])
    failed = len(checks) - passed
    print(json.dumps({"ok": failed == 0, "checks": checks, "summary": {"total": len(checks), "pass": passed, "fail": failed}}, ensure_ascii=False, indent=2))
    print("SPEECH_NUMERIC_ONLY_BUTTON_CHECKS=%d PASS=%d FAIL=%d" % (len(checks), passed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
