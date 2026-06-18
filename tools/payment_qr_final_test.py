#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2.6.9 final payment QR URL and file test."""

import json
import os
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
        with urllib.request.urlopen(req, timeout=30) as resp:
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
    cloud_ok = cloud_status == 200 and cloud.get("ok") is True
    status, checkout = post("/api/checkout", {})
    order = checkout.get("order") or {}
    content = order.get("payment_qr_content") or ""
    qr_path = order.get("payment_qr_path") or ""
    mode = order.get("payment_mode") or order.get("payment_url_type")
    checks.append({"name": "checkout order", "pass": status == 200 and checkout.get("ok") is True and bool(order.get("order_id")), "order_id": order.get("order_id")})
    checks.append({"name": "qr exists flag", "pass": order.get("qr_exists") is True, "qr_error": order.get("qr_error")})
    checks.append({"name": "qr file exists", "pass": bool(qr_path) and os.path.exists(qr_path) and os.path.getsize(qr_path) > 0, "path": qr_path})
    checks.append({"name": "qr is png preferred", "pass": qr_path.endswith(".png"), "path": qr_path})
    checks.append({"name": "payment content nonempty", "pass": bool(content), "content": content})
    checks.append({"name": "file url nonempty", "pass": bool(order.get("payment_qr_file_url")), "file_url": order.get("payment_qr_file_url")})
    if cloud_ok:
        checks.append({"name": "cloud content priority", "pass": bool(order.get("cloud_pay_url")) and content == order.get("cloud_pay_url") and "127.0.0.1" not in content, "content": content})
    else:
        checks.append({"name": "local fallback explicit", "pass": mode in {"lan", "local", "local_debug"} and bool(order.get("qr_message")), "mode": mode, "message": order.get("qr_message")})
        if "127.0.0.1" in content:
            checks.append({"name": "127 only allowed in local_debug", "pass": mode == "local_debug" and order.get("local_debug_only") is True, "mode": mode, "content": content})
        else:
            checks.append({"name": "local link not localhost", "pass": True, "content": content})
    status, regen = post("/api/payment/qr/regenerate", {"order_id": order.get("order_id")})
    regen_order = regen.get("order") or {}
    checks.append({"name": "regenerate qr", "pass": status == 200 and regen.get("qr_exists") is True and (regen_order.get("payment_qr_path") or "").endswith(".png"), "regen": regen})
    post("/api/cart/clear", {})
    passed = sum(1 for c in checks if c["pass"])
    failed = len(checks) - passed
    print(json.dumps({"ok": failed == 0, "cloud_ok": cloud_ok, "checks": checks, "summary": {"total": len(checks), "pass": passed, "fail": failed}}, ensure_ascii=False, indent=2))
    print("PAYMENT_QR_FINAL_CHECKS=%d PASS=%d FAIL=%d" % (len(checks), passed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
