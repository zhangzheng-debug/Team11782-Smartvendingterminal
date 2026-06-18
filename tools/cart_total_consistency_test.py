#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2.6.5 cart total consistency API gate."""

import argparse
import json
import sys
import urllib.request


def req(method, url, body=None, timeout=10):
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", "replace"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:5000")
    args = ap.parse_args()
    base = args.base.rstrip("/")

    req("POST", base + "/api/cart/clear", {})
    req("POST", base + "/api/scan", {"barcode": "SKU001"})
    req("POST", base + "/api/scan", {"barcode": "SKU002"})
    state = req("GET", base + "/api/state")

    items = state.get("cart_items") or state.get("cart", {}).get("items") or []
    expected = sum(int(i.get("subtotal_cent") or 0) for i in items)
    reported = int(state.get("cart_total_cent") or state.get("cart", {}).get("total_cent") or 0)
    ok = bool(state.get("cart_total_consistency_ok")) and expected == reported

    print(json.dumps({
        "ok": ok,
        "expected_sum_cent": expected,
        "reported_total_cent": reported,
        "cart_count": state.get("cart_count"),
        "item_count": len(items),
    }, ensure_ascii=False, indent=2))
    req("POST", base + "/api/cart/clear", {})
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
