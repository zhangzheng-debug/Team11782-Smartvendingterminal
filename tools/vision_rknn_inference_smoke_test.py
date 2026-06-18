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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="models/vision_10sku_rknn_v262/vision_10sku_v262_default.rknn")
    parser.add_argument("--labels", default="models/vision_10sku_rknn_v262/labels.txt")
    parser.add_argument("--image", default="static/product_images/SKU001.jpg")
    parser.add_argument("--imgsz", type=int, default=224)
    args = parser.parse_args()

    start = time.time()
    result = {"ok": False, "model": args.model, "labels": args.labels, "image": args.image}
    try:
        import numpy as np
        from PIL import Image
        from rknnlite.api import RKNNLite
    except Exception as exc:
        result.update({"error_reason": "rknnlite_python_missing", "error_type": type(exc).__name__, "error": str(exc)})
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("VISION_RKNN_INFERENCE_OK=False")
        return 2

    try:
        labels = load_labels(args.labels)
        with Image.open(args.image) as im:
            im = im.convert("RGB").resize((args.imgsz, args.imgsz))
            arr = np.asarray(im).astype("float32") / 255.0
        arr = arr[None, ...]
        rknn = RKNNLite()
        ret = rknn.load_rknn(args.model)
        if ret != 0:
            raise RuntimeError(f"load_rknn failed: {ret}")
        ret = rknn.init_runtime()
        if ret != 0:
            raise RuntimeError(f"init_runtime failed: {ret}")
        outputs = rknn.inference(inputs=[arr])
        rknn.release()
        output = outputs[0][0]
        probs = softmax(output)
        top = sorted(range(len(probs)), key=lambda i: probs[i], reverse=True)[:3]
        top3 = [{"rank": rank, "class_index": int(idx), "label": labels[idx] if idx < len(labels) else str(idx), "confidence": round(float(probs[idx]), 4)} for rank, idx in enumerate(top, 1)]
        result.update({"ok": True, "top1": top3[0] if top3 else {}, "top3": top3, "latency_ms": int((time.time() - start) * 1000)})
    except Exception as exc:
        result.update({"ok": False, "error_type": type(exc).__name__, "error": str(exc), "latency_ms": int((time.time() - start) * 1000)})
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("VISION_RKNN_INFERENCE_OK=%s" % result["ok"])
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

