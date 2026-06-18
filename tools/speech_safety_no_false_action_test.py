#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Voice safety regression: no dangerous action without wake; inline wake may execute."""

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
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.getcode(), json.loads(resp.read().decode("utf-8", "replace") or "{}")
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8", "replace") or "{}")


def post(path, body=None):
    return request_json("POST", path, body or {})


def get(path):
    return request_json("GET", path)


def cart_snapshot():
    _, state = get("/api/state")
    cart = state.get("cart") or {}
    return {
        "count": int(state.get("cart_count") or cart.get("count") or 0),
        "total_cent": int(state.get("cart_total_cent") or cart.get("total_cent") or 0),
    }


def latest_order_id():
    _, state = get("/api/state")
    return (state.get("latest_order") or {}).get("order_id") or ""


def prepare_cart():
    post("/api/speech/cancel", {})
    post("/api/cart/clear", {})
    post("/api/cart/add", {"product_id": "SKU006", "quantity": 1})
    post("/api/cart/add", {"product_id": "SKU007", "quantity": 1})


def main():
    checks = []
    for text in ["删除上一件", "我要结账", "二", "四"]:
        prepare_cart()
        before = {"cart": cart_snapshot(), "order_id": latest_order_id()}
        status, payload = post("/api/speech/session_step", {"reset": True, "text": text})
        after = {"cart": cart_snapshot(), "order_id": latest_order_id()}
        checks.append({
            "name": "not woken blocks %s" % text,
            "pass": status == 200 and payload.get("executed") is False and before == after,
            "status": status,
            "executed": payload.get("executed"),
            "message": payload.get("message"),
            "before": before,
            "after": after,
        })

    prepare_cart()
    before = {"cart": cart_snapshot(), "order_id": latest_order_id()}
    status, payload = post("/api/speech/session_step", {"reset": True, "text": "小售小售二"})
    after = {"cart": cart_snapshot(), "order_id": latest_order_id()}
    checks.append({
        "name": "inline wake + 2 removes last",
        "pass": status == 200 and payload.get("executed") is True and after["cart"]["count"] == before["cart"]["count"] - 1,
        "status": status,
        "digit": payload.get("digit"),
        "intent": payload.get("intent"),
        "message": payload.get("message"),
    })

    prepare_cart()
    before = {"cart": cart_snapshot(), "order_id": latest_order_id()}
    status, payload = post("/api/speech/session_step", {"reset": True, "text": "小售小售四"})
    after = {"cart": cart_snapshot(), "order_id": latest_order_id()}
    checks.append({
        "name": "inline wake + 4 checks out",
        "pass": status == 200 and payload.get("executed") is True and after["order_id"] != before["order_id"],
        "status": status,
        "digit": payload.get("digit"),
        "intent": payload.get("intent"),
        "message": payload.get("message"),
    })

    post("/api/cart/clear", {})
    passed = sum(1 for c in checks if c["pass"])
    failed = len(checks) - passed
    print(json.dumps({"ok": failed == 0, "checks": checks, "summary": {"total": len(checks), "pass": passed, "fail": failed}}, ensure_ascii=False, indent=2))
    print("SPEECH_SAFETY_NO_FALSE_ACTION_CHECKS=%d PASS=%d FAIL=%d" % (len(checks), passed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
