#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2.6.11-A robust numbered phrase voice hotfix test."""

import json
import os
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:5000"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def request(method, path, body=None, timeout=35):
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "replace")
            return resp.getcode(), json.loads(raw or "{}")
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        return exc.code, json.loads(raw or "{}")


def post(path, body=None):
    return request("POST", path, body or {})


def get(path):
    return request("GET", path)


def payload_value(payload, key):
    return payload.get(key) or (payload.get("numeric") or {}).get(key) or (payload.get("wake") or {}).get(key) or ""


def parser_checks():
    from app import parse_wake_and_numeric_command, parse_numeric_only_command, voice_menu_payload

    checks = []
    cases = [
        ("小售小售一号查询总价", "1", "query_total_price"),
        ("小售小售二号删除上一件", "2", "remove_last"),
        ("小售小售三号清空购物车", "3", "clear_cart"),
        ("小售小售四号结账", "4", "checkout"),
        ("小售小售五号拍照识别", "5", "camera_capture"),
        ("小售小售零号取消", "0", "cancel"),
    ]
    for text, digit, intent in cases:
        parsed = parse_wake_and_numeric_command(text)
        checks.append({
            "name": "parse wake phrase " + text,
            "pass": parsed.get("wake_detected") is True and parsed.get("digit") == digit and parsed.get("intent") == intent,
            "parsed": parsed,
        })

    button_cases = [
        ("一号查询总价", "1", "query_total_price"),
        ("四号结账", "4", "checkout"),
    ]
    for text, digit, intent in button_cases:
        parsed = parse_numeric_only_command(text)
        checks.append({
            "name": "parse button phrase " + text,
            "pass": parsed.get("success") is True and parsed.get("digit") == digit and parsed.get("intent") == intent,
            "parsed": parsed,
        })

    conflict = parse_wake_and_numeric_command("小售小售一号结账")
    checks.append({
        "name": "operation word wins conflict",
        "pass": conflict.get("intent") == "checkout" and conflict.get("digit") == "4" and conflict.get("conflict_warning") is True,
        "parsed": conflict,
    })

    menu = voice_menu_payload()
    menu_text = json.dumps(menu, ensure_ascii=False)
    checks.append({
        "name": "menu recommends full phrase",
        "pass": "小售小售一号查询总价" in menu_text and "小售小售四号结账" in menu_text and "button_prompt" in menu,
        "menu": menu,
    })
    return checks


def api_checks():
    checks = []
    post("/api/speech/cancel", {})
    post("/api/cart/clear", {})

    # No wake word: should not execute risky commands.
    for text in ["四号结账", "我要结账"]:
        post("/api/speech/cancel", {})
        post("/api/cart/clear", {})
        post("/api/cart/add", {"product_id": "SKU006", "quantity": 1})
        before_status, before = get("/api/state")
        status, payload = post("/api/speech/session_step", {"reset": True, "text": text})
        after_status, after = get("/api/state")
        before_order = (before.get("latest_order") or {}).get("order_id") if before_status == 200 else ""
        after_order = (after.get("latest_order") or {}).get("order_id") if after_status == 200 else ""
        checks.append({
            "name": "no wake blocks " + text,
            "pass": status == 200 and payload.get("executed") is False and before_order == after_order,
            "payload": payload,
        })

    # Button mode allows short numbered phrases.
    post("/api/speech/cancel", {})
    status, payload = post("/api/speech/session_step", {"button_wake": True, "text": "一号查询总价"})
    checks.append({
        "name": "button one query total",
        "pass": status == 200 and payload.get("executed") is True and payload_value(payload, "intent") == "query_total_price",
        "payload": payload,
    })

    post("/api/speech/cancel", {})
    post("/api/cart/clear", {})
    post("/api/cart/add", {"product_id": "SKU006", "quantity": 1})
    status, payload = post("/api/speech/session_step", {"button_wake": True, "text": "四号结账"})
    checks.append({
        "name": "button four checkout",
        "pass": status == 200 and payload.get("executed") is True and payload_value(payload, "intent") == "checkout",
        "payload": payload,
    })

    # Inline wake + conflict should execute operation word and report conflict.
    post("/api/speech/cancel", {})
    post("/api/cart/clear", {})
    post("/api/cart/add", {"product_id": "SKU006", "quantity": 1})
    status, payload = post("/api/speech/session_step", {"reset": True, "text": "小售小售一号结账"})
    conflict = payload.get("numeric") or payload.get("wake") or {}
    checks.append({
        "name": "api conflict operation wins",
        "pass": status == 200 and payload.get("executed") is True and payload_value(payload, "intent") == "checkout" and conflict.get("conflict_warning") is True,
        "payload": payload,
    })

    post("/api/cart/clear", {})
    return checks


def main():
    checks = parser_checks() + api_checks()
    passed = sum(1 for c in checks if c["pass"])
    failed = len(checks) - passed
    print(json.dumps({"ok": failed == 0, "checks": checks, "summary": {"total": len(checks), "pass": passed, "fail": failed}}, ensure_ascii=False, indent=2))
    print("SPEECH_NUMBERED_PHRASE_HOTFIX_CHECKS=%d PASS=%d FAIL=%d" % (len(checks), passed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
