#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Normalize a loose 10-SKU vision zip into dataset_raw_v260.

Expected source folders are named like:
  商品名 6921355232318/

The script copies images, assigns stable SKU IDs, validates readability, and
generates manifest/report/contact sheet without modifying the original zip.
"""

import argparse
import csv
import hashlib
import json
import re
import shutil
import tempfile
import zipfile
from dataclasses import dataclass, asdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


CATEGORIES = {
    "三元酸奶": "乳制品",
    "上海硫磺皂": "日用品",
    "冠益乳": "乳制品",
    "燕麦代餐棒": "食品",
    "立顿乌龙茶固体饮料": "冲调饮品",
    "纳美科学牙膏": "日用品",
    "绿豆糕": "糕点",
    "西红柿方便面": "主食",
    "魔爪": "饮料",
    "鱼油胶囊": "营养品",
}

PREFERRED_PRODUCT_ORDER = [
    "三元酸奶",
    "上海硫磺皂",
    "冠益乳",
    "燕麦代餐棒",
    "立顿乌龙茶固体饮料",
    "纳美科学牙膏",
    "绿豆糕",
    "西红柿方便面",
    "魔爪",
    "鱼油胶囊",
]

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
BARCODE_RE = re.compile(r"(\d{8,14})")


@dataclass
class ProductIntake:
    product_id: str
    product_name: str
    barcode: str
    price_cent: int
    category: str
    image_count: int
    train_enabled: bool
    notes: str
    source_dir: str
    min_width: int = 0
    min_height: int = 0
    max_width: int = 0
    max_height: int = 0
    total_bytes: int = 0
    broken_images: int = 0


def parse_product_folder(name: str):
    match = BARCODE_RE.search(name)
    barcode = match.group(1) if match else ""
    product_name = name
    if barcode:
        product_name = name.replace(barcode, "").strip(" -_()（）")
    product_name = product_name.strip() or name.strip()
    return product_name, barcode


def safe_rmtree(path: Path):
    if path.exists():
        shutil.rmtree(path)


def image_info(path: Path):
    try:
        with Image.open(path) as im:
            im.verify()
        with Image.open(path) as im:
            return True, im.size
    except Exception:
        return False, (0, 0)


def sha256_file(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_contact_sheet(rows, out_path: Path, thumbs):
    cols = 5
    thumb_w, thumb_h = 260, 220
    label_h = 72
    rows_count = (len(rows) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows_count * (thumb_h + label_h)), "white")
    draw = ImageDraw.Draw(sheet)
    for idx, row in enumerate(rows):
        x = (idx % cols) * thumb_w
        y = (idx // cols) * (thumb_h + label_h)
        thumb_path = thumbs.get(row.product_id)
        if thumb_path and thumb_path.exists():
            with Image.open(thumb_path) as im:
                im.thumbnail((thumb_w - 20, thumb_h - 20))
                sheet.paste(im.convert("RGB"), (x + (thumb_w - im.width) // 2, y + 10))
        text = f"{row.product_id}\n{row.product_name}\n{row.barcode}\n{row.image_count} images"
        draw.multiline_text((x + 8, y + thumb_h + 4), text, fill=(20, 20, 20), spacing=2)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path, quality=92)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", required=True, dest="zip_path")
    parser.add_argument("--out", default="dataset_raw_v260")
    parser.add_argument("--sku-start", default="SKU001")
    parser.add_argument("--placeholder-price-cent", type=int, default=100)
    args = parser.parse_args()

    zip_path = Path(args.zip_path)
    out = Path(args.out)
    if not zip_path.exists():
        raise SystemExit(f"zip not found: {zip_path}")
    if out.resolve() == zip_path.parent.resolve():
        raise SystemExit("refusing to extract over source zip parent")

    safe_rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="vision_zip_intake_") as tmp:
        tmp_dir = Path(tmp)
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(tmp_dir)

        dirs = []
        for p in tmp_dir.rglob("*"):
            if p.is_dir():
                image_files = [x for x in p.iterdir() if x.is_file() and x.suffix.lower() in IMAGE_EXTS]
                if image_files:
                    dirs.append((p, image_files))
        order_index = {name: idx for idx, name in enumerate(PREFERRED_PRODUCT_ORDER)}
        dirs.sort(key=lambda item: order_index.get(parse_product_folder(item[0].name)[0], 999))

        rows = []
        copy_records = []
        thumbs = {}
        seen_barcodes = set()
        for idx, (src_dir, images) in enumerate(dirs, start=1):
            sku = f"SKU{idx:03d}"
            product_name, barcode = parse_product_folder(src_dir.name)
            category = CATEGORIES.get(product_name, "TODO_USER_CONFIRM_CATEGORY")
            dest_img_dir = out / sku / "images"
            dest_img_dir.mkdir(parents=True, exist_ok=True)
            images = sorted(images, key=lambda p: p.name)
            dims = []
            broken = 0
            total_bytes = 0
            valid_count = 0
            for img_idx, src_img in enumerate(images, start=1):
                ok, size = image_info(src_img)
                total_bytes += src_img.stat().st_size
                if not ok:
                    broken += 1
                    continue
                valid_count += 1
                dims.append(size)
                dest = dest_img_dir / f"{sku}_{valid_count:03d}{src_img.suffix.lower() if src_img.suffix.lower() in IMAGE_EXTS else '.jpg'}"
                shutil.copy2(src_img, dest)
                copy_records.append({
                    "product_id": sku,
                    "source": str(src_img),
                    "dest": str(dest),
                    "sha256": sha256_file(dest),
                    "width": size[0],
                    "height": size[1],
                })
                if sku not in thumbs:
                    thumbs[sku] = dest
            notes = ["TODO_USER_CONFIRM_PRICE", "baseline_low_sample_count"]
            if valid_count < 20:
                notes.append("below_recommended_40_60_images")
            if not barcode:
                notes.append("missing_barcode")
            if barcode in seen_barcodes:
                notes.append("duplicate_barcode")
            seen_barcodes.add(barcode)
            widths = [d[0] for d in dims] or [0]
            heights = [d[1] for d in dims] or [0]
            rows.append(ProductIntake(
                product_id=sku,
                product_name=product_name,
                barcode=barcode,
                price_cent=args.placeholder_price_cent,
                category=category,
                image_count=valid_count,
                train_enabled=valid_count > 0 and bool(barcode),
                notes=";".join(notes),
                source_dir=str(src_dir),
                min_width=min(widths),
                min_height=min(heights),
                max_width=max(widths),
                max_height=max(heights),
                total_bytes=total_bytes,
                broken_images=broken,
            ))

    manifest_path = out / "manifest.csv"
    with manifest_path.open("w", encoding="utf-8-sig", newline="") as f:
        fieldnames = ["product_id", "product_name", "barcode", "price_cent", "category", "image_count", "train_enabled", "notes"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: getattr(row, k) for k in fieldnames})

    (out / "metadata.json").write_text(json.dumps({
        "source_zip": str(zip_path),
        "product_count": len(rows),
        "image_count": sum(r.image_count for r in rows),
        "low_sample_warning": "Current data is suitable for a baseline flow test only; recommended 40-60 images per SKU.",
        "products": [asdict(r) for r in rows],
        "files": copy_records,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    contact_sheet = out / "contact_sheet.jpg"
    write_contact_sheet(rows, contact_sheet, thumbs)
    report = out / "intake_report.md"
    lines = [
        "# Dataset Intake V260 Report",
        "",
        "Result: PASS" if len(rows) == 10 and all(r.image_count > 0 for r in rows) else "Result: FAIL",
        "",
        "This is a 10-SKU baseline dataset. It is not a final high-confidence production dataset.",
        "",
        "| SKU | Product | Barcode | Images | Category | Notes |",
        "|---|---|---:|---:|---|---|",
    ]
    for r in rows:
        lines.append(f"| {r.product_id} | {r.product_name} | {r.barcode} | {r.image_count} | {r.category} | {r.notes} |")
    lines.extend([
        "",
        f"Total images: {sum(r.image_count for r in rows)}",
        f"Contact sheet: `{contact_sheet}`",
        "",
        "Honest limitation: each class currently has about 9-20 images; continue collecting until 40-60 images per SKU.",
    ])
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")

    shutil.copy2(manifest_path, "TEN_SKU_MANIFEST_V260.csv")
    shutil.copy2(report, "DATASET_INTAKE_V260_REPORT.md")
    shutil.copy2(contact_sheet, "DATASET_CONTACT_SHEET_V260.jpg")
    Path("DATASET_QUALITY_SUMMARY_V260.md").write_text(report.read_text(encoding="utf-8"), encoding="utf-8")
    print(json.dumps({
        "ok": len(rows) == 10 and all(r.image_count > 0 for r in rows),
        "out": str(out),
        "products": len(rows),
        "images": sum(r.image_count for r in rows),
        "manifest": str(manifest_path),
        "contact_sheet": str(contact_sheet),
    }, ensure_ascii=False, indent=2))
    return 0 if len(rows) == 10 and all(r.image_count > 0 for r in rows) else 2


if __name__ == "__main__":
    raise SystemExit(main())
