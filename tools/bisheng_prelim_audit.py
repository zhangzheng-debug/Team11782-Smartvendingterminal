#!/usr/bin/env python3
"""Offline structure and claim audit for the Bisheng Cup preliminary package.

This script deliberately does not access the board, database, camera, network,
cloud payment service, or display. It checks only files and the frozen dataset
metadata so a materials audit cannot change the demo state.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def check(root: Path, relative: str, required: bool = True) -> dict:
    path = root / relative
    return {"path": relative, "exists": path.exists(), "required": required}


def check_any(root: Path, relatives: list[str], label: str) -> dict:
    present = [item for item in relatives if (root / item).exists()]
    return {"path": label, "alternatives": relatives, "exists": bool(present), "present": present, "required": True}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--json-out")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    required_files = [
        "README.md",
        "app.py",
        "qt_kiosk/Main.qml",
        "V263_LIMITATIONS_HONEST_LIST.md",
        "tools/scan_api_matrix_test.py",
        "tools/qml_business_api_test.py",
        "tools/rknn_cli_smoke_test.py",
        "docs/competition/BISHENG_CUP_DESIGN_REPORT_DRAFT.md",
        "docs/competition/BISHENG_CUP_REQUIREMENTS_EVIDENCE_MATRIX.md",
        "docs/competition/BISHENG_CUP_PRELIMINARY_DEMO_SCRIPT.md",
        "docs/competition/BISHENG_CUP_MATERIALS_GAP_LIST.md",
    ]
    checks = [check(root, item) for item in required_files]
    checks.extend([
        check_any(root, ["dataset_raw_v260/manifest.csv", "data/10sku_manifest/manifest.csv"], "10-SKU manifest"),
        check_any(root, ["TRAINING_REPORT_V260_YOLOV8N_CLS.md", "data/10sku_manifest/intake_report.md"], "dataset report"),
        check_any(root, ["EVALUATION_REPORT_V260.md", "model_artifacts/rknn/eval_fp/summary.json"], "model evaluation summary"),
    ])

    manifest = next((root / item for item in ("dataset_raw_v260/manifest.csv", "data/10sku_manifest/manifest.csv") if (root / item).exists()), None)
    rows = []
    if manifest is not None:
        with manifest.open(newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.DictReader(handle))
    ids = [row.get("product_id", "") for row in rows]
    barcodes = [row.get("barcode", "") for row in rows]
    dataset = {
        "row_count": len(rows),
        "unique_product_ids": len(set(ids)),
        "unique_barcodes": len(set(barcodes)),
        "total_declared_images": sum(int(row.get("image_count", 0) or 0) for row in rows),
        "ten_sku_manifest": len(rows) == 10 and len(set(ids)) == 10 and len(set(barcodes)) == 10,
    }

    app_text = (root / "app.py").read_text(encoding="utf-8", errors="replace") if (root / "app.py").exists() else ""
    report_paths = [
        root / name for name in ("TRAINING_REPORT_V260_YOLOV8N_CLS.md", "EVALUATION_REPORT_V260.md", "data/10sku_manifest/intake_report.md", "docs/competition/BISHENG_CUP_DESIGN_REPORT_DRAFT.md")
        if (root / name).exists()
    ]
    report_text = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in report_paths)
    claims = {
        "vision_auto_add_disabled": "VISION_AUTO_ADD_CART = False" in app_text,
        "small_test_set_disclosed": "18" in report_text and "94.44" in report_text and ("100.00" in report_text or "100%" in report_text),
        "payment_boundary_disclosed": "仿真云支付" in (root / "docs/competition/BISHENG_CUP_DESIGN_REPORT_DRAFT.md").read_text(encoding="utf-8") if (root / "docs/competition/BISHENG_CUP_DESIGN_REPORT_DRAFT.md").exists() else False,
    }

    pending = [
        "赛区统一报告模板与报名页面核对",
        "本次现场 HDMI/外设/支付照片或视频",
        "BOM 与成本估算",
        "干净环境 smoke test",
        "最终提交包 secrets/个人信息/旧地址扫描",
    ]
    result = {
        "audit": "bisheng_cup_preliminary",
        "mode": "offline_files_only",
        "root": str(root),
        "required_files_pass": all(item["exists"] for item in checks),
        "required_files": checks,
        "dataset": dataset,
        "claim_guards": claims,
        "pending_field_evidence": pending,
        "decision": "READY_WITH_PENDING_FIELD_EVIDENCE" if all(item["exists"] for item in checks) and dataset["ten_sku_manifest"] and all(claims.values()) else "NEEDS_REVIEW",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.json_out:
        output = Path(args.json_out)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if result["decision"] == "READY_WITH_PENDING_FIELD_EVIDENCE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
