#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2.6.9 inline wake + numeric/action execution matrix."""

import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:5000"


def req(method, path, body=None):
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    r = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=25) as resp:
            return resp.getcode(), json.loads(resp.read().decode("utf-8", "replace") or "{}")
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8", "replace") or "{}")


def post(path, body=None):
    return req("POST", path, body or {})


def main():
    checks = []
    cases = [
        ("小售小售1", "1", "query_total_price", True),
        ("小搜小搜1", "1", "query_total_price", True),
        ("小受小受一", "1", "query_total_price", True),
        ("小售小售幺", "1", "query_total_price", True),
        ("小售小售我要结账", "4", "checkout", True),
        ("小售小售四", "4", "checkout", True),
        ("小售小售是", "4", "checkout", True),
        ("小售小售二", "2", "remove_last", True),
        ("小售小售删除上一件", "2", "remove_last", True),
        ("小售小售清空购物车", "3", "clear_cart", True),
        ("小售小售拍照", "5", "camera_capture", True),
        ("小售小售", "1", "query_total_price", True),
        ("二", "", "", False),
        ("我要结账", "", "", False),
    ]
    for text, digit, intent, should_execute in cases:
        post("/api/speech/cancel", {})
        post("/api/cart/clear", {})
        if intent in {"remove_last", "clear_cart", "checkout"}:
            post("/api/cart/add", {"product_id": "SKU006", "quantity": 1})
        status, payload = post("/api/speech/session_step", {"reset": True, "text": text})
        got_digit = payload.get("digit") or (payload.get("numeric") or {}).get("digit") or ""
        got_intent = payload.get("intent") or (payload.get("numeric") or {}).get("intent") or ""
        executed = payload.get("executed") is True
        passed = status == 200 and executed == should_execute
        if should_execute:
            passed = passed and got_digit == digit and got_intent == intent
        checks.append({
            "name": text,
            "pass": passed,
            "status": status,
            "digit": got_digit,
            "intent": got_intent,
            "executed": executed,
            "message": payload.get("message", ""),
        })
    post("/api/cart/clear", {})
    passed = sum(1 for c in checks if c["pass"])
    failed = len(checks) - passed
    print(json.dumps({"ok": failed == 0, "checks": checks, "summary": {"total": len(checks), "pass": passed, "fail": failed}}, ensure_ascii=False, indent=2))
    print("SPEECH_WAKE_INLINE_EXECUTE_CHECKS=%d PASS=%d FAIL=%d" % (len(checks), passed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
