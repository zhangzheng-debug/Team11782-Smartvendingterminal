#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pydeps", default="/userdata/smart_retail/pydeps/onnxruntime_v260")
    args = parser.parse_args()
    pydeps = Path(args.pydeps)
    sys.path.insert(0, str(pydeps))

    result = {
        "ok": False,
        "pydeps": str(pydeps),
        "pydeps_exists": pydeps.exists(),
        "python": sys.version,
        "sys_path0": sys.path[0],
    }
    try:
        import numpy as np
        import onnxruntime as ort
        result.update({
            "ok": True,
            "numpy_version": np.__version__,
            "onnxruntime_version": ort.__version__,
            "providers": ort.get_available_providers(),
            "device": ort.get_device(),
        })
    except Exception as exc:
        result.update({
            "ok": False,
            "error_type": type(exc).__name__,
            "error": str(exc),
        })
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("ONNXRUNTIME_IMPORT_OK=%s" % result["ok"])
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
