# V2.6.4 RKNN Field Demo Evidence Report

Status: TECHNICAL PASS

Scope:
- No new features were added.
- No boot/rootfs/oem/uboot writes were performed.
- No RKDevTool, Upgrade, EraseFlash, autostart, database overwrite, or cloud server change was performed.

Current runtime:
- Flask: running on board.
- Weston HDMI-primary: running.
- QML cashier: running.
- Vision backend: `rknn_cli`.
- ONNX Runtime: retained as fallback.

RKNN evidence:
- `/api/vision/status` reports `active_backend=rknn_cli`.
- `tools/rknn_cli_smoke_test.py`: PASS.
- `tools/vision_rknn_cli_backend_test.py`: PASS.
- RKNN direct CLI SKU001 result: top1 `SKU001`, confidence about `0.997559`, latency observed `18-24 ms`.
- Flask RKNN backend SKU001 result: top1 `SKU001`, `source=rknn_cli`, confidence about `0.9976`, latency observed about `24 ms`.

Business safety evidence:
- Barcode scanner remains the add-to-cart authority.
- `VISION_AUTO_ADD_CART=false`.
- `vision_no_repeat_add_test.py`: PASS, scan adds once, verify/candidates do not add again.
- Vision verification may return low confidence on live capture images; this is expected and handled honestly as verification/candidate information, not automatic billing.

Final regression evidence:
- `scan_v260_10sku_test.py`: 43/43 PASS.
- `scan_api_matrix_test.py`: 39/39 PASS.
- `qml_business_api_test.py`: PASS.
- `input_arbitration_api_test.py`: PASS.
- `capture_stress_test.py`: PASS.
- `audio_event_matrix_test.py`: PASS.
- `vision_model_status_test.py`: 6/6 PASS.
- `vision_predict_smoke_test.py`: PASS.
- `vision_scan_verify_test.py`: PASS.
- `vision_no_repeat_add_test.py`: 3/3 PASS.
- `rknn_cli_smoke_test.py`: PASS.

Physical evidence still needs the user to capture with a phone:
- HDMI QML screen showing the cashier.
- RKNN/NPU backend and Top-3 result visible in the UI.
- Scanner, HyperX, camera, HDMI, and network cable port photos.
- Cloud paid writeback demo photo/video.
- Voice broadcast demo video.

Conclusion:
- V2.6.4 technical readiness is PASS.
- Final release freeze can proceed after the user captures the physical evidence photos/videos listed in `V264_RKNN_EVIDENCE_MANIFEST.md`.
