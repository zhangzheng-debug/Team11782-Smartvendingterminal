#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys
import urllib.request

BASE = "http://127.0.0.1:5000"


def post(path, payload):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8", "replace") or "{}")


def main():
    status, data = post("/api/vision/predict", {})
    checks = [
        ("http_200", status == 200),
        ("has_result", bool(data.get("result"))),
        ("safe_no_auto_add", data.get("auto_add_cart") is False),
        ("candidates_field", isinstance(data.get("candidates"), list)),
    ]
    result = {"ok": all(v for _, v in checks), "checks": [{"name": k, "pass": v} for k, v in checks], "response": data}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

