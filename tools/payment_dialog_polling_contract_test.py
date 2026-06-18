#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2.6.11-B PaymentDialog polling API contract test."""

import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:5000"


def request(method, path, body=None, timeout=25):
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "replace")
            return resp.status, json.loads(raw or "{}")
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        try:
            payload = json.loads(raw or "{}")
        except Exception:
            payload = {"raw": raw}
        return exc.code, payload


def post(path, body=None):
    return request("POST", path, body or {})


def get(path):
    return request("GET", path)


def create_order():
    post("/api/cart/clear", {})
    post("/api/cart/add", {"product_id": "SKU006", "quantity": 1})
    status, payload = post("/api/checkout", {})
    return status, payload.get("order") or {}


def main():
    checks = []
    status, latest_empty = post("/api/payment/sync_latest", {})
    checks.append({
        "name": "sync_latest returns JSON",
        "pass": status == 200 and isinstance(latest_empty, dict) and "message" in latest_empty,
        "payload": latest_empty,
    })

    status, order = create_order()
    order_id = order.get("order_id") or ""
    checks.append({"name": "checkout order for polling", "pass": status == 200 and bool(order_id), "order": order})

    status, waiting = post("/api/order/%s/sync_cloud" % order_id, {})
    waiting_order = waiting.get("order") or {}
    checks.append({
        "name": "waiting sync contract",
        "pass": status == 200 and waiting.get("ok") is True and "message" in waiting and waiting_order.get("payment_status") in {"unpaid", "paid"} and "order" in waiting and "latest_order" in waiting,
        "payload": waiting,
    })

    pay_url = order.get("cloud_pay_url") or ""
    if pay_url:
        urllib.request.urlopen(pay_url.rstrip("/") + "/success", timeout=20).read()
    status, paid = post("/api/payment/sync_latest", {})
    paid_order = paid.get("order") or {}
    checks.append({
        "name": "paid sync_latest contract",
        "pass": status == 200 and paid.get("ok") is True and paid_order.get("payment_status") == "paid" and paid_order.get("cloud_status") == "paid" and paid.get("message"),
        "payload": paid,
    })

    status, not_found = post("/api/order/ORDER_DOES_NOT_EXIST/sync_cloud", {})
    checks.append({
        "name": "not found has JSON",
        "pass": status == 404 and not_found.get("error") == "order_not_found" and bool(not_found.get("message")),
        "payload": not_found,
    })

    status, state = get("/api/state")
    latest = state.get("latest_order") or {}
    checks.append({
        "name": "state exposes QML paid fields",
        "pass": status == 200 and all(k in latest for k in ["payment_status", "cloud_status", "paid_at", "last_sync_at", "payment_qr_file_url", "qr_exists", "message"]),
        "latest_order": latest,
    })

    post("/api/cart/clear", {})
    passed = sum(1 for c in checks if c["pass"])
    failed = len(checks) - passed
    print(json.dumps({"ok": failed == 0, "checks": checks, "summary": {"total": len(checks), "pass": passed, "fail": failed}}, ensure_ascii=False, indent=2))
    print("PAYMENT_DIALOG_POLLING_CONTRACT_CHECKS=%d PASS=%d FAIL=%d" % (len(checks), passed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
