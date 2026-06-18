#!/usr/bin/env python3
import argparse
import json
import urllib.error
import urllib.request


def req(method, url, body=None):
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=10) as r:
            text = r.read().decode("utf-8", "ignore")
            return r.status, json.loads(text or "{}")
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", "ignore")
        try:
            payload = json.loads(text or "{}")
        except Exception:
            payload = {"raw": text}
        return e.code, payload
    except Exception as e:
        return 0, {"ok": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://127.0.0.1:5000")
    args = parser.parse_args()
    base = args.base.rstrip("/")
    checks = []
    cases = [
        ("status", "GET", "/api/vision/status", None),
        ("verify SKU006", "POST", "/api/vision/verify_scan", {"barcode": "SKU006"}),
        ("unknown candidates", "POST", "/api/vision/candidates", {"image_path": "", "limit": 3}),
        ("manual confirm canceled", "POST", "/api/vision/confirm", {"product_id": "SKU006", "confirmed": False}),
    ]
    for name, method, path, body in cases:
        status, data = req(method, base + path, body)
        checks.append({"name": name, "pass": status == 200 and "ok" in data, "status": status, "data": data})
    passed = sum(1 for c in checks if c["pass"])
    report = {"ok": passed == len(checks), "checks": checks, "passed": passed, "total": len(checks)}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
