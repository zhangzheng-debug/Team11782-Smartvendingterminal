#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2.6.9-B payment QR accessibility contract test."""

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
    status, checkout = post("/api/checkout", {})
    order = checkout.get("order") or {}
    mode = order.get("payment_mode")
    access = order.get("payment_accessibility")
    content = order.get("payment_qr_content") or ""
    qr_path = order.get("payment_qr_path") or ""
    checks.append({"name": "checkout ok", "pass": status == 200 and checkout.get("ok") is True, "mode": mode})
    checks.append({"name": "mode present", "pass": mode in {"cloud", "lan", "local_debug"}, "mode": mode})
    checks.append({"name": "accessibility present", "pass": access in {"phone_accessible", "same_lan_required", "local_debug_only", "unknown"}, "accessibility": access})
    checks.append({"name": "qr exists", "pass": order.get("qr_exists") is True and os.path.exists(qr_path) and os.path.getsize(qr_path) > 0, "path": qr_path})
    checks.append({"name": "qr file url present", "pass": bool(order.get("payment_qr_file_url")), "file_url": order.get("payment_qr_file_url")})
    checks.append({"name": "user message present", "pass": bool(order.get("qr_user_message") or order.get("qr_message")), "message": order.get("qr_user_message") or order.get("qr_message")})
    if mode == "cloud":
        checks.append({"name": "cloud phone accessible", "pass": access == "phone_accessible" and content == order.get("cloud_pay_url") and "127.0.0.1" not in content, "content": content})
    elif mode == "lan":
        checks.append({"name": "lan same network", "pass": access == "same_lan_required" and bool(order.get("board_lan_ip")) and "127.0.0.1" not in content, "content": content})
    else:
        checks.append({"name": "local debug explicit", "pass": access == "local_debug_only" and order.get("local_debug_only") is True and "手机不可访问" in (order.get("qr_user_message") or order.get("qr_message") or ""), "content": content})
    status, regen = post("/api/payment/qr/regenerate", {"order_id": order.get("order_id")})
    ro = regen.get("order") or {}
    checks.append({"name": "regenerate keeps accessibility", "pass": status == 200 and regen.get("qr_exists") is True and ro.get("payment_accessibility") in {"phone_accessible", "same_lan_required", "local_debug_only"}, "regen": regen})
    post("/api/cart/clear", {})
    passed = sum(1 for c in checks if c["pass"])
    failed = len(checks) - passed
    print(json.dumps({"ok": failed == 0, "checks": checks, "summary": {"total": len(checks), "pass": passed, "fail": failed}}, ensure_ascii=False, indent=2))
    print("PAYMENT_QR_ACCESSIBILITY_CHECKS=%d PASS=%d FAIL=%d" % (len(checks), passed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
