#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Safely update SKU001-SKU010 demo retail prices for V2.6.11-C."""

import argparse
import json
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "database" / "retail_terminal.db"

TARGET_PRICES = {
    "SKU001": ("三元酸奶", 350),
    "SKU002": ("上海硫磺皂", 250),
    "SKU003": ("冠益乳", 790),
    "SKU004": ("燕麦代餐棒", 590),
    "SKU005": ("立顿乌龙茶固体饮料", 1290),
    "SKU006": ("纳美科学牙膏", 1590),
    "SKU007": ("绿豆糕", 890),
    "SKU008": ("西红柿方便面", 550),
    "SKU009": ("魔爪", 700),
    "SKU010": ("鱼油胶囊", 3990),
}


def money(cent):
    return "¥%.2f" % (int(cent) / 100.0)


def connect():
    if not DB_PATH.exists():
        raise SystemExit("database not found: %s" % DB_PATH)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def backup_db():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = DB_PATH.parent / "backups" / ("v2611c_price_update_%s" % ts)
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / DB_PATH.name
    shutil.copy2(str(DB_PATH), str(backup_path))
    return backup_path


def fetch_rows(conn):
    placeholders = ",".join("?" for _ in TARGET_PRICES)
    rows = conn.execute(
        "SELECT product_id, product_name, short_name, price_cent, barcode, model_class_id "
        "FROM products WHERE product_id IN (%s) ORDER BY product_id" % placeholders,
        tuple(TARGET_PRICES.keys()),
    ).fetchall()
    return [dict(r) for r in rows]


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    conn = connect()
    before = fetch_rows(conn)
    found = {r["product_id"] for r in before}
    missing = [sku for sku in TARGET_PRICES if sku not in found]
    if missing:
        raise SystemExit("missing products: " + ",".join(missing))

    changes = []
    for row in before:
        sku = row["product_id"]
        label, target = TARGET_PRICES[sku]
        changes.append({
            "product_id": sku,
            "product_name": row["product_name"],
            "label": label,
            "old_price_cent": int(row["price_cent"]),
            "old_price_text": money(row["price_cent"]),
            "new_price_cent": int(target),
            "new_price_text": money(target),
            "barcode": row.get("barcode"),
            "model_class_id": row.get("model_class_id"),
        })

    backup_path = None
    cart_rows = int(conn.execute("SELECT COUNT(*) AS n FROM cart_items").fetchone()["n"])
    if args.apply:
        backup_path = backup_db()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for sku, (_, target) in TARGET_PRICES.items():
            conn.execute("UPDATE products SET price_cent=?, updated_at=? WHERE product_id=?", (int(target), now, sku))
        if cart_rows:
            conn.execute("DELETE FROM cart_items")
        conn.commit()

    after = fetch_rows(conn)
    conn.close()

    result = {
        "ok": True,
        "mode": "apply" if args.apply else "dry-run",
        "database": str(DB_PATH),
        "backup_path": str(backup_path) if backup_path else "",
        "cart_cleared": bool(args.apply and cart_rows),
        "cart_rows_before": cart_rows,
        "changes": changes,
        "after": after,
        "note": "校园便利店演示参考价；不声明实时线上售价。",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("V2611C_PRICE_UPDATE_%s_OK=True" % ("APPLY" if args.apply else "DRY_RUN"))


if __name__ == "__main__":
    main()
