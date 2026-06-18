#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2.6.10 phone-first cloud payment policy test."""

import json
import os
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


def get(path):
    return request("GET", path)


def post(path, body=None):
    return request("POST", path, body or {})


def main():
    checks = []
    _, cloud = get("/api/cloud/status")
    cloud_ok = bool(cloud.get("cloud_health_ok"))

    post("/api/cart/clear", {})
    post("/api/cart/add", {"product_id": "SKU006", "quantity": 1})
    status, checkout = post("/api/checkout", {})
    order = checkout.get("order") or {}
    mode = order.get("payment_mode")
    access = order.get("payment_accessibility")
    content = order.get("payment_qr_content") or ""
    qr_path = order.get("payment_qr_path") or ""

    checks.append({"name": "checkout returns order", "pass": status == 200 and checkout.get("ok") is True and bool(order.get("order_id")), "mode": mode})
    checks.append({"name": "qr png exists", "pass": bool(qr_path) and os.path.exists(qr_path) and os.path.getsize(qr_path) > 0, "path": qr_path})
    checks.append({"name": "phone_demo_ready field", "pass": order.get("phone_demo_ready") in {True, False, "conditional", "true", "false"}, "value": order.get("phone_demo_ready")})

    if cloud_ok:
        checks.append({"name": "cloud health ok selects cloud", "pass": mode == "cloud" and access == "phone_accessible", "order": order})
        checks.append({"name": "qr content equals cloud url", "pass": bool(order.get("cloud_pay_url")) and content == order.get("cloud_pay_url") and "127.0.0.1" not in content, "content": content})
        checks.append({"name": "phone demo ready true", "pass": order.get("phone_demo_ready") is True, "value": order.get("phone_demo_ready")})
    else:
        checks.append({"name": "cloud offline does not claim phone cloud", "pass": mode in {"lan", "local_debug"} and access in {"same_lan_required", "local_debug_only"}, "cloud": cloud, "order": order})
        if mode == "local_debug":
            checks.append({"name": "local_debug phone not ready", "pass": order.get("phone_demo_ready") is False and "127.0.0.1" in content, "content": content})
        else:
            checks.append({"name": "lan is conditional", "pass": order.get("phone_demo_ready") == "conditional" and "127.0.0.1" not in content, "content": content})

    order_id = order.get("order_id", "")
    status, promoted = post("/api/order/%s/promote_cloud" % order_id, {})
    if cloud_ok or mode == "cloud":
        po = promoted.get("order") or {}
        checks.append({"name": "promote_cloud success when cloud available", "pass": status == 200 and promoted.get("ok") is True and po.get("payment_mode") == "cloud", "payload": promoted})
    else:
        checks.append({"name": "promote_cloud fails clearly when cloud offline", "pass": status in {502, 503} and promoted.get("ok") is False and bool(promoted.get("message")), "payload": promoted})

    post("/api/cart/clear", {})
    passed = sum(1 for c in checks if c["pass"])
    failed = len(checks) - passed
    print(json.dumps({"ok": failed == 0, "cloud_health_ok": cloud_ok, "checks": checks, "summary": {"total": len(checks), "pass": passed, "fail": failed}}, ensure_ascii=False, indent=2))
    print("PAYMENT_PHONE_FIRST_CLOUD_CHECKS=%d PASS=%d FAIL=%d" % (len(checks), passed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

