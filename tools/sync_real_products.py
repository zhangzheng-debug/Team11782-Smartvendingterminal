#!/usr/bin/env python3
import sqlite3
import sys
from pathlib import Path


REAL_PRODUCTS = [
    ("SKU006", "今麦郎纯净水", "今麦郎", "饮料", 200),
    ("SKU007", "舒肤佳沐浴露", "舒肤佳", "日用品", 1690),
    ("SKU008", "洁饶消毒剂", "洁饶", "日用品", 990),
    ("SKU009", "大宝护肤霜", "大宝", "日用品", 1290),
    ("SKU010", "Pantene护发素", "潘婷", "日用品", 1990),
]


def main():
    db_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "/userdata/smart_retail/database/retail_terminal.db"
    )
    if not db_path.exists():
        raise SystemExit(f"database not found: {db_path}")

    conn = sqlite3.connect(str(db_path))
    try:
        for product_id, name, short_name, category, price_cent in REAL_PRODUCTS:
            cur = conn.execute(
                """
                UPDATE products
                SET product_name=?, short_name=?, category=?, price_cent=?, updated_at=datetime('now')
                WHERE product_id=?
                """,
                (name, short_name, category, int(price_cent), product_id),
            )
            if cur.rowcount != 1:
                raise RuntimeError(f"expected one row for {product_id}, updated {cur.rowcount}")
        conn.commit()
        rows = conn.execute(
            """
            SELECT product_id, product_name, short_name, category, price_cent
            FROM products
            WHERE product_id IN ('SKU006','SKU007','SKU008','SKU009','SKU010')
            ORDER BY product_id
            """
        ).fetchall()
        for row in rows:
            print("%s\t%s\t%s\t%s\t%s" % row)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
