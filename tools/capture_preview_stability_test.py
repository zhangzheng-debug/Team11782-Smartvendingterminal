#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2.6.6 capture preview metadata stability gate."""

import json
import sys
import time
import urllib.request

BASE = "http://127.0.0.1:5000"


def req(method, path, payload=None, timeout=20):
    data = json.dumps(payload or {}).encode("utf-8") if method == "POST" else None
    request = urllib.request.Request(BASE + path, data=data, headers={"Content-Type": "application/json"}, method=method)
    with urllib.request.urlopen(request, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", "replace"))


def main():
    req("POST", "/api/system/reset_busy_flags")
    captures = []
    for i in range(5):
        r = req("POST", "/api/capture", {}, timeout=25)
        captures.append({
            "idx": i + 1,
            "ok": r.get("ok"),
            "status": r.get("capture_status") or r.get("status"),
            "capture_id": r.get("capture_id"),
            "image_path": r.get("image_path"),
            "thumb_path": r.get("thumb_path"),
            "message": r.get("message"),
        })
        time.sleep(2.0)
    s = req("GET", "/api/state")
    ok_success = any(c.get("ok") for c in captures)
    ok_thumb = bool(s.get("latest_capture_thumb_url") and s.get("latest_capture_id"))
    ok_fields = s.get("latest_capture_status") in {"idle", "success", "cooldown"}
    result = {
        "ok": ok_success and ok_thumb and ok_fields,
        "captures": captures,
        "latest_capture_id": s.get("latest_capture_id"),
        "latest_capture_thumb_url": s.get("latest_capture_thumb_url"),
        "latest_capture_status": s.get("latest_capture_status"),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
