#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2.6.8 payment QR generation and cloud URL priority test."""

import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:5000"


def request(method, path, body=None):
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
    return request("POST", path, body or {})


def get(path):
    return request("GET", path)


def main():
    checks = []
    post("/api/cart/clear", {})
    post("/api/cart/add", {"product_id": "SKU006", "quantity": 1})
    cloud_status, cloud = get("/api/cloud/status")
    cloud_available = cloud_status == 200 and cloud.get("ok") is True
    status, checkout = post("/api/checkout", {})
    order = checkout.get("order") or {}
    checks.append({"name": "checkout creates order", "pass": status == 200 and checkout.get("ok") is True and bool(order.get("order_id")), "order": order})
    checks.append({"name": "qr_exists true", "pass": order.get("qr_exists") is True, "qr_error": order.get("qr_error")})
    checks.append({"name": "qr url not empty", "pass": bool(order.get("payment_qr_url") or order.get("payment_qr_file_url") or order.get("qr_image_url"))})
    if cloud_available:
        checks.append({"name": "cloud_pay_url exists if cloud available", "pass": bool(order.get("cloud_pay_url")), "cloud": cloud})
        checks.append({"name": "payment content not localhost when cloud available", "pass": "127.0.0.1" not in (order.get("payment_qr_content") or ""), "payment_qr_content": order.get("payment_qr_content")})
    else:
        checks.append({"name": "local fallback explicit when cloud unavailable", "pass": order.get("payment_url_type") == "local_fallback" or not order.get("cloud_pay_url"), "cloud": cloud})
    status, regen = post("/api/payment/qr/regenerate", {"order_id": order.get("order_id")})
    checks.append({"name": "regenerate works", "pass": status == 200 and regen.get("qr_exists") is True, "regen": regen})
    status, fetched = get("/api/order/" + order.get("order_id", ""))
    fetched_order = fetched.get("order") or {}
    checks.append({"name": "api order exposes qr fields", "pass": status == 200 and "payment_qr_file_url" in fetched_order and "qr_exists" in fetched_order, "order": fetched_order})
    post("/api/cart/clear", {})
    passed = sum(1 for c in checks if c["pass"])
    failed = len(checks) - passed
    print(json.dumps({"ok": failed == 0, "cloud_available": cloud_available, "checks": checks, "summary": {"total": len(checks), "pass": passed, "fail": failed}}, ensure_ascii=False, indent=2))
    print("PAYMENT_QR_GENERATION_CHECKS=%d PASS=%d FAIL=%d" % (len(checks), passed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
