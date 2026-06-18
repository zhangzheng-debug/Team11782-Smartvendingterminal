#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Terminal kiosk fallback for Weston terminal.

This is a no-Qt cashier UI. It talks only to the Flask JSON API and keeps all
business logic in Flask + SQLite.
"""

import argparse
import json
import os
import shutil
import sys
import textwrap
import time
import urllib.error
import urllib.request


DEFAULT_BASE = "http://127.0.0.1:5000"


def api_request(base_url, method, path, body=None, timeout=8):
    url = base_url.rstrip("/") + path
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "replace")
            return resp.status, json.loads(raw or "{}")
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        try:
            return exc.code, json.loads(raw or "{}")
        except Exception:
            return exc.code, {"ok": False, "error": "http_error", "message": raw}
    except Exception as exc:
        return 0, {"ok": False, "error": "network_error", "message": str(exc)}


def api_get(base_url, path):
    return api_request(base_url, "GET", path)


def api_post(base_url, path, body=None):
    return api_request(base_url, "POST", path, body or {})


def clip(value, width):
    text = str(value or "")
    if width <= 0:
        return ""
    if len(text) <= width:
        return text
    if width <= 3:
        return text[:width]
    return text[: width - 3] + "..."


def money(value):
    if value is None:
        return "0.00"
    return str(value).replace("¥", "CNY ")


def clear_screen():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


class TerminalKiosk:
    def __init__(self, base_url, once=False):
        self.base_url = base_url.rstrip("/")
        self.once = once
        self.state = {}
        self.http_status = 0
        self.message = "Starting terminal kiosk fallback"
        self.last_action = "-"

    def refresh(self):
        status, data = api_get(self.base_url, "/api/state")
        self.http_status = status
        if status == 200 and data.get("ok"):
            self.state = data
            return True
        self.message = "API offline: %s" % (data.get("message") or data.get("error") or status)
        return False

    def render(self):
        columns, rows = shutil.get_terminal_size((100, 30))
        cart = self.state.get("cart") or {}
        products = self.state.get("products") or []
        latest_order = self.state.get("latest_order") or {}
        latest_speech = self.state.get("latest_speech_text") or "-"
        parsed = self.state.get("latest_speech_parsed") or {}
        audio = self.state.get("audio") or {}

        clear_screen()
        print("=" * columns)
        title = "QSM368ZP-WF Smart Retail Terminal - V2.5.6 Terminal Kiosk"
        print(clip(title, columns))
        print(clip("API: %s  HTTP: %s  Time: %s" % (self.base_url, self.http_status, self.state.get("time", "-")), columns))
        print("=" * columns)
        print("Cart: %s item(s)    Total: %s" % (cart.get("count", 0), money(cart.get("total_text", "0.00"))))
        print("-" * columns)

        cart_items = cart.get("items") or []
        if cart_items:
            print("%-8s %-32s %6s %12s" % ("SKU", "Name", "Qty", "Subtotal"))
            for item in cart_items[:8]:
                print(
                    "%-8s %-32s %6s %12s"
                    % (
                        clip(item.get("product_id"), 8),
                        clip(item.get("product_name"), 32),
                        item.get("quantity", 0),
                        money(item.get("subtotal_text")),
                    )
                )
            if len(cart_items) > 8:
                print("... %d more cart line(s)" % (len(cart_items) - 8))
        else:
            print("Cart is empty. Scan a barcode or type a SKU/barcode below.")

        print("-" * columns)
        print("Quick products:")
        for product in products[:10]:
            print(
                "  %-8s %-24s %s"
                % (
                    clip(product.get("product_id"), 8),
                    clip(product.get("short_name") or product.get("product_name"), 24),
                    money(product.get("price_text")),
                )
            )

        print("-" * columns)
        order_text = "-"
        if latest_order:
            order_text = "%s %s %s" % (
                latest_order.get("order_id", "-"),
                latest_order.get("payment_status", "-"),
                money(latest_order.get("total_text")),
            )
        print(clip("Latest order: " + order_text, columns))
        print(clip("Speech: %s  Intent: %s" % (latest_speech, parsed.get("intent", "-")), columns))
        print(clip("Audio out: %s" % audio.get("output_device", "-"), columns))
        print(clip("Last action: %s" % self.last_action, columns))
        print(clip("Status: %s" % self.message, columns))
        print("=" * columns)
        print("Commands: barcode | SKU001 | clear | del | checkout | refresh | speech <text> | help | quit")
        print()

    def command_help(self):
        self.message = (
            "Type a barcode/SKU to add. Commands: clear, del, checkout, refresh, "
            "speech <text>, quit."
        )

    def handle_scan_or_sku(self, text):
        if text.upper().startswith("SKU"):
            status, data = api_post(self.base_url, "/api/cart/add", {"product_id": text.upper(), "quantity": 1})
            self.last_action = "add %s" % text.upper()
        else:
            status, data = api_post(self.base_url, "/api/scan", {"barcode": text})
            self.last_action = "scan %s" % text
        self.message = data.get("message") or data.get("status") or data.get("error") or ("HTTP %s" % status)

    def handle_checkout(self):
        status, data = api_post(self.base_url, "/api/checkout", {})
        self.last_action = "checkout"
        if status == 200 and data.get("ok"):
            self.message = "Order %s total %s QR %s" % (
                data.get("order_id"),
                money(data.get("total_cent")),
                data.get("qr_image_url"),
            )
        else:
            self.message = data.get("message") or data.get("error") or ("HTTP %s" % status)

    def handle_speech(self, text):
        if not text:
            self.last_action = "speech"
            self.message = "Speech hardware loop is reserved. Use: speech <recognized text>"
            return
        status, data = api_post(self.base_url, "/api/speech/execute", {"text": text})
        self.last_action = "speech %s" % text
        if data.get("confirm_required"):
            self.message = "Speech intent %s needs confirmation in API; not executed." % data.get("intent")
        else:
            self.message = data.get("result") or data.get("message") or data.get("error") or ("HTTP %s" % status)

    def handle_command(self, line):
        text = (line or "").strip()
        if not text:
            self.refresh()
            self.message = "Refreshed"
            return True

        lower = text.lower()
        if lower in {"q", "quit", "exit"}:
            self.last_action = "quit"
            self.message = "Leaving terminal kiosk"
            return False
        if lower in {"help", "?"}:
            self.last_action = "help"
            self.command_help()
        elif lower == "refresh":
            self.last_action = "refresh"
            self.refresh()
            self.message = "Refreshed"
        elif lower == "clear":
            status, data = api_post(self.base_url, "/api/cart/clear", {})
            self.last_action = "clear"
            self.message = data.get("message") or data.get("status") or data.get("error") or ("HTTP %s" % status)
        elif lower in {"del", "delete", "remove_last"}:
            status, data = api_post(self.base_url, "/api/cart/remove_last", {})
            self.last_action = "delete last"
            self.message = data.get("status") or data.get("message") or data.get("error") or ("HTTP %s" % status)
        elif lower == "checkout":
            self.handle_checkout()
        elif lower.startswith("speech"):
            self.handle_speech(text[6:].strip())
        else:
            self.handle_scan_or_sku(text)

        self.refresh()
        return True

    def run_once(self):
        self.refresh()
        self.render()

    def run(self):
        self.refresh()
        if self.once:
            self.render()
            return 0

        while True:
            self.render()
            try:
                line = input("scan/cmd> ")
            except (EOFError, KeyboardInterrupt):
                print()
                return 0
            if not self.handle_command(line):
                self.render()
                return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Terminal kiosk fallback for QSM368ZP-WF.",
        epilog=textwrap.dedent(
            """\
            Examples:
              python3 terminal_kiosk.py
              python3 terminal_kiosk.py --once
              python3 terminal_kiosk.py --base http://127.0.0.1:5000
            """
        ),
    )
    parser.add_argument("--base", default=os.environ.get("RETAIL_API_BASE", DEFAULT_BASE))
    parser.add_argument("--once", action="store_true", help="render one screen and exit")
    args = parser.parse_args(argv)

    kiosk = TerminalKiosk(args.base, once=args.once)
    return kiosk.run()


if __name__ == "__main__":
    raise SystemExit(main())

