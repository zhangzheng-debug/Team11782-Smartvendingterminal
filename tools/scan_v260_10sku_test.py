#!/usr/bin/env python3
import argparse
import csv
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def request_json(base, method, path, body=None):
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(base.rstrip("/") + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.getcode()
            raw = resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        status = exc.code
        raw = exc.read().decode("utf-8", "replace")
    try:
        payload = json.loads(raw or "{}")
    except Exception:
        payload = {"raw": raw}
    return status, payload


def load_manifest(path):
    with Path(path).open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    rows = [r for r in rows if r.get("product_id")]
    if len(rows) != 10:
        raise RuntimeError("expected 10 manifest rows, got %d" % len(rows))
    return rows


def cart_total(payload):
    return int((payload.get("cart") or {}).get("total_cent") or 0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://127.0.0.1:5000")
    parser.add_argument("--manifest", default="dataset_raw_v260/manifest.csv")
    parser.add_argument("--cooldown", type=float, default=2.1)
    args = parser.parse_args()

    rows = load_manifest(args.manifest)
    checks = []

    def add(name, passed, status=None, payload=None, note=""):
        payload = payload or {}
        checks.append({
            "name": name,
            "pass": bool(passed),
            "status": status,
            "ok": payload.get("ok"),
            "success": payload.get("success"),
            "product_id": payload.get("product_id"),
            "product_name": payload.get("product_name"),
            "raw_code": payload.get("raw_code"),
            "error_reason": payload.get("error_reason"),
            "cart_total_cent": cart_total(payload),
            "note": note,
        })

    status, payload = request_json(args.base, "POST", "/api/cart/clear", {})
    add("clear cart before V260 scan matrix", status == 200 and payload.get("ok") is True, status, payload)

    for row in rows:
        product_id = row["product_id"].strip()
        barcode = row["barcode"].strip()
        price_cent = int(row["price_cent"] or 0)

        status, payload = request_json(args.base, "POST", "/api/cart/clear", {})
        add("clear cart before %s" % product_id, status == 200 and payload.get("ok") is True, status, payload)
        time.sleep(args.cooldown)
        status, payload = request_json(args.base, "POST", "/api/scan", {"product_id": product_id})
        add(
            "scan product_id %s" % product_id,
            status == 200
            and payload.get("ok") is True
            and payload.get("success") is True
            and payload.get("product_id") == product_id
            and cart_total(payload) == price_cent,
            status,
            payload,
        )

        status, payload = request_json(args.base, "POST", "/api/cart/clear", {})
        add("clear cart before barcode %s" % product_id, status == 200 and payload.get("ok") is True, status, payload)
        time.sleep(args.cooldown)
        status, payload = request_json(args.base, "POST", "/api/scan", {"barcode": barcode})
        add(
            "scan barcode %s %s" % (product_id, barcode),
            status == 200
            and payload.get("ok") is True
            and payload.get("success") is True
            and payload.get("product_id") == product_id
            and cart_total(payload) == price_cent,
            status,
            payload,
        )

    status, payload = request_json(args.base, "POST", "/api/scan", {"barcode": "UNKNOWN_TEST_001"})
    add(
        "unknown barcode remains explicit",
        status == 200
        and payload.get("ok") is False
        and payload.get("success") is False
        and payload.get("error_reason") == "unknown_barcode",
        status,
        payload,
    )

    status, payload = request_json(args.base, "POST", "/api/cart/clear", {})
    add("clear cart after V260 scan matrix", status == 200 and payload.get("ok") is True, status, payload)

    passed = sum(1 for c in checks if c["pass"])
    failed = len(checks) - passed
    result = {
        "ok": failed == 0,
        "manifest": str(args.manifest),
        "summary": {"total": len(checks), "pass": passed, "fail": failed},
        "checks": checks,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("V260_SCAN_10SKU_CHECKS=%d PASS=%d FAIL=%d" % (len(checks), passed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
