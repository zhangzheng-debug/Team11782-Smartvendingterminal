#!/usr/bin/env python3
"""Compare V2.6.3 RKNN outputs against ONNX Runtime outputs.

Run in the Linux x86_64 Python 3.8 RKNN-Toolkit2 conversion environment.
"""

import argparse
import csv
import json
import math
from pathlib import Path


def softmax(values):
    vals = [float(v) for v in values]
    m = max(vals) if vals else 0.0
    exps = [math.exp(v - m) for v in vals]
    s = sum(exps) or 1.0
    return [v / s for v in exps]


def collect_images(dataset_dir):
    images = []
    for sku_dir in sorted(Path(dataset_dir).glob("SKU*/images")):
        sku = sku_dir.parent.name
        for img in sorted(sku_dir.glob("*")):
            if img.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}:
                images.append((sku, img))
    return images


def topk(probs, labels, k=3):
    idxs = sorted(range(len(probs)), key=lambda i: probs[i], reverse=True)[:k]
    return [{"idx": int(i), "label": labels[i] if i < len(labels) else str(i), "confidence": float(probs[i])} for i in idxs]


def load_labels(path):
    return [line.strip() for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--onnx", default="MODEL_ARTIFACTS_V260/model.onnx")
    parser.add_argument("--rknn", default="MODEL_ARTIFACTS_V263_RKNN/vision_10sku_v263_default.rknn")
    parser.add_argument("--variant", choices=["fp", "i8"], default="fp")
    parser.add_argument("--calibration", default="MODEL_ARTIFACTS_V263_RKNN/calibration_dataset.txt")
    parser.add_argument("--labels", default="MODEL_ARTIFACTS_V263_RKNN/labels.txt")
    parser.add_argument("--dataset", default="dataset_raw_v260")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--outdir", default="MODEL_ARTIFACTS_V263_RKNN/eval_default")
    args = parser.parse_args()

    import numpy as np
    import onnxruntime as ort
    from PIL import Image
    from rknn.api import RKNN

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    mismatch_dir = outdir / "mismatch_samples"
    mismatch_dir.mkdir(parents=True, exist_ok=True)

    labels = load_labels(args.labels)
    images = collect_images(args.dataset)
    if args.limit:
        images = images[: args.limit]

    ort_sess = ort.InferenceSession(args.onnx, providers=["CPUExecutionProvider"])
    ort_input = ort_sess.get_inputs()[0].name
    rknn = RKNN(verbose=False)
    rknn.config(target_platform="rk3568", mean_values=[[0, 0, 0]], std_values=[[255, 255, 255]])
    ret = rknn.load_onnx(model=args.onnx)
    if ret != 0:
        raise SystemExit(f"load_onnx failed: {ret}")
    ret = rknn.build(do_quantization=args.variant == "i8", dataset=args.calibration if args.variant == "i8" else None)
    if ret != 0:
        raise SystemExit(f"build failed: {ret}")
    ret = rknn.init_runtime()
    if ret != 0:
        raise SystemExit(f"init_runtime failed: {ret}")

    rows = []
    top1_agree = 0
    top3_contains = 0
    for expected_sku, img_path in images:
        with Image.open(img_path) as im:
            rgb = im.convert("RGB").resize((224, 224))
            hwc_u8 = np.asarray(rgb).astype("uint8")
            nchw_f32 = hwc_u8.astype("float32").transpose(2, 0, 1)[None, ...] / 255.0
        onnx_out = ort_sess.run(None, {ort_input: nchw_f32})[0][0]
        onnx_probs = softmax(onnx_out)
        # RKNN config performs /255 internally, so pass RGB uint8 HWC.
        rknn_out = rknn.inference(inputs=[hwc_u8])[0][0]
        rknn_probs = softmax(rknn_out)
        onnx_top3 = topk(onnx_probs, labels, 3)
        rknn_top3 = topk(rknn_probs, labels, 3)
        onnx_top1 = onnx_top3[0]["label"].split("_", 1)[0]
        rknn_top1 = rknn_top3[0]["label"].split("_", 1)[0]
        agree = onnx_top1 == rknn_top1
        contains = onnx_top1 in [x["label"].split("_", 1)[0] for x in rknn_top3]
        top1_agree += 1 if agree else 0
        top3_contains += 1 if contains else 0
        rows.append({
            "image": str(img_path),
            "expected_sku": expected_sku,
            "onnx_top1": onnx_top1,
            "rknn_top1": rknn_top1,
            "top1_agree": agree,
            "onnx_top3": json.dumps(onnx_top3, ensure_ascii=False),
            "rknn_top3": json.dumps(rknn_top3, ensure_ascii=False),
        })
        if not agree:
            try:
                import shutil
                shutil.copy2(img_path, mismatch_dir / img_path.name)
            except Exception:
                pass

    rknn.release()
    total = len(rows) or 1
    summary = {
        "ok": True,
        "onnx": args.onnx,
        "rknn": args.rknn,
        "variant": args.variant,
        "evaluation_mode": "load_onnx_build_then_simulator_inference",
        "image_count": len(rows),
        "top1_agreement": top1_agree,
        "top1_agreement_rate": top1_agree / total,
        "top3_contains_onnx_top1": top3_contains,
        "top3_contains_onnx_top1_rate": top3_contains / total,
        "mismatch_count": len(rows) - top1_agree,
    }
    with (outdir / "rknn_vs_onnx_predictions.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["image"])
        writer.writeheader()
        writer.writerows(rows)
    (outdir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
