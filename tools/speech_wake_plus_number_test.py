#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2.6.8 wake word and number in the same utterance."""

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
        with urllib.request.urlopen(r, timeout=15) as resp:
            raw = resp.read().decode("utf-8", "replace")
            status = resp.getcode()
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        status = exc.code
    return status, json.loads(raw or "{}")


def post(path, body=None):
    return req("POST", path, body or {})


def add_check(checks, name, passed, status, payload):
    checks.append({
        "name": name,
        "pass": bool(passed),
        "status": status,
        "stage": payload.get("stage"),
        "digit": payload.get("digit") or (payload.get("numeric") or {}).get("digit"),
        "intent": payload.get("intent") or (payload.get("numeric") or {}).get("intent"),
        "executed": payload.get("executed"),
        "message": payload.get("message"),
    })


def main():
    checks = []
    cases = [
        ("小售小售1", "1", "query_total_price"),
        ("小售小售一", "1", "query_total_price"),
        ("小售小售幺", "1", "query_total_price"),
        ("小售小售2", "2", "remove_last"),
        ("小售小售二", "2", "remove_last"),
        ("小售小售4", "4", "checkout"),
        ("小售小售四", "4", "checkout"),
        ("小售小售5", "5", "camera_capture"),
        ("小售小售零", "0", "cancel"),
        ("小售小售我要结账", "4", "checkout"),
        ("小售小售查询总价", "1", "query_total_price"),
    ]
    for text, digit, intent in cases:
        post("/api/speech/cancel", {})
        post("/api/cart/clear", {})
        if intent in {"remove_last", "clear_cart", "checkout"}:
            post("/api/cart/add", {"product_id": "SKU006", "quantity": 1})
        status, payload = post("/api/speech/session_step", {"reset": True, "text": text})
        got_digit = payload.get("digit") or (payload.get("numeric") or {}).get("digit")
        got_intent = payload.get("intent") or (payload.get("numeric") or {}).get("intent")
        passed = status == 200 and got_digit == digit and got_intent == intent and payload.get("executed") is True
        add_check(checks, "wake plus %s" % text, passed, status, payload)

    post("/api/speech/cancel", {})
    status, payload = post("/api/speech/session_step", {"reset": True, "text": "小售小售"})
    add_check(checks, "wake only no execute", status == 200 and payload.get("voice_mode") == "command_listening" and payload.get("executed") is False, status, payload)
    status, payload = post("/api/speech/session_step", {"reset": True, "text": "2"})
    add_check(checks, "no wake number no execute", status == 200 and payload.get("executed") is False, status, payload)
    status, payload = post("/api/speech/session_step", {"reset": True, "text": "我要结账"})
    add_check(checks, "no wake checkout no execute", status == 200 and payload.get("executed") is False, status, payload)
    post("/api/cart/clear", {})

    passed = sum(1 for c in checks if c["pass"])
    failed = len(checks) - passed
    print(json.dumps({"ok": failed == 0, "checks": checks, "summary": {"total": len(checks), "pass": passed, "fail": failed}}, ensure_ascii=False, indent=2))
    print("SPEECH_WAKE_PLUS_NUMBER_CHECKS=%d PASS=%d FAIL=%d" % (len(checks), passed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
