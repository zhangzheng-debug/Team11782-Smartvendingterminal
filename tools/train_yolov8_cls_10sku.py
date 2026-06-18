#!/usr/bin/env python3
"""Dry-run friendly YOLOv8 classification training launcher for 10 SKU images."""

import argparse
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="YOLO classification dataset root")
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--imgsz", type=int, default=224)
    parser.add_argument("--model", default="yolov8n-cls.pt")
    parser.add_argument("--project", default="runs/retail_10sku")
    parser.add_argument("--name", default="yolov8n_cls_10sku")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    data = Path(args.data)
    cmd = [
        "yolo", "classify", "train",
        "model=%s" % args.model,
        "data=%s" % data,
        "epochs=%d" % args.epochs,
        "imgsz=%d" % args.imgsz,
        "project=%s" % args.project,
        "name=%s" % args.name,
    ]
    print("TRAIN_COMMAND")
    print(" ".join(cmd))
    if not data.exists():
        print("DATASET_MISSING %s" % data)
        return 2
    if not args.execute:
        print("DRY_RUN add --execute to train")
        return 0
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
