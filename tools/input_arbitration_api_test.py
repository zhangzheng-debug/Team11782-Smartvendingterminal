#!/usr/bin/env python3
import json
import sys
import time
import urllib.error
import urllib.request


BASE = "http://127.0.0.1:5000"


def req(method, path, body=None):
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=8) as resp:
            status = resp.getcode()
            raw = resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        status = exc.code
        raw = exc.read().decode("utf-8", "replace")
    return status, json.loads(raw or "{}")


def add_result(results, name, passed, status, payload):
    results.append({
        "name": name,
        "pass": bool(passed),
        "status": status,
        "ok": payload.get("ok"),
        "success": payload.get("success"),
        "status_text": payload.get("status"),
        "error_reason": payload.get("error_reason") or payload.get("error"),
        "intent": payload.get("intent"),
        "message": payload.get("message") or payload.get("result"),
        "cart_total": (payload.get("cart") or {}).get("total_text"),
    })


def main():
    results = []
    req("POST", "/api/cart/clear", {})

    scan_cases = [
        ("scan SKU006", {"barcode": "SKU006"}, True, "SKU006", ""),
        ("scan SKU007", {"barcode": "SKU007"}, True, "SKU007", ""),
        ("scan unknown", {"barcode": "UNKNOWN_TEST_001"}, False, "", "unknown_barcode"),
        ("scan empty", {"barcode": ""}, False, "", "empty_scan"),
    ]
    for name, body, expect_ok, product_id, reason in scan_cases:
        time.sleep(2.1)
        status, payload = req("POST", "/api/scan", body)
        passed = status == 200 and payload.get("ok") is expect_ok and payload.get("success") is expect_ok
        if product_id:
            passed = passed and payload.get("product_id") == product_id
        if reason:
            passed = passed and payload.get("error_reason") == reason
        add_result(results, name, passed, status, payload)

    status, payload = req("POST", "/api/speech/execute", {"text": "一共多少钱", "confirmed": False})
    passed = status == 200 and payload.get("ok") is True and payload.get("intent") == "query_total_price"
    add_result(results, "speech query total", passed, status, payload)

    status, payload = req("POST", "/api/speech/execute", {"text": "我要截正", "confirmed": False})
    passed = status == 200 and payload.get("ok") is True and payload.get("intent") == "checkout"
    passed = passed and payload.get("confirm_required") is True
    add_result(results, "speech corrected checkout", passed, status, payload)

    req("POST", "/api/cart/clear", {})
    passed = sum(1 for r in results if r["pass"])
    failed = len(results) - passed
    out = {"ok": failed == 0, "checks": results, "summary": {"total": len(results), "pass": passed, "fail": failed}}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    print("INPUT_ARBITRATION_API_CHECKS=%d PASS=%d FAIL=%d" % (len(results), passed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
