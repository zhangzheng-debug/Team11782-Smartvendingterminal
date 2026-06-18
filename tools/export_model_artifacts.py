#!/usr/bin/env python3
"""Collect trained model files, classes, and reports into a deployment folder."""

import argparse
import json
import shutil
from pathlib import Path


def copy_if_exists(src, dst):
    src = Path(src)
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(src), str(dst))
        return True
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--out", default="artifacts/vision_10sku")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    out = Path(args.out)
    manifest = Path(args.manifest)
    out.mkdir(parents=True, exist_ok=True)

    copied = []
    for rel in ["weights/best.pt", "weights/last.pt", "results.csv", "confusion_matrix.png"]:
        if copy_if_exists(run_dir / rel, out / rel):
            copied.append(rel)
    if manifest.exists():
        copy_if_exists(manifest, out / "product_manifest.csv")

    summary = {
        "ok": bool(copied),
        "run_dir": str(run_dir),
        "out": str(out),
        "copied": copied,
        "note": "RKNN conversion/install is a separate verified gate.",
    }
    (out / "artifact_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if copied else 2


if __name__ == "__main__":
    raise SystemExit(main())
