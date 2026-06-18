#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys
import urllib.request

BASE = "http://127.0.0.1:5000"


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=10) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8", "replace") or "{}")


def main():
    status, data = get("/api/vision/status")
    checks = [
        ("http_200", status == 200),
        ("ok_true", data.get("ok") is True),
        ("has_backend", "backend" in data),
        ("has_model_available", "model_available" in data),
        ("class_count_reported", int(data.get("class_count", 0) or 0) >= 0),
        ("policy_safe", data.get("auto_add_cart") is False),
    ]
    result = {"ok": all(v for _, v in checks), "checks": [{"name": k, "pass": v} for k, v in checks], "status": data}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("VISION_MODEL_STATUS_CHECKS=%d PASS=%d FAIL=%d" % (len(checks), sum(1 for _, v in checks if v), sum(1 for _, v in checks if not v)))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

