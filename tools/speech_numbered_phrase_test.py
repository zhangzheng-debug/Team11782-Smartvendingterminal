#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2.6.10 numbered phrase voice command test."""

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


def post(path, body=None):
    return request("POST", path, body or {})


def run_voice(text, button=False, prefill=False):
    post("/api/speech/cancel", {})
    post("/api/cart/clear", {})
    if prefill:
        post("/api/cart/add", {"product_id": "SKU006", "quantity": 1})
    if button:
        return post("/api/speech/session_step", {"button_wake": True, "text": text})
    return post("/api/speech/session_step", {"reset": True, "text": text})


def got(payload, key):
    return payload.get(key) or (payload.get("numeric") or {}).get(key) or (payload.get("wake") or {}).get(key) or ""


def main():
    checks = []
    cases = [
        ("小售小售一号查询总价", False, False, "1", "query_total_price", True),
        ("小售小售二号删除上一件", False, True, "2", "remove_last", True),
        ("小售小售三号清空购物车", False, True, "3", "clear_cart", True),
        ("小售小售四号结账", False, True, "4", "checkout", True),
        ("小售小售五号拍照识别", False, False, "5", "camera_capture", None),
        ("一号查询总价", True, False, "1", "query_total_price", True),
        ("四号结账", True, True, "4", "checkout", True),
        ("我要结账", False, True, "", "", False),
        ("二号删除上一件", False, True, "", "", False),
        ("小售小售一号结账", False, True, "4", "checkout", True),
    ]
    for text, button, prefill, digit, intent, should_execute in cases:
        status, payload = run_voice(text, button=button, prefill=prefill)
        actual_digit = got(payload, "digit")
        actual_intent = got(payload, "intent")
        executed = payload.get("executed") is True
        if should_execute is None:
            passed = status == 200 and actual_digit == digit and actual_intent == intent
        elif should_execute:
            passed = status == 200 and executed and actual_digit == digit and actual_intent == intent
        else:
            passed = status == 200 and not executed
        if "一号结账" in text:
            passed = passed and bool((payload.get("numeric") or payload.get("wake") or {}).get("conflict_warning"))
        checks.append({
            "name": text,
            "pass": passed,
            "status": status,
            "button_mode": button,
            "digit": actual_digit,
            "intent": actual_intent,
            "executed": executed,
            "message": payload.get("message", ""),
            "payload": payload,
        })
    post("/api/cart/clear", {})
    passed = sum(1 for c in checks if c["pass"])
    failed = len(checks) - passed
    print(json.dumps({"ok": failed == 0, "checks": checks, "summary": {"total": len(checks), "pass": passed, "fail": failed}}, ensure_ascii=False, indent=2))
    print("SPEECH_NUMBERED_PHRASE_CHECKS=%d PASS=%d FAIL=%d" % (len(checks), passed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
