#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2.6.9-B cloud payment mode selection smoke test."""

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
        with urllib.request.urlopen(r, timeout=30) as resp:
            return resp.getcode(), json.loads(resp.read().decode("utf-8", "replace") or "{}")
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8", "replace") or "{}")


def main():
    checks = []
    status, cloud = req("GET", "/api/cloud/status")
    checks.append({"name": "cloud status fields", "pass": status == 200 and "cloud_enabled" in cloud and "cloud_health_ok" in cloud and "last_checked_at" in cloud, "cloud": cloud})
    req("POST", "/api/cart/clear", {})
    req("POST", "/api/cart/add", {"product_id": "SKU006", "quantity": 1})
    status, checkout = req("POST", "/api/checkout", {})
    order = checkout.get("order") or {}
    cloud_ok = cloud.get("cloud_health_ok") is True
    if cloud_ok:
        passed = order.get("payment_mode") == "cloud" and order.get("payment_accessibility") == "phone_accessible" and order.get("payment_qr_content") == order.get("cloud_pay_url")
    else:
        passed = order.get("payment_mode") in {"lan", "local_debug"} and order.get("payment_accessibility") in {"same_lan_required", "local_debug_only"}
    checks.append({"name": "checkout mode follows cloud status", "pass": status == 200 and passed, "cloud_ok": cloud_ok, "order": order})
    req("POST", "/api/cart/clear", {})
    p = sum(1 for c in checks if c["pass"])
    f = len(checks) - p
    print(json.dumps({"ok": f == 0, "checks": checks, "summary": {"total": len(checks), "pass": p, "fail": f}}, ensure_ascii=False, indent=2))
    print("CLOUD_PAYMENT_MODE_SELECTION_CHECKS=%d PASS=%d FAIL=%d" % (len(checks), p, f))
    return 0 if f == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
