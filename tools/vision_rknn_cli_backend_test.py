#!/usr/bin/env python3
import argparse
import json
import sys
import urllib.request


def get_json(url, timeout=8):
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def post_json(url, payload, timeout=12):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://127.0.0.1:5000")
    parser.add_argument("--image", default="/userdata/smart_retail/static/product_images/SKU001.jpg")
    parser.add_argument("--expected", default="SKU001")
    args = parser.parse_args()

    checks = []
    status_code, status = get_json(args.base + "/api/vision/status")
    checks.append(("status_http_200", status_code == 200, status_code))
    checks.append(("backend_rknn_cli", status.get("backend") == "rknn_cli", status.get("backend")))
    checks.append(("active_backend_rknn_cli", status.get("active_backend") == "rknn_cli", status.get("active_backend")))
    checks.append(("rknn_model_available", status.get("rknn_model_available") is True, status.get("rknn_model_available")))
    checks.append(("rknn_cli_available", status.get("rknn_cli_available") is True, status.get("rknn_cli_available")))

    pred_code, pred = post_json(args.base + "/api/vision/predict", {"image_path": args.image})
    top1 = pred.get("top1") or {}
    checks.append(("predict_http_200", pred_code == 200, pred_code))
    checks.append(("predict_ok", pred.get("ok") is True, pred.get("ok")))
    checks.append(("predict_backend_rknn_cli", pred.get("backend") == "rknn_cli", pred.get("backend")))
    checks.append(("top1_expected", top1.get("product_id") == args.expected, top1))
    checks.append(("source_rknn_cli", top1.get("source") == "rknn_cli", top1.get("source")))
    checks.append(("no_auto_add_cart", pred.get("auto_add_cart") is False, pred.get("auto_add_cart")))

    ok = all(item[1] for item in checks)
    result = {
        "ok": ok,
        "checks": [{"name": name, "ok": passed, "value": value} for name, passed, value in checks],
        "status_backend": status.get("backend"),
        "top1": top1,
        "latency_ms": pred.get("latency_ms"),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("VISION_RKNN_CLI_BACKEND_TEST_OK=%s" % ok)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
