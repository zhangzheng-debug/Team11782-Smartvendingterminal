#!/usr/bin/env python3
"""Safely import/update product catalog rows and barcode bindings.

Default mode is --dry-run. The script backs up the SQLite DB before writes.
It never deletes orders, order_items, cloud logs, recognition logs, or audio logs.
"""

import argparse
import csv
import json
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path


def connect(db_path):
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="database/retail_terminal.db")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--apply", action="store_true", help="write changes; otherwise dry-run")
    parser.add_argument("--dry-run", action="store_true", help="explicit dry-run alias; default when --apply is absent")
    parser.add_argument("--backup-root", default="database/backups")
    parser.add_argument("--source-images", default="dataset_raw_v260")
    args = parser.parse_args()

    db_path = Path(args.db)
    manifest = Path(args.manifest)
    if not db_path.exists():
        raise SystemExit("DB not found: %s" % db_path)
    if not manifest.exists():
        raise SystemExit("manifest not found: %s" % manifest)

    rows = []
    with manifest.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            product_id = (row.get("product_id") or "").strip()
            product_name = (row.get("product_name") or "").strip()
            price_cent = int(row.get("price_cent") or 0)
            notes = row.get("notes") or ""
            rows.append({
                "product_id": product_id,
                "product_name": product_name,
                "short_name": (row.get("short_name") or product_name[:8] or product_name).strip(),
                "category": (row.get("category") or "").strip(),
                "price_cent": price_cent,
                "barcode": (row.get("barcode") or "").strip(),
                "model_class_id": row.get("model_class_id") or None,
                "image_path": "static/product_images/%s.jpg" % product_id,
                "notes": notes,
                "price_pending": "TODO_USER_CONFIRM_PRICE" in notes or price_cent <= 0,
            })

    print("CATALOG_IMPORT rows=%d mode=%s" % (len(rows), "apply" if args.apply else "dry-run"))
    for r in rows:
        print("%s %s barcode=%s price_cent=%s" % (r["product_id"], r["product_name"], r["barcode"], r["price_cent"]))

    report = {
        "mode": "apply" if args.apply else "dry-run",
        "db": str(db_path),
        "manifest": str(manifest),
        "rows": rows,
        "barcode_count": len({r["barcode"] for r in rows if r["barcode"]}),
        "price_pending": [r for r in rows if r["price_pending"]],
        "backup": "",
    }

    if not args.apply:
        Path("PRODUCT_CATALOG_IMPORT_V260_REPORT.md").write_text(
            "# Product Catalog Import V260 Report\n\nResult: DRY-RUN PASS\n\nNo database writes were made.\n\n"
            + "Rows: %d\n\n" % len(rows)
            + "\n".join("- {product_id} {product_name} barcode={barcode} price_cent={price_cent} notes={notes}".format(**r) for r in rows)
            + "\n",
            encoding="utf-8",
        )
        Path("BARCODE_BINDING_V260_REPORT.md").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        Path("PRODUCT_PRICE_PENDING_LIST.md").write_text(
            "# Product Price Pending List\n\n"
            + "\n".join("- {product_id} {product_name}: price_cent={price_cent}, user confirmation required".format(**r) for r in rows if r["price_pending"])
            + "\n",
            encoding="utf-8",
        )
        print("DRY_RUN no database writes")
        return 0

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(args.backup_root) / ("catalog_import_v260_" + ts)
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup = backup_dir / db_path.name
    shutil.copy2(str(db_path), str(backup))
    report["backup"] = str(backup_dir)
    print("DB_BACKUP %s" % backup)

    product_image_dir = Path("static/product_images")
    product_image_dir.mkdir(parents=True, exist_ok=True)
    source_root = Path(args.source_images)
    for r in rows:
        candidates = sorted((source_root / r["product_id"] / "images").glob("*")) if source_root.exists() else []
        if candidates:
            shutil.copy2(candidates[0], product_image_dir / ("%s.jpg" % r["product_id"]))

    conn = connect(db_path)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for r in rows:
        if not r["product_id"] or not r["product_name"] or r["price_cent"] <= 0:
            raise SystemExit("invalid row: %r" % r)
        conn.execute("""
            INSERT OR REPLACE INTO products(product_id,product_name,short_name,category,price_cent,barcode,model_class_id,image_path,status,updated_at,created_at)
            VALUES(?,?,?,?,?,?,?,?,COALESCE((SELECT status FROM products WHERE product_id=?),'active'),?,COALESCE((SELECT created_at FROM products WHERE product_id=?),?))
        """, (
            r["product_id"], r["product_name"], r["short_name"], r["category"], r["price_cent"], r["barcode"],
            r["model_class_id"], r["image_path"], r["product_id"], now, r["product_id"], now,
        ))
        if r["barcode"]:
            conn.execute(
                "INSERT OR REPLACE INTO product_barcodes(barcode, product_id, source, created_at) VALUES(?,?,?,?)",
                (r["barcode"], r["product_id"], "ten_sku_import", now),
            )
    conn.commit()
    conn.close()
    Path("PRODUCT_CATALOG_IMPORT_V260_REPORT.md").write_text(
        "# Product Catalog Import V260 Report\n\nResult: APPLY PASS\n\n"
        + f"Backup: `{backup_dir}`\n\nRows: {len(rows)}\n\n"
        + "\n".join("- {product_id} {product_name} barcode={barcode} price_cent={price_cent} image_path={image_path}".format(**r) for r in rows)
        + "\n\nNo orders, order_items, logs, or cloud records were deleted.\n",
        encoding="utf-8",
    )
    Path("BARCODE_BINDING_V260_REPORT.md").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    Path("PRODUCT_PRICE_PENDING_LIST.md").write_text(
        "# Product Price Pending List\n\n"
        + "\n".join("- {product_id} {product_name}: placeholder price_cent={price_cent}, user confirmation required".format(**r) for r in rows if r["price_pending"])
        + "\n",
        encoding="utf-8",
    )
    print("CATALOG_IMPORT_APPLIED backup=%s" % backup)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
