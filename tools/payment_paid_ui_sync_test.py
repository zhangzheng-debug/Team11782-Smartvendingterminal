#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2.6.11-B payment paid UI sync endpoint test."""

import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:5000"


def request(method, url, body=None, timeout=25):
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "replace")
            if "application/json" in resp.headers.get("Content-Type", ""):
                return resp.status, json.loads(raw or "{}")
            return resp.status, {"raw": raw}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        try:
            payload = json.loads(raw or "{}")
        except Exception:
            payload = {"raw": raw}
        return exc.code, payload


def local(method, path, body=None):
    return request(method, BASE + path, body)


def main():
    checks = []
    status, cloud = local("GET", "/api/cloud/status")
    checks.append({"name": "cloud health", "pass": status == 200 and cloud.get("cloud_health_ok") is True, "payload": cloud})

    local("POST", "/api/cart/clear", {})
    local("POST", "/api/cart/add", {"product_id": "SKU006", "quantity": 1})
    status, checkout = local("POST", "/api/checkout", {})
    order = checkout.get("order") or {}
    order_id = order.get("order_id") or ""
    pay_url = order.get("cloud_pay_url") or ""
    checks.append({
        "name": "checkout has cloud order",
        "pass": status == 200 and bool(order_id) and pay_url.startswith("http") and bool(order.get("cloud_order_id")),
        "order": order,
    })

    status, success_page = request("GET", pay_url.rstrip("/") + "/success")
    checks.append({
        "name": "cloud success route",
        "pass": status == 200 and "支付成功" in (success_page.get("raw") or ""),
        "status": status,
    })

    status, synced = local("POST", "/api/order/%s/sync_cloud" % order_id, {})
    synced_order = synced.get("order") or {}
    checks.append({
        "name": "sync_cloud returns paid",
        "pass": status == 200 and synced.get("ok") is True and synced_order.get("payment_status") == "paid" and synced_order.get("cloud_status") == "paid" and bool(synced_order.get("paid_at")),
        "payload": synced,
    })

    status, state = local("GET", "/api/state")
    latest = state.get("latest_order") or {}
    audio = state.get("audio") or {}
    checks.append({
        "name": "state latest_order paid",
        "pass": status == 200 and latest.get("order_id") == order_id and latest.get("payment_status") == "paid" and latest.get("cloud_status") == "paid",
        "latest_order": latest,
    })
    checks.append({
        "name": "payment_success audio event",
        "pass": audio.get("latest_event") == "payment_success" or state.get("latest_audio_event") == "payment_success",
        "audio": audio,
    })
    checks.append({
        "name": "qml fields present",
        "pass": all(k in latest for k in ["payment_status", "cloud_status", "paid_at", "last_sync_at", "message", "payment_qr_file_url", "qr_exists"]),
        "latest_order_keys": sorted(latest.keys()),
    })

    local("POST", "/api/cart/clear", {})
    passed = sum(1 for c in checks if c["pass"])
    failed = len(checks) - passed
    print(json.dumps({"ok": failed == 0, "checks": checks, "summary": {"total": len(checks), "pass": passed, "fail": failed}}, ensure_ascii=False, indent=2))
    print("PAYMENT_PAID_UI_SYNC_CHECKS=%d PASS=%d FAIL=%d" % (len(checks), passed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
