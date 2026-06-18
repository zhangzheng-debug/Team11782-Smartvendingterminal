#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sqlite3
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "database" / "retail_terminal.db"
BASE = "http://127.0.0.1:5000"


def post(path, payload):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
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


def order_count():
    conn = sqlite3.connect(str(DB_PATH))
    n = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    conn.close()
    return int(n)


def check(name, passed, **extra):
    item = {"name": name, "pass": bool(passed)}
    item.update(extra)
    return item


def main():
    checks = []
    post("/api/cart/clear", {})
    post("/api/cart/add", {"product_id": "SKU001", "quantity": 1})
    before = order_count()
    status, data = post("/api/speech/session_step", {"button_wake": True, "text": "四号结账"})
    after = order_count()
    action = data.get("action_result") or {}
    order = data.get("order") or action.get("order") or {}
    order_id = order.get("order_id") or data.get("order_id") or action.get("order_id")
    status_state, state = get("/api/state")
    latest = state.get("latest_order") or {}

    checks.append(check("speech session response ok", status == 200 and data.get("intent") == "checkout", status=status, intent=data.get("intent")))
    checks.append(check("ui_action open_payment_dialog", (data.get("ui_action") or action.get("ui_action")) == "open_payment_dialog",
                        ui_action=data.get("ui_action"), action_ui=action.get("ui_action")))
    checks.append(check("order returned", bool(order_id and order), order_id=order_id))
    checks.append(check("qr exists", bool(order.get("qr_exists")), qr_exists=order.get("qr_exists")))
    checks.append(check("payment_qr_file_url present", bool(order.get("payment_qr_file_url")), value=order.get("payment_qr_file_url")))
    checks.append(check("payment fields present", bool(order.get("payment_mode") and order.get("payment_qr_content")),
                        payment_mode=order.get("payment_mode"), payment_qr_content=order.get("payment_qr_content")))
    checks.append(check("latest_order matches returned order", status_state == 200 and latest.get("order_id") == order_id,
                        latest_order_id=latest.get("order_id"), order_id=order_id))
    checks.append(check("one order created", after == before + 1, before=before, after=after))
    checks.append(check("cart cleared by checkout", int((state.get("cart") or {}).get("total_cent", -1)) == 0,
                        cart=state.get("cart")))

    post("/api/cart/clear", {})
    passed = sum(1 for c in checks if c["pass"])
    result = {"ok": passed == len(checks), "checks": checks,
              "summary": {"total": len(checks), "pass": passed, "fail": len(checks) - passed}}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("VOICE_CHECKOUT_DIALOG_CONTRACT_CHECKS=%d PASS=%d FAIL=%d" % (len(checks), passed, len(checks) - passed))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
