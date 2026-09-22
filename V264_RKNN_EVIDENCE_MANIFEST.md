# V2.6.4 RKNN Evidence Manifest

Automated evidence already collected:

- `active_backend=rknn_cli` from `/api/vision/status`.
- `RKNN_CLI_SMOKE_OK=True`.
- `VISION_RKNN_CLI_BACKEND_TEST_OK=True`.
- `V260_SCAN_10SKU_CHECKS=43 PASS=43 FAIL=0`.
- `SCAN_API_MATRIX_CHECKS=39 PASS=39 FAIL=0`.
- `VISION_MODEL_STATUS_CHECKS=6 PASS=6 FAIL=0`.
- `VISION_NO_REPEAT_ADD_CHECKS=3 PASS=3 FAIL=0`.
- `RKNN_CLI_SMOKE_OK=True` after final rehearsal.

Files to cite:

- `V263_RKNN_CLI_SMOKE_TEST_REPORT.md`
- `V263_FLASK_RKNN_CLI_BACKEND_REPORT.md`
- `V263_RKNN_NPU_PERFORMANCE_REPORT.md`
- `V263_FINAL_TEST_RESULTS.md`
- `V263_LIMITATIONS_HONEST_LIST.md`
- `V264_RKNN_FIELD_DEMO_EVIDENCE_REPORT.md`

Physical photos/videos to capture:

1. `evidence_v264_01_hdmi_qml_home.jpg`
   - HDMI screen with QML cashier visible.

2. `evidence_v264_02_rknn_status.jpg`
   - UI or terminal showing `active_backend=rknn_cli`.

3. `evidence_v264_03_rknn_top3.jpg`
   - Top-3 visual candidates, confidence, and latency.

4. `evidence_v264_04_scan_no_repeat.jpg`
   - Scan adds one cart item; visual verify does not add again.

5. `evidence_v264_05_unknown_candidate.jpg`
   - Unknown barcode shows candidate workflow, not silent failure.

6. `evidence_v264_06_cloud_paid.jpg`
   - Cloud payment paid writeback visible.

7. `evidence_v264_07_voice_broadcast.mp4`
   - Operation voice prompt audible through HyperX.

8. `evidence_v264_08_hardware_ports.jpg`
   - Scanner, HyperX, camera, HDMI, and Ethernet/ADB port layout.

Short proof statement:

```text
Custom 10-SKU classifier -> ONNX -> RKNN -> RK3568 NPU C runtime CLI -> Flask /api/vision -> QML cashier.
Barcode is the stable payment input; RKNN vision provides on-device verification and unknown-barcode candidate support.
```
