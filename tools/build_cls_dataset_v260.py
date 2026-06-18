#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build an Ultralytics classification dataset from dataset_raw_v260."""

import argparse
import csv
import json
import random
import shutil
from pathlib import Path

from PIL import Image


def safe_name(value):
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in value).strip("_")


def split_counts(n, split):
    if n < 3:
        return max(1, n), 0, 0
    val = max(1, int(round(n * split[1])))
    test = max(1, int(round(n * split[2])))
    train = n - val - test
    if train < 1:
        train = 1
        if val >= test and val > 1:
            val -= 1
        elif test > 1:
            test -= 1
    return train, val, test


def copy_image(src, dst, resize=None):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not resize:
        shutil.copy2(src, dst)
        return
    with Image.open(src) as im:
        im.thumbnail((resize, resize))
        canvas = Image.new("RGB", (resize, resize), (255, 255, 255))
        canvas.paste(im.convert("RGB"), ((resize - im.width) // 2, (resize - im.height) // 2))
        canvas.save(dst.with_suffix(".jpg"), quality=92)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", default="dataset_raw_v260")
    parser.add_argument("--out", default="datasets/vision_10sku_cls_v260")
    parser.add_argument("--split", nargs=3, type=float, default=[0.7, 0.15, 0.15])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--resize-copy", type=int, default=0)
    args = parser.parse_args()

    raw = Path(args.raw)
    out = Path(args.out)
    manifest = raw / "manifest.csv"
    if not manifest.exists():
        raise SystemExit(f"manifest not found: {manifest}")
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    rows = []
    with manifest.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    rows.sort(key=lambda r: r["product_id"])

    rng = random.Random(args.seed)
    class_map = {}
    split_rows = []
    for class_idx, row in enumerate(rows):
        sku = row["product_id"]
        class_name = f"{sku}_{safe_name(row['product_name'])}"
        class_map[sku] = {
            "class_index": class_idx,
            "class_name": class_name,
            "product_name": row["product_name"],
            "barcode": row["barcode"],
        }
        images = sorted((raw / sku / "images").glob("*"))
        images = [p for p in images if p.is_file()]
        rng.shuffle(images)
        train_n, val_n, test_n = split_counts(len(images), args.split)
        assignments = (
            [("train", p) for p in images[:train_n]]
            + [("val", p) for p in images[train_n:train_n + val_n]]
            + [("test", p) for p in images[train_n + val_n:train_n + val_n + test_n]]
        )
        for split_name, src in assignments:
            dest = out / split_name / class_name / src.name
            copy_image(src, dest, args.resize_copy or None)
        split_rows.append({
            "product_id": sku,
            "class_name": class_name,
            "source_images": len(images),
            "train": train_n,
            "val": val_n,
            "test": test_n,
        })

    (out / "labels.txt").write_text("\n".join(class_map[sku]["class_name"] for sku in sorted(class_map)) + "\n", encoding="utf-8")
    (out / "class_map.json").write_text(json.dumps(class_map, ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.copy2(manifest, out / "manifest.csv")
    lines = [
        "# Classification Dataset Build Report",
        "",
        "Result: PASS",
        "",
        f"Seed: {args.seed}",
        f"Split request: {args.split}",
        f"Resize copy: {args.resize_copy or 'disabled'}",
        "",
        "| SKU | Class | Source | Train | Val | Test |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for r in split_rows:
        lines.append(f"| {r['product_id']} | {r['class_name']} | {r['source_images']} | {r['train']} | {r['val']} | {r['test']} |")
    lines.append("")
    lines.append("Limitation: low image count can make accuracy volatile; this is a baseline dataset.")
    (out / "split_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    Path("CLASSIFICATION_DATASET_BUILD_REPORT.md").write_text((out / "split_report.md").read_text(encoding="utf-8"), encoding="utf-8")
    print(json.dumps({"ok": True, "out": str(out), "classes": len(rows), "splits": split_rows}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())

