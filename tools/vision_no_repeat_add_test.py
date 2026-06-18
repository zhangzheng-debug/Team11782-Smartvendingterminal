#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys
import time
import urllib.request

BASE = "http://127.0.0.1:5000"


def req(method, path, payload=None):
    data = json.dumps(payload or {}).encode("utf-8") if method == "POST" else None
    r = urllib.request.Request(BASE + path, data=data, headers={"Content-Type": "application/json"}, method=method)
    with urllib.request.urlopen(r, timeout=20) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8", "replace") or "{}")


def cart_count():
    _, state = req("GET", "/api/state")
    return int(((state.get("cart") or {}).get("count") or 0))


def main():
    checks = []
    req("POST", "/api/cart/clear")
    before = cart_count()
    status, scan = req("POST", "/api/scan", {"barcode": "SKU001"})
    time.sleep(2)
    after_scan = cart_count()
    status_v, verify = req("POST", "/api/vision/verify_scan", {"barcode": "SKU001"})
    after_verify = cart_count()
    status_c, cand = req("POST", "/api/vision/candidates", {"image_path": "", "limit": 3})
    after_candidates = cart_count()
    checks.append(("scan_adds_once", status == 200 and after_scan == before + 1))
    checks.append(("verify_no_repeat_add", status_v == 200 and after_verify == after_scan))
    checks.append(("candidates_no_add", status_c == 200 and after_candidates == after_scan))
    req("POST", "/api/cart/clear")
    result = {
        "ok": all(v for _, v in checks),
        "checks": [{"name": k, "pass": v} for k, v in checks],
        "counts": {"before": before, "after_scan": after_scan, "after_verify": after_verify, "after_candidates": after_candidates},
        "scan": scan,
        "verify": verify,
        "candidates": cand,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("VISION_NO_REPEAT_ADD_CHECKS=%d PASS=%d FAIL=%d" % (len(checks), sum(1 for _, v in checks if v), sum(1 for _, v in checks if not v)))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

