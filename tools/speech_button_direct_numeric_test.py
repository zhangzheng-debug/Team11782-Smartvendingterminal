#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2.6.8 manual voice button means already woken."""

import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:5000"


def post(path, body=None):
    data = json.dumps(body or {}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(BASE + path, data=data, headers={"Accept": "application/json", "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.getcode(), json.loads(resp.read().decode("utf-8", "replace") or "{}")
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8", "replace") or "{}")


def main():
    checks = []
    cases = [
        ("一", "1", "query_total_price"),
        ("二", "2", "remove_last"),
        ("四", "4", "checkout"),
        ("零", "0", "cancel"),
        ("小售小售一", "1", "query_total_price"),
    ]
    for text, digit, intent in cases:
        post("/api/speech/cancel", {})
        post("/api/cart/clear", {})
        if intent in {"remove_last", "checkout"}:
            post("/api/cart/add", {"product_id": "SKU006", "quantity": 1})
        status, payload = post("/api/speech/session_step", {"button_wake": True, "text": text})
        got_digit = payload.get("digit") or (payload.get("numeric") or {}).get("digit")
        got_intent = payload.get("intent") or (payload.get("numeric") or {}).get("intent")
        checks.append({
            "name": "button_wake + %s" % text,
            "pass": status == 200 and got_digit == digit and got_intent == intent,
            "status": status,
            "digit": got_digit,
            "intent": got_intent,
            "message": payload.get("message"),
        })
    post("/api/cart/clear", {})
    passed = sum(1 for c in checks if c["pass"])
    failed = len(checks) - passed
    print(json.dumps({"ok": failed == 0, "checks": checks, "summary": {"total": len(checks), "pass": passed, "fail": failed}}, ensure_ascii=False, indent=2))
    print("SPEECH_BUTTON_DIRECT_NUMERIC_CHECKS=%d PASS=%d FAIL=%d" % (len(checks), passed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
