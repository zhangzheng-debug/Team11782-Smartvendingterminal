#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2.6.5 scan-triggered RKNN verify gate."""

import argparse
import json
import sys
import urllib.request


def req(method, url, body=None, timeout=30):
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
    ap.add_argument("--sku", default="SKU001")
    args = ap.parse_args()
    base = args.base.rstrip("/")

    req("POST", base + "/api/cart/clear", {})
    scan = req("POST", base + "/api/scan", {"barcode": args.sku})
    if not scan.get("ok"):
        print(json.dumps({"ok": False, "stage": "scan", "scan": scan}, ensure_ascii=False, indent=2))
        return 1

    verify = req("POST", base + "/api/vision/verify_scan", {"barcode": args.sku, "capture": True}, timeout=40)
    state = req("GET", base + "/api/state")
    count = int(state.get("cart_count") or state.get("cart", {}).get("count") or 0)
    ok = count == 1 and verify.get("auto_add_cart") is False and verify.get("job_status") in ("done", None, "")

    print(json.dumps({
        "ok": ok,
        "cart_count_after_scan_plus_verify": count,
        "verify_result": verify.get("result"),
        "backend": verify.get("backend"),
        "top1_product_id": verify.get("top1_product_id"),
        "match_scan": verify.get("match_scan"),
        "latency_ms": verify.get("latency_ms"),
    }, ensure_ascii=False, indent=2))
    req("POST", base + "/api/cart/clear", {})
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
