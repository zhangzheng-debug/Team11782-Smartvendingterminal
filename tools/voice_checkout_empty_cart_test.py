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
    before = order_count()
    status, data = post("/api/speech/session_step", {"button_wake": True, "text": "四号结账"})
    after = order_count()
    action = data.get("action_result") or {}
    ui_action = data.get("ui_action") or action.get("ui_action")
    error_reason = data.get("error_reason") or action.get("error_reason")

    checks.append(check("response json", status == 200 and data.get("intent") == "checkout", status=status, intent=data.get("intent")))
    checks.append(check("cart_empty returned", data.get("success") is False and error_reason == "cart_empty",
                        success=data.get("success"), error_reason=error_reason))
    checks.append(check("ui_action show_error", ui_action == "show_error", ui_action=ui_action))
    checks.append(check("no order returned", not (data.get("order") or action.get("order")),
                        order=data.get("order"), action_order=action.get("order")))
    checks.append(check("no new order created", after == before, before=before, after=after))

    passed = sum(1 for c in checks if c["pass"])
    result = {"ok": passed == len(checks), "checks": checks,
              "summary": {"total": len(checks), "pass": passed, "fail": len(checks) - passed}}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("VOICE_CHECKOUT_EMPTY_CART_CHECKS=%d PASS=%d FAIL=%d" % (len(checks), passed, len(checks) - passed))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
