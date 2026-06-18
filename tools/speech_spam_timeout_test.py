#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2.6.5 speech one-job/busy gate."""

import argparse
import json
import queue
import sys
import threading
import time
import urllib.request


def req(method, url, body=None, timeout=30):
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", "replace"))


def worker(base, outq, label):
    try:
        outq.put((label, req("POST", base + "/api/speech/auto_once", {"seconds": 1, "execute": "0"}, timeout=28)))
    except Exception as exc:
        outq.put((label, {"ok": False, "exception": str(exc)}))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:5000")
    args = ap.parse_args()
    base = args.base.rstrip("/")

    try:
        req("POST", base + "/api/speech/reset", {}, timeout=5)
    except Exception:
        pass

    outq = queue.Queue()
    t1 = threading.Thread(target=worker, args=(base, outq, "first"))
    t2 = threading.Thread(target=worker, args=(base, outq, "second"))
    start = time.time()
    t1.start()
    time.sleep(0.15)
    t2.start()
    t1.join(35)
    t2.join(35)
    elapsed = time.time() - start
    results = []
    while not outq.empty():
        results.append(outq.get())
    state = req("GET", base + "/api/state", timeout=8)

    busy_seen = any((r.get("stage") == "busy" or r.get("error") == "speech_busy") for _, r in results)
    no_hang = elapsed < 35 and len(results) == 2
    ok = no_hang and (busy_seen or any(r.get("ok") for _, r in results))
    print(json.dumps({
        "ok": ok,
        "elapsed_sec": round(elapsed, 2),
        "busy_seen": busy_seen,
        "latest_speech_status": state.get("latest_speech_status"),
        "results": results,
    }, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
