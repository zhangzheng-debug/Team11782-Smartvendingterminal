#!/usr/bin/env python3
"""Validate the 10-SKU image/barcode intake folder before training.

Expected manifest columns:
product_id,product_name,short_name,category,price_cent,barcode,image_dir
"""

import argparse
import csv
import json
from pathlib import Path


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--dataset-root", required=True)
    parser.add_argument("--min-skus", type=int, default=10)
    parser.add_argument("--min-images-per-sku", type=int, default=20)
    parser.add_argument("--report", default="")
    args = parser.parse_args()

    manifest = Path(args.manifest)
    root = Path(args.dataset_root)
    required = {"product_id", "product_name", "short_name", "category", "price_cent", "barcode", "image_dir"}
    checks = []
    rows = []
    errors = []

    if not manifest.exists():
        errors.append("manifest not found: %s" % manifest)
    if not root.exists():
        errors.append("dataset root not found: %s" % root)

    if not errors:
        with manifest.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            missing = required - set(reader.fieldnames or [])
            if missing:
                errors.append("manifest missing columns: %s" % ", ".join(sorted(missing)))
            else:
                for row in reader:
                    pid = (row.get("product_id") or "").strip()
                    img_dir = root / (row.get("image_dir") or pid)
                    images = [p for p in img_dir.rglob("*") if p.suffix.lower() in IMAGE_EXTS] if img_dir.exists() else []
                    ok = bool(pid) and img_dir.exists() and len(images) >= args.min_images_per_sku
                    checks.append({
                        "product_id": pid,
                        "product_name": row.get("product_name", ""),
                        "barcode": row.get("barcode", ""),
                        "image_dir": str(img_dir),
                        "image_count": len(images),
                        "ok": ok,
                    })
                    if not ok:
                        errors.append("%s has %d images, need >= %d" % (pid or "missing_product_id", len(images), args.min_images_per_sku))
                    rows.append(row)

    unique_ids = {r.get("product_id", "").strip() for r in rows if r.get("product_id", "").strip()}
    unique_barcodes = {r.get("barcode", "").strip() for r in rows if r.get("barcode", "").strip()}
    if len(unique_ids) < args.min_skus:
        errors.append("only %d unique SKUs, need >= %d" % (len(unique_ids), args.min_skus))
    if len(unique_barcodes) < args.min_skus:
        errors.append("only %d unique barcodes, need >= %d" % (len(unique_barcodes), args.min_skus))

    report = {
        "ok": not errors,
        "manifest": str(manifest),
        "dataset_root": str(root),
        "sku_count": len(unique_ids),
        "barcode_count": len(unique_barcodes),
        "checks": checks,
        "errors": errors,
    }
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        Path(args.report).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
