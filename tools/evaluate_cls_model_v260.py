#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Evaluate an Ultralytics classification model on a test split."""

import argparse
import csv
import json
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--data", default="datasets/vision_10sku_cls_v260")
    parser.add_argument("--out", default="MODEL_ARTIFACTS_V260")
    parser.add_argument("--imgsz", type=int, default=224)
    args = parser.parse_args()

    from ultralytics import YOLO

    data = Path(args.data)
    out = Path(args.out)
    wrong_dir = out / "wrong_predictions"
    wrong_dir.mkdir(parents=True, exist_ok=True)
    labels = (data / "labels.txt").read_text(encoding="utf-8").splitlines()
    model = YOLO(args.model)

    total = 0
    top1_ok = 0
    top3_ok = 0
    per_class = {label: {"total": 0, "top1": 0, "top3": 0} for label in labels}
    predictions = []
    for class_dir in sorted((data / "test").iterdir()):
        if not class_dir.is_dir():
            continue
        true_label = class_dir.name
        for img in sorted(class_dir.glob("*")):
            if not img.is_file():
                continue
            result = model.predict(str(img), imgsz=args.imgsz, verbose=False)[0]
            probs = result.probs
            top5 = probs.top5 if hasattr(probs, "top5") else []
            names = result.names
            top_labels = [names[int(i)] for i in top5[:3]]
            top1 = top_labels[0] if top_labels else ""
            confs = [float(probs.data[int(i)]) for i in top5[:3]]
            total += 1
            per_class[true_label]["total"] += 1
            is_top1 = top1 == true_label
            is_top3 = true_label in top_labels
            top1_ok += int(is_top1)
            top3_ok += int(is_top3)
            per_class[true_label]["top1"] += int(is_top1)
            per_class[true_label]["top3"] += int(is_top3)
            predictions.append({
                "image": str(img),
                "true": true_label,
                "top1": top1,
                "top3": "|".join(top_labels),
                "confidences": "|".join(f"{c:.4f}" for c in confs),
                "top1_ok": is_top1,
                "top3_ok": is_top3,
            })
            if not is_top1:
                shutil.copy2(img, wrong_dir / f"{true_label}__pred_{top1}__{img.name}")

    out.mkdir(parents=True, exist_ok=True)
    with (out / "predictions.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["image", "true", "top1", "top3", "confidences", "top1_ok", "top3_ok"])
        writer.writeheader()
        writer.writerows(predictions)
    per_class_rows = []
    for label, stats in per_class.items():
        n = stats["total"]
        per_class_rows.append({
            "class": label,
            "total": n,
            "top1_acc": round(stats["top1"] / n, 4) if n else 0,
            "top3_acc": round(stats["top3"] / n, 4) if n else 0,
        })
    with (out / "per_class_accuracy.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["class", "total", "top1_acc", "top3_acc"])
        writer.writeheader()
        writer.writerows(per_class_rows)

    summary = {
        "ok": total > 0,
        "model": args.model,
        "data": str(data),
        "test_images": total,
        "top1_accuracy": round(top1_ok / total, 4) if total else 0,
        "top3_accuracy": round(top3_ok / total, 4) if total else 0,
        "per_class": per_class_rows,
        "warning": "Low sample count baseline; do not represent as final production accuracy.",
    }
    (out / "evaluation_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Evaluation Report V260",
        "",
        "Result: PASS" if summary["ok"] else "Result: FAIL",
        "",
        f"Top-1 accuracy: {summary['top1_accuracy']}",
        f"Top-3 accuracy: {summary['top3_accuracy']}",
        f"Test images: {summary['test_images']}",
        "",
        "| Class | Test | Top-1 | Top-3 |",
        "|---|---:|---:|---:|",
    ]
    for r in per_class_rows:
        lines.append(f"| {r['class']} | {r['total']} | {r['top1_acc']} | {r['top3_acc']} |")
    lines.append("")
    lines.append("Honest limitation: this is a low-sample 10-SKU baseline.")
    (out / "EVALUATION_REPORT_V260.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    shutil.copy2(out / "EVALUATION_REPORT_V260.md", "EVALUATION_REPORT_V260.md")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

