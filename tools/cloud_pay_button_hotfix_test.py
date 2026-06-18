#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2.6.11-A cloud pay button/success route end-to-end test."""

import json
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:5000"


def request(method, url, body=None, timeout=20):
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "replace")
            ctype = resp.headers.get("Content-Type", "")
            if "application/json" in ctype:
                return resp.status, json.loads(raw or "{}")
            return resp.status, {"raw": raw, "content_type": ctype}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        try:
            payload = json.loads(raw or "{}")
        except Exception:
            payload = {"raw": raw}
        return exc.code, payload


def local(method, path, body=None):
    return request(method, BASE + path, body)


def make_order():
    local("POST", "/api/cart/clear", {})
    local("POST", "/api/cart/add", {"product_id": "SKU006", "quantity": 1})
    status, payload = local("POST", "/api/checkout", {})
    return status, payload.get("order") or {}


def check_order_paid(order_id):
    status, payload = local("GET", "/api/order/" + urllib.parse.quote(order_id))
    order = payload.get("order") or payload
    return status, order


def main():
    checks = []
    status, cloud = local("GET", "/api/cloud/status")
    cloud_ok = status == 200 and cloud.get("cloud_health_ok") is True
    checks.append({"name": "board cloud health", "pass": cloud_ok, "status": status, "payload": cloud})
    if not cloud_ok:
        print(json.dumps({"ok": False, "checks": checks}, ensure_ascii=False, indent=2))
        return 2

    post_status, post_order = make_order()
    post_url = post_order.get("cloud_pay_url") or ""
    post_order_id = post_order.get("order_id") or ""
    checks.append({"name": "checkout creates cloud url for POST", "pass": post_status == 200 and post_url.startswith("http"), "order": post_order})
    status, post_success = request("POST", post_url.rstrip("/") + "/success", {})
    checks.append({
        "name": "POST success marks paid page",
        "pass": status == 200 and "支付成功" in (post_success.get("raw") or ""),
        "status": status,
        "payload": {k: post_success.get(k) for k in ("content_type",)},
    })
    status, synced = check_order_paid(post_order_id)
    checks.append({"name": "board sync paid after POST", "pass": status == 200 and synced.get("payment_status") == "paid", "order": synced})

    get_status, get_order = make_order()
    get_url = get_order.get("cloud_pay_url") or ""
    get_order_id = get_order.get("order_id") or ""
    checks.append({"name": "checkout creates cloud url for GET", "pass": get_status == 200 and get_url.startswith("http"), "order": get_order})
    status, get_success = request("GET", get_url.rstrip("/") + "/success")
    checks.append({
        "name": "GET fallback success marks paid page",
        "pass": status == 200 and "支付成功" in (get_success.get("raw") or ""),
        "status": status,
        "payload": {k: get_success.get(k) for k in ("content_type",)},
    })
    status, synced = check_order_paid(get_order_id)
    checks.append({"name": "board sync paid after GET", "pass": status == 200 and synced.get("payment_status") == "paid", "order": synced})

    _, state = local("GET", "/api/state")
    checks.append({
        "name": "payment_success audio/event visible",
        "pass": ((state.get("audio") or {}).get("latest_event") == "payment_success") or state.get("latest_audio_event") == "payment_success",
        "audio": state.get("audio") or {},
    })

    local("POST", "/api/cart/clear", {})
    passed = sum(1 for c in checks if c["pass"])
    failed = len(checks) - passed
    print(json.dumps({"ok": failed == 0, "checks": checks, "summary": {"total": len(checks), "pass": passed, "fail": failed}}, ensure_ascii=False, indent=2))
    print("CLOUD_PAY_BUTTON_HOTFIX_CHECKS=%d PASS=%d FAIL=%d" % (len(checks), passed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
