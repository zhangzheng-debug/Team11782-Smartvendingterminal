#!/usr/bin/env python3
import json
import sys
import time
import urllib.error
import urllib.request


BASE = "http://127.0.0.1:5000"
COOLDOWN_SECONDS = 2.1
DEFAULT_PRODUCT_IDS = ["SKU006", "SKU007", "SKU008", "SKU009", "SKU010"]


def request_json(method, path, body=None):
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
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


def cart_total(payload):
    cart = payload.get("cart") or {}
    return int(cart.get("total_cent") or 0)


def load_products():
    status, payload = request_json("GET", "/api/state")
    products = payload.get("products") or payload.get("quick_products") or []
    by_id = {p.get("product_id"): p for p in products if p.get("product_id")}
    rows = []
    for product_id in DEFAULT_PRODUCT_IDS:
        p = by_id.get(product_id)
        if p:
            rows.append({
                "product_id": product_id,
                "product_name": p.get("product_name") or p.get("short_name") or product_id,
                "price_cent": int(p.get("price_cent") or 0),
                "barcode": p.get("barcode") or "",
            })
    if len(rows) != len(DEFAULT_PRODUCT_IDS):
        raise RuntimeError("Unable to load SKU006-SKU010 products from /api/state status=%s" % status)
    return rows


class Matrix:
    def __init__(self):
        self.checks = []

    def add(self, name, passed, status=None, payload=None, note=""):
        payload = payload or {}
        self.checks.append({
            "name": name,
            "pass": bool(passed),
            "status": status,
            "ok": payload.get("ok"),
            "success": payload.get("success"),
            "raw_code": payload.get("raw_code"),
            "product_id": payload.get("product_id"),
            "product_name": payload.get("product_name"),
            "error_reason": payload.get("error_reason"),
            "message": payload.get("message"),
            "cart_total_cent": cart_total(payload),
            "note": note,
        })

    def post(self, path, body):
        status, payload = request_json("POST", path, body)
        return status, payload

    def clear(self):
        status, payload = self.post("/api/cart/clear", {})
        self.add("clear cart", status == 200 and payload.get("ok") is True, status, payload)
        time.sleep(0.2)

    def scan(self, name, body, expected_ok, expected_reason=None, expected_product=None, expected_total=None):
        time.sleep(COOLDOWN_SECONDS)
        status, payload = self.post("/api/scan", body)
        passed = status == 200
        passed = passed and payload.get("ok") is expected_ok
        passed = passed and payload.get("success") is expected_ok
        passed = passed and "raw_code" in payload
        passed = passed and "message" in payload
        passed = passed and "cart" in payload
        passed = passed and "total_price_cent" in payload
        passed = passed and "total_yuan" in payload
        if expected_reason is not None:
            passed = passed and payload.get("error_reason") == expected_reason
        if expected_product is not None:
            passed = passed and payload.get("product_id") == expected_product
        if expected_total is not None:
            passed = passed and cart_total(payload) == expected_total
        self.add(name, passed, status, payload, note="body=%s" % body)
        return payload

    def run(self):
        products = load_products()
        self.clear()

        for product in products:
            sku = product["product_id"]
            name = product["product_name"]
            price_cent = product["price_cent"]
            self.clear()
            payload = self.scan(
                "scan product_id field %s" % sku,
                {"barcode": sku},
                True,
                expected_product=sku,
                expected_total=price_cent,
            )
            self.add("scan response product name %s" % sku, payload.get("product_name") == name, 200, payload)

            barcode = product.get("barcode") or ""
            if barcode and barcode != sku:
                self.clear()
                self.scan(
                    "scan bound barcode %s" % sku,
                    {"barcode": barcode},
                    True,
                    expected_product=sku,
                    expected_total=price_cent,
                )

        self.clear()
        time.sleep(COOLDOWN_SECONDS)
        numeric_status, numeric_payload = self.post("/api/scan", {"barcode": "690000000001"})
        numeric_known = numeric_payload.get("ok") is True and numeric_payload.get("success") is True
        numeric_unknown = (
            numeric_payload.get("ok") is False
            and numeric_payload.get("success") is False
            and numeric_payload.get("error_reason") == "unknown_barcode"
        )
        numeric_passed = (
            numeric_status == 200
            and (numeric_known or numeric_unknown)
            and "raw_code" in numeric_payload
            and "message" in numeric_payload
            and "cart" in numeric_payload
            and "total_price_cent" in numeric_payload
            and "total_yuan" in numeric_payload
        )
        self.add(
            "scan numeric barcode 690000000001 current binding",
            numeric_passed,
            numeric_status,
            numeric_payload,
            note="accepts current DB binding or unknown JSON; does not mutate product data",
        )
        before_unknown_total = cart_total(numeric_payload)

        self.scan(
            "scan unknown text barcode",
            {"barcode": "UNKNOWN_TEST_001"},
            False,
            expected_reason="unknown_barcode",
            expected_total=before_unknown_total,
        )
        self.scan(
            "scan empty barcode",
            {"barcode": ""},
            False,
            expected_reason="empty_scan",
            expected_total=before_unknown_total,
        )

        sku007 = next(p for p in products if p["product_id"] == "SKU007")
        for field in ["barcode", "code", "text", "product_id"]:
            self.clear()
            self.scan(
                "field compatibility %s=SKU007" % field,
                {field: "SKU007"},
                True,
                expected_product="SKU007",
                expected_total=sku007["price_cent"],
            )

        self.clear()
        return self.checks


def main():
    matrix = Matrix()
    checks = matrix.run()
    passed = sum(1 for c in checks if c["pass"])
    failed = len(checks) - passed
    result = {
        "ok": failed == 0,
        "checks": checks,
        "summary": {
            "total": len(checks),
            "pass": passed,
            "fail": failed,
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("SCAN_API_MATRIX_CHECKS=%d PASS=%d FAIL=%d" % (len(checks), passed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
