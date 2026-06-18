#!/usr/bin/env python3
import argparse
import json
import math
import sys
import time
from pathlib import Path


def softmax(values):
    vals = [float(v) for v in values]
    m = max(vals) if vals else 0.0
    exps = [math.exp(v - m) for v in vals]
    s = sum(exps) or 1.0
    return [v / s for v in exps]


def load_labels(path):
    return [line.strip() for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def resolve_image(args):
    if args.image:
        p = Path(args.image)
        if p.exists():
            return p
    for pattern in [
        "dataset_raw_v260/SKU001/images/*.jpg",
        "static/captures/*.jpg",
    ]:
        matches = sorted(Path(".").glob(pattern))
        if matches:
            return matches[0]
    raise FileNotFoundError("No test image found")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pydeps", default="/userdata/smart_retail/pydeps/onnxruntime_v260")
    parser.add_argument("--model", default="models/vision_10sku_v260/model.onnx")
    parser.add_argument("--labels", default="models/vision_10sku_v260/labels.txt")
    parser.add_argument("--image", default="")
    parser.add_argument("--imgsz", type=int, default=224)
    args = parser.parse_args()

    sys.path.insert(0, args.pydeps)
    start = time.time()
    result = {
        "ok": False,
        "pydeps": args.pydeps,
        "model": args.model,
        "labels": args.labels,
    }
    try:
        import numpy as np
        import onnxruntime as ort
        from PIL import Image

        image_path = resolve_image(args)
        labels = load_labels(args.labels)
        sess = ort.InferenceSession(args.model, providers=["CPUExecutionProvider"])
        input_name = sess.get_inputs()[0].name
        with Image.open(image_path) as im:
            im = im.convert("RGB").resize((args.imgsz, args.imgsz))
            arr = np.asarray(im).astype("float32") / 255.0
        arr = arr.transpose(2, 0, 1)[None, ...]
        output = sess.run(None, {input_name: arr})[0][0]
        probs = softmax(output)
        top = sorted(range(len(probs)), key=lambda i: probs[i], reverse=True)[:3]
        top3 = []
        for rank, idx in enumerate(top, start=1):
            top3.append({
                "rank": rank,
                "class_index": int(idx),
                "label": labels[idx] if idx < len(labels) else str(idx),
                "confidence": round(float(probs[idx]), 4),
            })
        result.update({
            "ok": True,
            "image": str(image_path),
            "providers": sess.get_providers(),
            "top1": top3[0] if top3 else {},
            "top3": top3,
            "latency_ms": int((time.time() - start) * 1000),
        })
    except Exception as exc:
        result.update({
            "ok": False,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "latency_ms": int((time.time() - start) * 1000),
        })
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("VISION_ONNX_INFERENCE_OK=%s" % result["ok"])
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
