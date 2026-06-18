#!/usr/bin/env python3
import argparse
import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cli", default="/userdata/smart_retail/bin/vision_rknn_cli_v263/vision_rknn_cli")
    parser.add_argument("--model", default="/userdata/smart_retail/models/vision_10sku_rknn_v263/vision_10sku_v263_default.rknn")
    parser.add_argument("--labels", default="/userdata/smart_retail/models/vision_10sku_rknn_v263/labels.txt")
    parser.add_argument("--image", default="/userdata/smart_retail/static/product_images/SKU001.jpg")
    parser.add_argument("--libdir", default="/userdata/smart_retail/bin/vision_rknn_cli_v263/lib")
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args()

    result = {"ok": False, "cli": args.cli, "model": args.model, "image": args.image}
    try:
        with Image.open(args.image) as im:
            raw = im.convert("RGB").resize((224, 224)).tobytes()
        raw_path = Path(tempfile.gettempdir()) / "vision_rknn_input_v263.rgb"
        raw_path.write_bytes(raw)
        cmd = [args.cli, "--model", args.model, "--input", str(raw_path), "--labels", args.labels, "--topk", "3", "--json"]
        env = {"LD_LIBRARY_PATH": args.libdir}
        proc = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=args.timeout)
        result.update({"returncode": proc.returncode, "stdout": proc.stdout.strip(), "stderr": proc.stderr.strip()[-1200:]})
        parsed = json.loads(proc.stdout.strip().splitlines()[-1])
        result.update({"ok": proc.returncode == 0 and parsed.get("ok") is True, "parsed": parsed})
    except Exception as exc:
        result.update({"ok": False, "error_type": type(exc).__name__, "error": str(exc)})
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("RKNN_CLI_SMOKE_OK=%s" % result["ok"])
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

