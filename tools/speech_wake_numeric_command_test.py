#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2.6.7 wake-word + numeric voice command matrix."""

import json
import sys
import urllib.error
import urllib.request


BASE = "http://127.0.0.1:5000"


def request_json(method, path, body=None):
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.getcode()
            raw = resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        status = exc.code
        raw = exc.read().decode("utf-8", "replace")
    try:
        payload = json.loads(raw or "{}")
    except Exception:
        payload = {"raw": raw}
    return status, payload


def post(path, body=None):
    return request_json("POST", path, body or {})


def get(path):
    return request_json("GET", path)


def cart_count():
    _, state = get("/api/state")
    return int(state.get("cart_count") or (state.get("cart") or {}).get("count") or 0)


def latest_order_id():
    _, state = get("/api/state")
    return (state.get("latest_order") or {}).get("order_id") or ""


class Matrix:
    def __init__(self):
        self.checks = []

    def add(self, name, passed, status=None, payload=None, note=""):
        payload = payload or {}
        self.checks.append({
            "name": name,
            "pass": bool(passed),
            "status": status,
            "voice_mode": payload.get("voice_mode"),
            "stage": payload.get("stage"),
            "success": payload.get("success"),
            "digit": payload.get("digit") or (payload.get("numeric") or {}).get("digit"),
            "intent": payload.get("intent") or (payload.get("numeric") or {}).get("intent"),
            "message": payload.get("message"),
            "note": note,
        })

    def reset(self):
        post("/api/speech/cancel", {})
        post("/api/cart/clear", {})

    def wake(self, text):
        status, payload = post("/api/speech/session_step", {"reset": True, "text": text})
        return status, payload

    def command(self, text):
        status, payload = post("/api/speech/session_step", {"text": text})
        return status, payload

    def run(self):
        for wake_text in ["小售小售", "小受小受", "开始操作"]:
            self.reset()
            status, payload = self.wake(wake_text)
            self.add(
                "wake %s" % wake_text,
                status == 200 and payload.get("voice_mode") == "command_listening" and payload.get("wake_detected") is True,
                status,
                payload,
            )

        self.reset()
        status, payload = self.wake("乱七八糟")
        self.add(
            "no wake random text",
            status == 200 and payload.get("wake_detected") is False and payload.get("executed") is False,
            status,
            payload,
        )

        command_cases = [
            ("一", "1", "query_total_price"),
            ("1", "1", "query_total_price"),
            ("幺", "1", "query_total_price"),
            ("二", "2", "remove_last"),
            ("两", "2", "remove_last"),
            ("三", "3", "clear_cart"),
            ("四", "4", "checkout"),
            ("是", "4", "checkout"),
            ("五", "5", "camera_capture"),
            ("我", "5", "camera_capture"),
            ("零", "0", "cancel"),
            ("取消", "0", "cancel"),
        ]
        for text, expected_digit, expected_intent in command_cases:
            self.reset()
            if expected_intent in {"remove_last", "clear_cart", "checkout"}:
                post("/api/cart/add", {"product_id": "SKU006", "quantity": 1})
            status, payload = self.wake("小售小售")
            if status != 200 or payload.get("voice_mode") != "command_listening":
                self.add("prepare wake for %s" % text, False, status, payload)
                continue
            before_count = cart_count()
            before_order = latest_order_id()
            status, payload = self.command(text)
            intent = payload.get("intent") or (payload.get("numeric") or {}).get("intent")
            digit = payload.get("digit") or (payload.get("numeric") or {}).get("digit")
            passed = status == 200 and digit == expected_digit and intent == expected_intent
            if expected_intent == "remove_last":
                passed = passed and cart_count() == max(0, before_count - 1)
            if expected_intent == "checkout":
                passed = passed and latest_order_id() != before_order
            self.add("wake + command %s" % text, passed, status, payload)

        safety_cases = ["二", "我要结账", "删除上一件"]
        for text in safety_cases:
            self.reset()
            post("/api/cart/add", {"product_id": "SKU006", "quantity": 1})
            before_count = cart_count()
            before_order = latest_order_id()
            status, payload = post("/api/speech/session_step", {"reset": True, "text": text})
            passed = (
                status == 200
                and payload.get("executed") is False
                and cart_count() == before_count
                and latest_order_id() == before_order
            )
            self.add("not woken no execute %s" % text, passed, status, payload)

        self.reset()
        return self.checks


def main():
    matrix = Matrix()
    checks = matrix.run()
    passed = sum(1 for c in checks if c["pass"])
    failed = len(checks) - passed
    print(json.dumps({
        "ok": failed == 0,
        "checks": checks,
        "summary": {"total": len(checks), "pass": passed, "fail": failed},
    }, ensure_ascii=False, indent=2))
    print("SPEECH_WAKE_NUMERIC_COMMAND_CHECKS=%d PASS=%d FAIL=%d" % (len(checks), passed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
