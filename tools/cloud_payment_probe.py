#!/usr/bin/env python3
import argparse
import json
import urllib.error
import urllib.request


def req(method, url, body=None, timeout=8):
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as r:
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
    parser.add_argument("--create-test-order", action="store_true")
    args = parser.parse_args()
    checks = []
    status, data = req("GET", args.base.rstrip("/") + "/api/cloud/status")
    checks.append({"name": "cloud status", "pass": status == 200 and data.get("ok") is True, "status": status, "data": data})
    if args.create_test_order:
        status, data = req("POST", args.base.rstrip("/") + "/api/cloud/test_order", {})
        checks.append({"name": "cloud test order", "pass": status == 200 and data.get("ok") is True, "status": status, "data": data})
    passed = sum(1 for c in checks if c["pass"])
    report = {"ok": passed == len(checks), "checks": checks, "passed": passed, "total": len(checks)}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
