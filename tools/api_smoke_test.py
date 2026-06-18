#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Smoke test for the Flask JSON API used by the Qt/QML kiosk."""

import argparse
import json
import sys
import urllib.error
import urllib.request


def request_json(base, method, path, body=None, timeout=12):
    url = base.rstrip("/") + path
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "replace")
            return resp.status, json.loads(raw or "{}"), raw
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        try:
            parsed = json.loads(raw or "{}")
        except Exception:
            parsed = {"ok": False, "raw": raw}
        return exc.code, parsed, raw


def require(condition, name, status, data):
    if condition:
        print(f"PASS {name}")
        return
    print(f"FAIL {name}")
    print(f"HTTP {status}")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://127.0.0.1:5000")
    parser.add_argument("--camera", action="store_true", help="also test /api/capture")
    parser.add_argument("--checkout", action="store_true", help="also create a non-empty checkout order")
    args = parser.parse_args()
    base = args.base.rstrip("/")

    status, data, _ = request_json(base, "GET", "/api/state")
    require(status == 200 and data.get("ok") is True, "/api/state", status, data)

    status, data, _ = request_json(base, "POST", "/api/cart/add", {"product_id": "SKU006", "quantity": 1})
    require(status == 200 and data.get("ok") is True and data.get("cart", {}).get("count", 0) >= 1, "/api/cart/add", status, data)

    status, data, _ = request_json(base, "POST", "/api/cart/remove_last", {})
    require(status == 200 and "cart" in data, "/api/cart/remove_last", status, data)

    status, data, _ = request_json(base, "POST", "/api/cart/clear", {})
    require(status == 200 and data.get("ok") is True and data.get("cart", {}).get("count") == 0, "/api/cart/clear", status, data)

    status, data, _ = request_json(base, "POST", "/api/speech/execute", {"text": "我要截止"})
    require(
        status == 200
        and data.get("intent") == "checkout"
        and data.get("corrected") is True
        and data.get("confirm_required") is True,
        "/api/speech/execute checkout corrected",
        status,
        data,
    )

    status, data, _ = request_json(base, "POST", "/api/speech/execute", {"text": "三推上一件"})
    require(
        status == 200
        and data.get("intent") == "remove_last"
        and data.get("corrected") is True,
        "/api/speech/execute remove_last corrected",
        status,
        data,
    )

    if args.camera:
        status, data, _ = request_json(base, "POST", "/api/capture", {})
        require(status == 200 and data.get("ok") is True, "/api/capture", status, data)
    else:
        print("SKIP /api/capture (add --camera)")

    status, data, _ = request_json(base, "POST", "/api/cart/clear", {})
    require(status == 200 and data.get("ok") is True, "/api/cart/clear before checkout-empty", status, data)
    status, data, _ = request_json(base, "POST", "/api/checkout", {})
    require(status == 400 and data.get("error") == "cart_empty", "/api/checkout empty cart", status, data)

    if args.checkout:
        status, data, _ = request_json(base, "POST", "/api/cart/add", {"product_id": "SKU006", "quantity": 1})
        require(status == 200 and data.get("ok") is True, "/api/cart/add before checkout", status, data)
        status, data, _ = request_json(base, "POST", "/api/checkout", {})
        require(status == 200 and data.get("ok") is True and data.get("order_id"), "/api/checkout order", status, data)
    else:
        print("SKIP /api/checkout non-empty order (add --checkout)")

    print("API smoke test complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())

