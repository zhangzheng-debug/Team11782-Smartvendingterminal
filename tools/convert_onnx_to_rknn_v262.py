#!/usr/bin/env python3
"""Convert the V2.6 10-SKU ONNX model to RKNN.

This script is intended for a Linux x86_64 Python 3.8 environment with
Rockchip RKNN-Toolkit2 installed in an isolated venv. It is not meant to run
on the board.
"""

import argparse
import json
import sys
from pathlib import Path


def collect_images(dataset_dir, limit_per_sku=8):
    images = []
    for sku_dir in sorted(Path(dataset_dir).glob("SKU*/images")):
        for img in sorted(sku_dir.glob("*"))[:limit_per_sku]:
            if img.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}:
                images.append(img)
    return images


def write_calibration_dataset(images, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(str(p.resolve()) for p in images) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--onnx", default="MODEL_ARTIFACTS_V260/model.onnx")
    parser.add_argument("--labels", default="MODEL_ARTIFACTS_V260/labels.txt")
    parser.add_argument("--class-map", default="MODEL_ARTIFACTS_V260/class_map.json")
    parser.add_argument("--dataset", default="dataset_raw_v260")
    parser.add_argument("--outdir", default="MODEL_ARTIFACTS_V262_RKNN")
    parser.add_argument("--target-platform", default="rk3568")
    parser.add_argument("--imgsz", type=int, default=224)
    parser.add_argument("--no-quant", action="store_true")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    calibration = outdir / "calibration_dataset.txt"
    images = collect_images(args.dataset)
    write_calibration_dataset(images, calibration)

    result = {
        "ok": False,
        "onnx": args.onnx,
        "target_platform": args.target_platform,
        "outdir": str(outdir),
        "calibration_dataset": str(calibration),
        "calibration_image_count": len(images),
    }

    try:
        from rknn.api import RKNN
    except Exception as exc:
        result.update({
            "error_reason": "rknn_toolkit2_missing",
            "error": str(exc),
            "python": sys.version,
        })
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2

    Path(args.labels).replace(outdir / "labels.txt") if False else None
    if Path(args.labels).exists():
        (outdir / "labels.txt").write_text(Path(args.labels).read_text(encoding="utf-8"), encoding="utf-8")
    if Path(args.class_map).exists():
        (outdir / "class_map.json").write_text(Path(args.class_map).read_text(encoding="utf-8"), encoding="utf-8")

    variants = [("fp", False)]
    if not args.no_quant:
        variants.append(("i8", True))

    exports = []
    for suffix, quantize in variants:
        model_name = outdir / f"vision_10sku_v262_{suffix}.rknn"
        rknn = RKNN(verbose=True)
        try:
            rknn.config(
                target_platform=args.target_platform,
                mean_values=[[0, 0, 0]],
                std_values=[[255, 255, 255]],
            )
            ret = rknn.load_onnx(model=args.onnx)
            if ret != 0:
                raise RuntimeError(f"load_onnx failed: {ret}")
            dataset_arg = str(calibration) if quantize else None
            ret = rknn.build(do_quantization=quantize, dataset=dataset_arg)
            if ret != 0:
                raise RuntimeError(f"build failed: {ret}")
            ret = rknn.export_rknn(str(model_name))
            if ret != 0:
                raise RuntimeError(f"export_rknn failed: {ret}")
            exports.append({"variant": suffix, "path": str(model_name), "quantized": quantize, "ok": True})
        except Exception as exc:
            exports.append({"variant": suffix, "path": str(model_name), "quantized": quantize, "ok": False, "error": str(exc)})
        finally:
            rknn.release()

    metadata = {
        "model_version": "v262_rknn_10sku_baseline",
        "source_onnx": args.onnx,
        "target_platform": args.target_platform,
        "input_size": [1, args.imgsz, args.imgsz, 3],
        "label_order_locked": True,
        "exports": exports,
    }
    (outdir / "model_metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    result.update({"ok": any(x["ok"] for x in exports), "exports": exports})
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

