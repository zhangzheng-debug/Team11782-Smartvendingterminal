#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys
import urllib.request

BASE = "http://127.0.0.1:5000"


def post(path, payload):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8", "replace") or "{}")


def main():
    status, data = post("/api/vision/verify_scan", {"barcode": "SKU001"})
    model_available = bool(data.get("model_available"))
    confidence = float(data.get("confidence", 0.0) or 0.0)
    result = data.get("result")
    checks = [
        ("http_200", status == 200),
        ("ok_true", data.get("ok") is True),
        ("safe_no_auto_add", data.get("auto_add_cart") is False),
        ("has_match_scan", "match_scan" in data),
        ("has_scanned_product", data.get("scanned_product_id") in {"", "SKU001"}),
        ("honest_unavailable_result", model_available or data.get("result") == "verification_pending_no_model"),
        ("low_confidence_not_forced_mismatch", confidence >= 0.45 or result == "verification_low_confidence" or not model_available),
    ]
    result = {"ok": all(v for _, v in checks), "checks": [{"name": k, "pass": v} for k, v in checks], "response": data}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
