#!/usr/bin/env python3
import json
import sys
import time
import urllib.error
import urllib.request


BASE = "http://127.0.0.1:5000"


def summarize(payload):
    cart = payload.get("cart") or {}
    order = payload.get("order") or {}
    bits = []
    for key in ["status", "error", "intent", "corrected", "confirm_required", "message"]:
        if key in payload:
            bits.append("%s=%s" % (key, payload.get(key)))
    if cart:
        bits.append("cart=%s/%s" % (cart.get("count"), cart.get("total_text")))
    if order:
        bits.append("order=%s/%s/%s" % (order.get("order_id"), order.get("total_text"), order.get("payment_status")))
    if "order_id" in payload:
        bits.append("order_id=" + str(payload.get("order_id")))
    return "; ".join(bits)


class Runner:
    def __init__(self):
        self.results = []

    def req(self, method, path, body=None, expect_ok=True):
        data = None
        headers = {"Accept": "application/json"}
        if body is not None:
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                status = response.getcode()
                raw = response.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:
            status = exc.code
            raw = exc.read().decode("utf-8", "replace")
        except Exception as exc:
            self.results.append({"step": method + " " + path, "pass": False, "error": repr(exc)})
            return {}
        try:
            payload = json.loads(raw or "{}")
        except Exception:
            payload = {"raw": raw}
        ok = 200 <= status < 300 and payload.get("ok") is not False
        passed = ok if expect_ok else not ok
        self.results.append({
            "step": method + " " + path,
            "status": status,
            "ok": payload.get("ok"),
            "pass": bool(passed),
            "summary": summarize(payload),
        })
        return payload

    def state(self, label):
        payload = self.req("GET", "/api/state")
        cart = payload.get("cart", {})
        latest_order = payload.get("latest_order") or {}
        self.results.append({
            "step": "STATE " + label,
            "pass": True,
            "summary": "cart=%s/%s lines=%s latest_order=%s" % (
                cart.get("count"),
                cart.get("total_text"),
                cart.get("line_count"),
                latest_order.get("order_id"),
            ),
        })
        return payload

    def product(self, product_id, state):
        products = state.get("products") or state.get("quick_products") or []
        for product in products:
            if product.get("product_id") == product_id:
                return product
        raise RuntimeError("Product not found in /api/state: %s" % product_id)

    def run(self):
        self.req("POST", "/api/cart/clear", {})
        initial = self.state("initial_empty")
        sku006 = self.product("SKU006", initial)
        sku007 = self.product("SKU007", initial)

        self.req("POST", "/api/cart/add", {"product_id": "SKU006", "quantity": 1})
        time.sleep(1.2)
        self.state("after_add_SKU006")
        self.req("POST", "/api/cart/add", {"product_id": "SKU007", "quantity": 1})
        time.sleep(1.2)
        self.state("after_add_SKU007")

        self.req("POST", "/api/scan", {"barcode": sku006.get("barcode") or "SKU006"})
        time.sleep(1.2)
        self.state("after_scan_SKU006_barcode")
        self.req("POST", "/api/scan", {"barcode": "SKU006"})
        time.sleep(1.2)
        self.state("after_scan_SKU006_product_id")

        self.req("POST", "/api/cart/remove_last", {})
        time.sleep(1.2)
        self.state("after_remove_last")
        self.req("POST", "/api/cart/remove_product", {"product_id": "SKU006"})
        time.sleep(1.2)
        self.state("after_remove_product_SKU006")

        self.req("POST", "/api/cart/clear", {})
        time.sleep(1.2)
        self.state("after_clear")
        self.req("POST", "/api/checkout", {}, expect_ok=False)

        self.req("POST", "/api/cart/add", {"product_id": "SKU006", "quantity": 1})
        checkout = self.req("POST", "/api/checkout", {})
        order_id = checkout.get("order_id") or (checkout.get("order") or {}).get("order_id")
        time.sleep(1.2)
        self.state("after_checkout")
        if order_id:
            self.req("GET", "/api/order/" + str(order_id))

        self.req("POST", "/api/cart/clear", {})
        self.req("POST", "/api/cart/add", {"product_id": "SKU006", "quantity": 1})
        self.req("POST", "/api/speech/execute", {"text": "一共多少钱", "confirmed": False})
        self.req("POST", "/api/speech/execute", {"text": "删除上一件", "confirmed": False})
        self.req("POST", "/api/cart/add", {"product_id": "SKU007", "quantity": 1})
        self.req("POST", "/api/speech/execute", {"text": "我要截正", "confirmed": False})
        self.state("after_speech_tests")

        self.req("POST", "/api/cart/clear", {})
        self.req("POST", "/api/cart/add", {"product_id": "SKU001", "quantity": 1})
        voice_checkout = self.req("POST", "/api/speech/session_step", {"button_wake": True, "text": "四号结账"})
        action = voice_checkout.get("action_result") or {}
        order = voice_checkout.get("order") or action.get("order") or {}
        self.results.append({
            "step": "VOICE checkout opens payment dialog contract",
            "pass": (
                voice_checkout.get("intent") == "checkout"
                and (voice_checkout.get("ui_action") or action.get("ui_action")) == "open_payment_dialog"
                and bool(order.get("order_id"))
                and bool(order.get("qr_exists"))
            ),
            "summary": "intent=%s ui_action=%s order=%s" % (
                voice_checkout.get("intent"),
                voice_checkout.get("ui_action") or action.get("ui_action"),
                order.get("order_id"),
            ),
        })

        self.req("POST", "/api/cart/clear", {})
        final = self.state("final_empty")
        return {"results": self.results, "final_cart": final.get("cart", {}), "products_used": [sku006, sku007]}


def main():
    result = Runner().run()
    failed = [r for r in result["results"] if not r.get("pass")]
    result["ok"] = not failed
    result["summary"] = {"total": len(result["results"]), "pass": len(result["results"]) - len(failed), "fail": len(failed)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("QML_BUSINESS_CHECKS=%d PASS=%d FAIL=%d" % (
        result["summary"]["total"],
        result["summary"]["pass"],
        result["summary"]["fail"],
    ))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
