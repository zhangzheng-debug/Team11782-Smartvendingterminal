#!/usr/bin/env python3
"""V2.6.3 ONNX to RKNN converter for the 10-SKU classifier.

Run only in an isolated Linux x86_64 Python 3.8 environment with
RKNN-Toolkit2 installed. Do not run on the board.
"""

import argparse
import json
import shutil
import sys
from pathlib import Path


def collect_images(dataset_dir, limit_per_sku=8):
    images = []
    for sku_dir in sorted(Path(dataset_dir).glob("SKU*/images")):
        for img in sorted(sku_dir.glob("*")):
            if img.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}:
                images.append(img)
                if len([x for x in images if x.parent == sku_dir]) >= limit_per_sku:
                    break
    return images


def write_calibration_dataset(images, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(str(p.resolve()) for p in images) + "\n", encoding="utf-8")


def copy_if_exists(src, dst):
    if Path(src).exists():
        shutil.copy2(src, dst)


def build_variant(RKNN, args, outdir, calibration, suffix, quantize):
    model_path = outdir / f"vision_10sku_v263_{suffix}.rknn"
    log = {"variant": suffix, "path": str(model_path), "quantized": quantize, "ok": False}
    rknn = RKNN(verbose=True)
    try:
        # The ONNX model already includes /255 preprocessing in the app-side path.
        # Keep RKNN preprocessing equivalent: RGB, resize 224, float input normalized by 255.
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
        ret = rknn.export_rknn(str(model_path))
        if ret != 0:
            raise RuntimeError(f"export_rknn failed: {ret}")
        log["ok"] = True
    except Exception as exc:
        log["error"] = str(exc)
    finally:
        rknn.release()
    return log


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--onnx", default="MODEL_ARTIFACTS_V260/model.onnx")
    parser.add_argument("--labels", default="MODEL_ARTIFACTS_V260/labels.txt")
    parser.add_argument("--class-map", default="MODEL_ARTIFACTS_V260/class_map.json")
    parser.add_argument("--source-metadata", default="MODEL_ARTIFACTS_V260/model_metadata.json")
    parser.add_argument("--dataset", default="dataset_raw_v260")
    parser.add_argument("--outdir", default="MODEL_ARTIFACTS_V263_RKNN")
    parser.add_argument("--target-platform", default="rk3568")
    parser.add_argument("--limit-per-sku", type=int, default=8)
    parser.add_argument("--fp-only", action="store_true")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    calibration = outdir / "calibration_dataset.txt"
    images = collect_images(args.dataset, args.limit_per_sku)
    write_calibration_dataset(images, calibration)

    copy_if_exists(args.labels, outdir / "labels.txt")
    copy_if_exists(args.class_map, outdir / "class_map.json")

    result = {
        "ok": False,
        "python": sys.version,
        "onnx": args.onnx,
        "target_platform": args.target_platform,
        "outdir": str(outdir),
        "calibration_dataset": str(calibration),
        "calibration_image_count": len(images),
        "preprocess": {
            "color": "RGB",
            "resize": [224, 224],
            "input_layout": "NCHW in ONNX",
            "normalization": "divide_by_255",
            "rknn_mean_values": [[0, 0, 0]],
            "rknn_std_values": [[255, 255, 255]],
        },
    }

    try:
        from rknn.api import RKNN
    except Exception as exc:
        result.update({"error_reason": "rknn_toolkit2_missing", "error": str(exc)})
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2

    variants = [("fp", False)]
    if not args.fp_only:
        variants.append(("i8", True))

    exports = [build_variant(RKNN, args, outdir, calibration, suffix, quantize) for suffix, quantize in variants]
    default = next((x["path"] for x in exports if x["ok"] and x["variant"] == "fp"), None)
    if default is None:
        default = next((x["path"] for x in exports if x["ok"]), None)
    if default:
        shutil.copy2(default, outdir / "vision_10sku_v263_default.rknn")

    metadata = {
        "model_version": "v263_rknn_10sku_baseline",
        "source_onnx": args.onnx,
        "source_metadata": args.source_metadata,
        "target_platform": args.target_platform,
        "label_order_locked": True,
        "labels": Path(args.labels).read_text(encoding="utf-8").splitlines() if Path(args.labels).exists() else [],
        "default_model": str(outdir / "vision_10sku_v263_default.rknn") if default else "",
        "exports": exports,
        "preprocess": result["preprocess"],
    }
    (outdir / "model_metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    result.update({"ok": any(x["ok"] for x in exports), "exports": exports, "default_model": metadata["default_model"]})
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

