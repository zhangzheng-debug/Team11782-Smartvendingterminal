#!/usr/bin/env python3
import importlib.util
import json
import os
from pathlib import Path


def probe_module(name):
    try:
        spec = importlib.util.find_spec(name)
        return {"name": name, "found": spec is not None, "origin": spec.origin if spec else ""}
    except Exception as exc:
        return {"name": name, "found": False, "error_type": type(exc).__name__, "error": str(exc)}


def main():
    result = {
        "ok": False,
        "modules": [probe_module(x) for x in ["rknnlite", "rknnlite.api", "rknn", "rknn.api"]],
        "runtime_files": {},
        "device_nodes": [],
    }
    for path in ["/usr/lib/librknnrt.so", "/usr/lib/librknn_api.so", "/usr/bin/rknn_server"]:
        p = Path(path)
        result["runtime_files"][path] = {"exists": p.exists(), "size": p.stat().st_size if p.exists() else 0}
    for pattern in ["/dev/rknpu0", "/dev/dri/renderD129", "/dev/dri/card1"]:
        if Path(pattern).exists():
            result["device_nodes"].append(pattern)
    result["ok"] = any(m["found"] for m in result["modules"])
    result["c_runtime_available"] = result["runtime_files"]["/usr/lib/librknnrt.so"]["exists"]
    result["npu_device_available"] = bool(result["device_nodes"])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("RKNN_PYTHON_IMPORT_OK=%s" % result["ok"])
    print("RKNN_C_RUNTIME_AVAILABLE=%s" % result["c_runtime_available"])
    print("RKNN_NPU_DEVICE_AVAILABLE=%s" % result["npu_device_available"])
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

