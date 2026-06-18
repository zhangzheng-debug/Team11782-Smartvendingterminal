#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2.6.6 cart total UI-source consistency gate."""

import json
import sys
import urllib.request

BASE = "http://127.0.0.1:5000"


def req(method, path, payload=None):
    data = json.dumps(payload or {}).encode("utf-8") if method == "POST" else None
    request = urllib.request.Request(BASE + path, data=data, headers={"Content-Type": "application/json"}, method=method)
    with urllib.request.urlopen(request, timeout=12) as resp:
        return json.loads(resp.read().decode("utf-8", "replace"))


def state_check(label, expected_count=None):
    s = req("GET", "/api/state")
    items = s.get("cart_items") or []
    recomputed = sum(int(i.get("subtotal_cent") or 0) for i in items)
    total = int(s.get("cart_total_cent") or 0)
    ok = bool(s.get("cart_total_consistency_ok")) and recomputed == total
    if expected_count is not None:
        ok = ok and int(s.get("cart_count") or 0) == expected_count
    return {
        "label": label,
        "pass": ok,
        "cart_count": s.get("cart_count"),
        "cart_total_cent": total,
        "cart_total_yuan": s.get("cart_total_yuan"),
        "cart_total_recomputed_cent": s.get("cart_total_recomputed_cent"),
        "item_sum_cent": recomputed,
        "cart_total_consistency_ok": s.get("cart_total_consistency_ok"),
    }


def main():
    checks = []
    req("POST", "/api/cart/clear")
    checks.append(state_check("clear", 0))
    req("POST", "/api/scan", {"barcode": "SKU006"})
    checks.append(state_check("add_SKU006", 1))
    req("POST", "/api/scan", {"barcode": "SKU007"})
    checks.append(state_check("add_SKU007", 2))
    req("POST", "/api/cart/remove_last")
    checks.append(state_check("remove_last", 1))
    req("POST", "/api/cart/clear")
    checks.append(state_check("clear_final", 0))
    ok = all(c["pass"] for c in checks)
    print(json.dumps({"ok": ok, "checks": checks}, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
