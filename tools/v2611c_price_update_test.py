#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sqlite3
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "database" / "retail_terminal.db"
BASE = "http://127.0.0.1:5000"

EXPECTED = {
    "SKU001": 350,
    "SKU002": 250,
    "SKU003": 790,
    "SKU004": 590,
    "SKU005": 1290,
    "SKU006": 1590,
    "SKU007": 890,
    "SKU008": 550,
    "SKU009": 700,
    "SKU010": 3990,
}


def post(path, payload):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8", "replace") or "{}")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        try:
            return exc.code, json.loads(body or "{}")
        except Exception:
            return exc.code, {"raw": body}


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=12) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8", "replace") or "{}")


def check(name, passed, **extra):
    item = {"name": name, "pass": bool(passed)}
    item.update(extra)
    return item


def cart_total(payload):
    return int(((payload or {}).get("cart") or {}).get("total_cent") or 0)


def main():
    checks = []
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT product_id, product_name, price_cent FROM products "
        "WHERE product_id BETWEEN 'SKU001' AND 'SKU010' ORDER BY product_id"
    ).fetchall()
    conn.close()
    db_prices = {r["product_id"]: int(r["price_cent"]) for r in rows}

    for sku, expected in EXPECTED.items():
        checks.append(check("db price %s" % sku, db_prices.get(sku) == expected,
                            actual=db_prices.get(sku), expected=expected))

    status, state = get("/api/state")
    products = {p.get("product_id"): p for p in ((state.get("quick_products") or []) + (state.get("products") or []))}
    checks.append(check("/api/state ok", status == 200 and state.get("ok") is True, status=status))
    for sku, expected in EXPECTED.items():
        p = products.get(sku) or {}
        checks.append(check("api price %s" % sku, int(p.get("price_cent") or -1) == expected,
                            actual=p.get("price_cent"), expected=expected, price_text=p.get("price_text")))

    post("/api/cart/clear", {})
    time.sleep(2.2)
    status, scan1 = post("/api/scan", {"barcode": "SKU001"})
    checks.append(check("scan SKU001 total ¥3.50", status == 200 and scan1.get("ok") is True and cart_total(scan1) == 350,
                        status=status, total=cart_total(scan1), product=scan1.get("product_id")))
    time.sleep(2.2)
    status, scan9 = post("/api/scan", {"barcode": "SKU009"})
    checks.append(check("scan SKU009 adds ¥7.00", status == 200 and scan9.get("ok") is True and cart_total(scan9) == 1050,
                        status=status, total=cart_total(scan9), product=scan9.get("product_id")))
    status, state2 = get("/api/state")
    checks.append(check("cart_total_consistency_ok", status == 200 and state2.get("cart_total_consistency_ok") is True,
                        status=status, total=state2.get("cart_total_cent")))
    post("/api/cart/clear", {})

    passed = sum(1 for c in checks if c["pass"])
    result = {"ok": passed == len(checks), "checks": checks,
              "summary": {"total": len(checks), "pass": passed, "fail": len(checks) - passed}}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("V2611C_PRICE_UPDATE_CHECKS=%d PASS=%d FAIL=%d" % (len(checks), passed, len(checks) - passed))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
