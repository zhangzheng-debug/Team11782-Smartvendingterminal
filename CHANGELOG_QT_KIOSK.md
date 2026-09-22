# Qt Kiosk Changelog

## 2026-06-10 V2.6.11-D

- Completed `V2.6.11-D Voice Checkout Opens Payment Dialog Hotfix`.
- Added a unified checkout UI action contract: `ui_action=open_payment_dialog` with full `order` payload.
- Added empty-cart checkout contract: `ui_action=show_error`, `error_reason=cart_empty`.
- Updated `/api/checkout`, numeric voice checkout, and speech checkout response payloads.
- Updated QML `Main.qml` with `openPaymentDialog(order)`, `handleUiAction(data)`, and shared order extraction from `order`, `action_result.order`, or `exec_result.order`.
- Voice checkout now opens the same `PaymentDialog` path as the checkout button.
- Added tests: `tools/voice_checkout_dialog_contract_test.py` and `tools/voice_checkout_empty_cart_test.py`.
- Updated `tools/qml_business_api_test.py` to include a voice checkout dialog contract check.
- Board regression PASS: voice checkout dialog `9/9`, voice empty-cart `5/5`, QML business `45/45`, payment paid UI sync `7/7`, phone-first cloud payment `7/7`, scan API matrix `39/39`, RKNN CLI smoke, and audio event matrix `24/24`.
- No flashing, RKDevTool, Upgrade/EraseFlash, boot/rootfs/oem/uboot write, `/etc/init.d/S03weston` change, autostart change, database overwrite, cloud server change, or RKNN backend change was performed.

## 2026-06-10 V2.6.11-C

- Completed `V2.6.11-C Final UI Prompt Bar + Realistic Demo Pricing Hotfix`.
- Added `qt_kiosk/components/PersistentVoiceHintBar.qml`.
- Inserted a persistent HDMI top voice-command hint below `HeaderBar`, independent of changing speech/status results.
- Added `tools/update_v2611c_demo_prices.py` with `--dry-run`, `--apply`, and automatic DB backup before apply.
- Updated SKU001-SKU010 `products.price_cent` to campus convenience-store demo reference prices.
- Added `tools/v2611c_price_update_test.py`.
- Board DB backup created at `/userdata/smart_retail/database/backups/v2611c_price_update_20260610_112135/retail_terminal.db`.
- Board regression PASS: V2.6.11-C price test `24/24`, cart total consistency, scan API matrix `39/39`, QML business `41/41`, phone-first cloud payment `7/7`, RKNN CLI smoke, audio event matrix `24/24`, and `/api/state` HTTP 200 with `active_backend=rknn_cli`.
- No flashing, RKDevTool, Upgrade/EraseFlash, boot/rootfs/oem/uboot write, `/etc/init.d/S03weston` change, autostart change, historical order rewrite, cloud server change, or checkpoint deletion was performed.

## 2026-06-10 V2.6.11-B

- Completed `V2.6.11-B Payment Paid UI Sync Hotfix`.
- Added `POST /api/order/<order_id>/sync_cloud` to poll cloud payment status for a specific order and update local paid state.
- Added `POST /api/payment/sync_latest` for latest-order payment synchronization.
- Extended order JSON with `last_sync_at`, `last_sync_status`, and user-facing paid/waiting `message`.
- Hardened latest-order selection with `ORDER BY created_at DESC, rowid DESC` to avoid same-second order ambiguity.
- Rebuilt `PaymentDialog.qml` with paid polling, manual refresh, green `支付成功` state, QR de-emphasis, `paidConfirmed(order)` signal, and auto-close after paid.
- Updated `Main.qml` to refresh the cashier screen after dialog paid confirmation.
- Added tests: `tools/payment_paid_ui_sync_test.py` and `tools/payment_dialog_polling_contract_test.py`.
- Board serial regression PASS: payment paid UI sync `7/7`, payment dialog polling contract, phone-first cloud payment, scan API matrix, QML business `41/41`, audio event matrix `24/24`, RKNN CLI smoke, and `/api/state` HTTP 200 with `active_backend=rknn_cli`.
- Created V2.6.11-B reports and release patch decision docs.
- No flashing, RKDevTool, Upgrade/EraseFlash, boot/rootfs/oem/uboot write, `/etc/init.d/S03weston` change, autostart change, database overwrite, cloud server code change, or RKNN fallback removal was performed.

## 2026-06-10 V2.6.9

- Completed `V2.6.9 Voice Guard Real Mode + Numeric Parser Hardening + Payment QR Final Fix`.
- Reclassified V2.6.8 as automated `TECH PASS` but field UX insufficient.
- Changed QR generation to PNG-first using PIL from the pyqrcode matrix; SVG remains as compatibility output.
- Added board payment URL selection: cloud URL first, then board LAN URL, then `local_debug` 127.0.0.1 with explicit warning.
- Extended order JSON with `payment_mode`, `local_debug_only`, `board_lan_ip`, `board_lan_iface`, `local_url_candidates`, and `qr_message`.
- Rewrote `PaymentDialog.qml` with clear cloud/local/local_debug status, QR error text, payment link text, and regenerate button.
- Hardened voice parsing for inline wake phrases such as `小售小售1`, `小搜小搜1`, and `小售小售我要结账`.
- Added numeric-only parser for button voice mode; natural phrases such as `我要结账` and `删除上一件` no longer execute after pressing the voice button.
- Enlarged the QML numeric voice menu so it is always visible and understandable in field use.
- Added tests: `speech_wake_inline_execute_test.py`, `speech_numeric_only_button_test.py`, `speech_guard_real_mode_test.py`, and `payment_qr_final_test.py`.
- Updated `speech_safety_no_false_action_test.py` for the V2.6.9 inline wake policy while preserving no-wake safety checks.
- Board regression PASS: inline wake `14/14`, button numeric-only `8/8`, guard real mode `9/9`, safety `6/6`, payment QR final `9/9`, V2.6 scan 10-SKU `43/43`, RKNN CLI smoke, and main business regressions.
- Cloud and board LAN were unavailable during this run, so payment correctly reported `local_debug`; Release Freeze still requires final human HDMI QR/menu confirmation and cloud retest if cloud paid callback will be shown.
- No flashing, RKDevTool, Upgrade/EraseFlash, boot/rootfs/oem/uboot write, `/etc/init.d/S03weston` change, autostart change, database overwrite, cloud server change, `/userdata/qt5` deletion, or checkpoint destruction was performed.

## 2026-06-10 V2.6.8

- Completed `V2.6.8 Voice Guard Mode + Payment QR Fix + Final Demo UX Gate`.
- Added wake-plus-command parsing for one-utterance commands such as `小售小售一` and `小售小售我要结账`.
- Fixed phrase priority so `我要结账` is not misread as digit `1`.
- Added button-direct numeric voice flow: after QML button wake, the operator can say the digit directly.
- Added optional voice guard APIs and QML controls, with bounded recordings under `static/audio/voice_guard/`.
- Added guard cleanup/status fields to `/api/state`.
- Added payment QR order fields and `/api/payment/qr/regenerate`.
- Updated payment dialog QR source priority and explicit cloud/local fallback status.
- Reworded RKNN vision display to auxiliary reference wording and removed misleading low-confidence terms.
- Added tests: `speech_wake_plus_number_test.py`, `speech_button_direct_numeric_test.py`, `speech_guard_mode_test.py`, and `payment_qr_generation_test.py`.
- Board regression PASS: wake numeric `19/19`, wake-plus-number `14/14`, button numeric `5/5`, guard mode `7/7`, payment QR `6/6`, V2.6 scan 10-SKU `43/43`, RKNN CLI smoke, and full main business regression.
- Cloud payment was unreachable from the board during this run, so local QR fallback was verified; cloud paid writeback remains previously proven and should be retested when field network is online.
- Release Freeze is still not entered; V2.6.8 is ready for final human HDMI/payment visual confirmation.
- No flashing, RKDevTool, Upgrade/EraseFlash, boot/rootfs/oem/uboot write, `/etc/init.d/S03weston` change, autostart change, database overwrite, checkpoint deletion, or cloud server change was performed.

## 2026-06-10 V2.6.7

- Completed `V2.6.7 Wake Word + Numeric Voice Command + Final UX Polish Gate`.
- Added wake-word gated voice session APIs: `/api/speech/wake_once`, `/api/speech/command_once`, `/api/speech/session_step`, `/api/speech/cancel`, and `/api/speech/menu`.
- Added closed-domain numeric command mapping: `1` query total, `2` remove last, `3` clear cart, `4` checkout, `5` capture/vision, `0` cancel.
- Added guard rails so destructive voice actions are not executed unless the wake word has been accepted first.
- Kept legacy manual `/api/speech/execute` for text/debug compatibility.
- Updated QML voice operation area with wake prompt, numeric menu cards, session status, raw text, normalized digit, and action result.
- Updated the main QML speech button to `语音唤醒`.
- Reworded QML vision status from confidence-risk language to demo-safe auxiliary-reference wording.
- Added tests: `tools/speech_wake_numeric_command_test.py` and `tools/speech_safety_no_false_action_test.py`.
- Board regression PASS: wake numeric command `19/19`, speech false-action prevention `5/5`, speech fuzzy command `18/18`, speech spam/timeout, cart total consistency, UI total consistency, capture preview stability, scan API matrix, QML business, input arbitration, capture stress, audio event matrix `24/24`, V2.6 10-SKU scan matrix, scan auto vision verify, vision status/predict/verify/no-repeat-add, and RKNN CLI smoke.
- Created checkpoint `/userdata/smart_retail/checkpoints/v267_wake_numeric_voice_polished_20260610_041917`.
- Decision: `READY_FOR_RELEASE_FREEZE_AFTER_HUMAN_HDMI_CONFIRMATION`; Release Freeze is still not entered in this gate.
- No flashing, RKDevTool, Upgrade/EraseFlash, boot/rootfs/oem/uboot write, `/etc/init.d/S03weston` change, autostart change, database overwrite, checkpoint destruction, or cloud server change was performed.

## 2026-06-10 V2.6.6

- Completed `V2.6.6 Field UI/UX Stabilization + Speech Fuzzy Command Gate`.
- Fixed cart total display source by binding QML cart total to backend `/api/state.cart_total_cent`.
- Added `/api/state.cart_total_recomputed_cent`.
- Added capture preview metadata: `latest_capture_id`, `latest_capture_updated_at`, `latest_capture_thumb`, and `latest_capture_thumb_url`.
- Added thumbnail generation under `static/captures/thumbs/`.
- Added QML double-buffer image preview so the old preview remains visible until the new thumbnail is ready.
- Added large QML status card for scan, speech, and RKNN/vision reference score.
- Added confidence-band language for reference score and auxiliary verification.
- Added fixed command voice matcher `normalize_voice_command()` before the older fuzzy speech rules.
- Added voice prompt tags in QML: `一共多少钱 / 删除上一件 / 清空购物车 / 我要结账 / 拍照`.
- Added tests: `tools/cart_total_ui_consistency_test.py`, `tools/capture_preview_stability_test.py`, `tools/speech_fuzzy_command_test.py`.
- Regression PASS: cart total consistency, UI total consistency, capture preview stability, speech fuzzy command `18/18`, speech spam/timeout, scan auto vision verify, V2.6 10-SKU scan matrix, scan API matrix, QML business, input arbitration, capture stress, audio event matrix, vision status/predict/verify/no-repeat-add, RKNN CLI smoke.
- Decision: `READY_FOR_RELEASE_FREEZE_AFTER_HUMAN_HDMI_CONFIRMATION`.
- No flashing, RKDevTool, Upgrade/EraseFlash, boot/rootfs/oem/uboot write, `/etc/init.d/S03weston` change, autostart change, database overwrite, checkpoint destruction, or cloud server change was performed.

## 2026-06-10 V2.6.5

- Completed `V2.6.5 Field UX Hardening + Auto Vision Verify Sprint`.
- Reclassified V2.6.4 as `TECHNICAL PASS, FIELD UX BLOCKED`; V2.6.5 resolves the field UX blockers.
- Updated `/api/state.quick_products` to expose SKU001-SKU010 only, while keeping the full products list available.
- Added cart total consistency fields and warning logic in `/api/state`.
- Added capture status machine fields and `/api/system/reset_busy_flags`.
- Added `/api/speech/reset`, speech one-job busy guard, shorter recording bound, and 15-second Whisper timeout.
- Updated `/api/vision/verify_scan` to accept `capture=true`, allowing scan success to trigger capture + RKNN verification without repeat cart add.
- Rewrote QML Main and small components with clean UTF-8 Chinese text, 10-SKU product panel, split capture/speech busy states, manual capture auto-predict, scan-triggered vision verify, speech command prompt UI, and scanner focus recovery.
- Added tests: `tools/cart_total_consistency_test.py`, `tools/scan_auto_vision_verify_test.py`, `tools/speech_spam_timeout_test.py`.
- Board regression PASS: cart consistency, scan auto vision verify, speech spam/timeout, V2.6 10-SKU scan matrix, scan API matrix, QML business, input arbitration, capture stress, audio event matrix, vision model status, vision predict, vision scan verify, vision no-repeat-add, RKNN CLI smoke.
- Audio devices restored to `plughw:CARD=III,DEV=0`; capture/speech busy flags reset to idle after testing.
- No flashing, RKDevTool, Upgrade/EraseFlash, boot/rootfs/oem/uboot write, `/etc/init.d/S03weston` change, autostart change, database overwrite, checkpoint destruction, or cloud server change was performed.

## 2026-06-10 V2.6.4

- Completed `V2.6.4 RKNN Field Demo Evidence + Final Release Readiness`.
- Did not add new features; this was an evidence and release-readiness gate.
- Reconfirmed `/api/vision/status` reports `active_backend=rknn_cli`.
- Reconfirmed `tools/rknn_cli_smoke_test.py` PASS and `tools/vision_rknn_cli_backend_test.py` PASS.
- Reconfirmed RKNN direct/Flask path on SKU001: top1 `SKU001`, `source=rknn_cli`, confidence about `0.9976`.
- Ran final regression matrix: V2.6 scan 10-SKU `43/43 PASS`, scan API matrix `39/39 PASS`, QML business API PASS, input arbitration PASS, capture stress PASS, audio event matrix PASS, vision model status `6/6 PASS`, vision predict smoke PASS, vision scan verify PASS, vision no-repeat-add `3/3 PASS`, RKNN CLI smoke PASS.
- Added V2.6.4 reports:
  - `V264_RKNN_FIELD_DEMO_EVIDENCE_REPORT.md`
  - `V264_FINAL_REHEARSAL_CHECKLIST.md`
  - `V264_RKNN_EVIDENCE_MANIFEST.md`
  - `V264_RELEASE_READINESS_DECISION.md`
- Updated final demo script, video script, judge notes, evidence list, failure recovery card, RKNN QA, and limitations.
- Decision: `READY_FOR_RELEASE_FREEZE_AFTER_PHYSICAL_EVIDENCE_CAPTURE`.
- No flashing, RKDevTool, Upgrade/EraseFlash, boot/rootfs/oem/uboot write, `/etc/init.d/S03weston` change, autostart change, database overwrite, or cloud server change was performed.

## 2026-06-10 V2.6.3

- Completed `V2.6.3 RKNN Conversion Environment + C Runtime Bridge`.
- Built an isolated Linux x86_64 Python 3.8 RKNN Toolkit2 environment on a dedicated build host.
- Converted the V2.6.0 static ONNX 10-SKU classifier to RKNN FP and INT8 variants.
- Selected FP RKNN as default because FP matched ONNX top1 on 117/117 evaluation images; INT8 matched 116/117.
- Added `MODEL_ARTIFACTS_V263_ONNX/` and `MODEL_ARTIFACTS_V263_RKNN/`.
- Added `rknn_cls_runner_v263/`, a small RKNN C runtime CLI bridge.
- Cross-compiled `vision_rknn_cli` for RK3568/aarch64 using the SDK Buildroot host toolchain.
- Deployed the CLI and RKNN model under `/userdata/smart_retail/bin/vision_rknn_cli_v263/` and `/userdata/smart_retail/models/vision_10sku_rknn_v263/`.
- Confirmed board CLI smoke test: SKU001 top1 correct, `backend=rknn_cli`, `npu=true`, CLI latency 15 ms.
- Updated `app.py` so `/api/vision/status` and `/api/vision/predict` use RKNN CLI when available and keep ONNX Runtime fallback.
- Added `tools/rknn_cli_smoke_test.py` and `tools/vision_rknn_cli_backend_test.py`.
- Confirmed `/api/vision/status` reports `active_backend=rknn_cli`.
- Confirmed `/api/vision/predict` returns `source=rknn_cli`, top1 SKU001, confidence about 0.9976 on SKU001 product image.
- Re-ran main board regressions after RKNN integration: scan matrix `39/39 PASS`, QML business API PASS, input arbitration PASS, capture stress PASS, audio event matrix `24/24 PASS`, vision API gate `4/4 PASS`, RKNN backend test PASS.
- Preserved `VISION_AUTO_ADD_CART=false`; barcode remains the add-to-cart authority and vision remains verification/suggestion only.
- No flashing, RKDevTool, Upgrade/EraseFlash, boot/rootfs/oem/uboot write, `/etc/init.d/S03weston` change, autostart change, database overwrite, system Python pollution, or cloud payment server change was performed.

## 2026-06-10 V2.6.2

- Started `V2.6.2 RKNN/NPU Vision Backend Gate`.
- Completed RKNN toolchain/runtime discovery as `PARTIAL PASS`.
- Found RKNN SDK components in `rk3568_linux_r60_v1.3.2_qsm368zp-QSM368ZP_rl`, including `external/rknn-toolkit2`, `external/rknpu2`, RK356X Linux runtime libraries, and rknn demo packages.
- Confirmed SDK has RKNN-Toolkit2 Linux x86_64 wheels for cp36/cp38 and RKNNLite aarch64 wheels for cp37/cp39.
- Confirmed current Windows Python 3.12 cannot import RKNN Toolkit2 and cannot use the Linux x86_64 wheel directly.
- Confirmed the cloud SDK host has the same SDK/wheels but default Python is Ubuntu 24.04 Python 3.12; a separate Linux Python 3.8 venv/container is still required.
- Confirmed board NPU/C runtime evidence: RKNPU driver initialized, `/dev/dri/renderD129`, `/usr/lib/librknnrt.so`, `/usr/lib/librknn_api.so`, and `/usr/bin/rknn_server` exist.
- Confirmed board Python RKNNLite is missing for Python 3.8.
- Ran existing vendor `/userdata/rknn_yolov5_demo` successfully; it produced person/bus detections from `bus.jpg`, proving RKNN C runtime/NPU demo path is live.
- Added future-use scripts:
  - `tools/convert_onnx_to_rknn_v262.py`
  - `tools/rknn_runtime_import_test.py`
  - `tools/vision_rknn_inference_smoke_test.py`
- Did not export a project `.rknn` model because RKNN-Toolkit2 conversion environment is not active yet.
- Did not integrate RKNN into `app.py`; active backend remains V2.6.1 `onnxruntime`.
- Added V2.6.2 reports and fallback policy documents.
- No flashing, RKDevTool, Upgrade/EraseFlash, boot/rootfs/oem/uboot write, `/etc/init.d/S03weston` change, autostart change, database overwrite, system Python pollution, or app/QML RKNN switch was performed.

## 2026-06-09 V2.6.1

- Completed `V2.6.1 Board ONNX Runtime Feasibility Gate`.
- Downloaded a compatible `onnxruntime-1.16.3` cp38 manylinux2014 aarch64 wheel and dependencies into `wheelhouse_v261`.
- Deployed ONNX Runtime only as isolated app-local pydeps at `/userdata/smart_retail/pydeps/onnxruntime_v260`.
- Added `tools/onnxruntime_import_test.py` and confirmed board import works with `CPUExecutionProvider`.
- Added `tools/vision_onnx_inference_smoke_test.py` and confirmed `models/vision_10sku_v260/model.onnx` runs on the board CPU and returns Top-3.
- Updated `app.py` to detect and use isolated ONNX Runtime pydeps without modifying system Python.
- Updated vision verification so low-confidence ONNX predictions return `verification_low_confidence` instead of false mismatch.
- Updated `tools/vision_scan_verify_test.py` for low-confidence ONNX safety behavior.
- Confirmed `/api/vision/status` now reports `backend=onnxruntime`, `model_available=true`, `class_count=10`, and `pydeps_available=true`.
- Confirmed vision no-repeat-add remains PASS after ONNX enablement.
- Ran full regression after ONNX enablement: scan 10-SKU, scan API matrix, QML business API, input arbitration, capture stress, audio event matrix, vision model status, vision predict, vision verify, and no-repeat-add all PASS.
- Added V2.6.1 evidence and rollback docs:
  - `BOARD_ONNX_RUNTIME_ENV_PROBE.md`
  - `ONNXRUNTIME_WHEEL_SEARCH_REPORT.md`
  - `ONNXRUNTIME_DEPLOY_DECISION.md`
  - `ONNXRUNTIME_DEPLOY_REPORT.md`
  - `ONNXRUNTIME_IMPORT_TEST_REPORT.md`
  - `VISION_ONNX_INFERENCE_SMOKE_REPORT.md`
  - `BOARD_ONNX_VISION_BACKEND_REPORT.md`
  - `VISION_ONNX_API_TEST_REPORT.md`
  - `VISION_NO_REPEAT_ADD_AFTER_ONNX_REPORT.md`
  - `V261_BOARD_ONNX_RUNTIME_FEASIBILITY_REPORT.md`
  - `V261_BOARD_ONNX_RUNTIME_FINAL_DECISION.md`
  - `V261_BOARD_VISION_BACKEND_STATUS.md`
  - `V261_TEST_RESULTS.md`
  - `V261_ROLLBACK_GUIDE.md`
- No flashing, RKDevTool, Upgrade/EraseFlash, boot/rootfs/oem/uboot write, `/etc/init.d/S03weston` change, autostart change, system site-packages change, or database overwrite was performed.

## 2026-06-09 V2.6.0

- Added V2.6.0 10-SKU vision baseline from `图像识别.zip`.
- Normalized 117 images into `dataset_raw_v260/` and generated `TEN_SKU_MANIFEST_V260.csv`, `DATASET_INTAKE_V260_REPORT.md`, `DATASET_QUALITY_SUMMARY_V260.md`, and `DATASET_CONTACT_SHEET_V260.jpg`.
- Built Ultralytics classification dataset at `datasets/vision_10sku_cls_v260/` with fixed SKU001-SKU010 label order.
- Trained YOLOv8n-cls baseline locally for 50 epochs and exported `MODEL_ARTIFACTS_V260/best.pt`, `last.pt`, and `model.onnx`.
- Evaluated the baseline model: 18 test images, Top-1 94.44%, Top-3 100.00%; documented as low-sample baseline, not final production accuracy.
- Added `/api/vision/predict` and improved `/api/vision/status`, `/api/vision/verify_scan`, and `/api/vision/candidates` for V2.6 model metadata and safe fallback behavior.
- Fixed `verify_scan` so model-unavailable fallback candidates cannot be misreported as visual matches; it now returns `verification_pending_no_model`.
- Updated fallback vision candidates to come from the current product catalog instead of old quick-product seed IDs.
- Updated `tools/product_catalog_import.py` for dry-run/apply, database backup, product image paths, and barcode upsert.
- Added `tools/scan_v260_10sku_test.py` and refreshed regression tests to read the active product catalog dynamically.
- Deployed model artifacts, manifest, product images, app.py, QML files, and tools to `/userdata/smart_retail` only.
- Imported 10 products/barcodes on board after database backup; prices are placeholder `price_cent=100` and require user confirmation.
- Board runtime detection found `numpy` and `PIL` available, but `onnxruntime`, `torch`, and `ultralytics` missing; board neural inference is therefore honestly marked pending/unavailable.
- Board regression passed: V2.6 scan matrix `43/43`, scan matrix `39/39`, QML business `41/41`, input arbitration `6/6`, capture stress `12/12`, audio matrix `24/24`, vision status/predict/verify/no-repeat/API gate PASS.
- Added V2.6 reports including `BOARD_VISION_INTEGRATION_REPORT.md`, `VISION_BACKEND_DETECTION_REPORT.md`, `V260_FINAL_TEST_RESULTS.md`, `V260_10SKU_VISION_BASELINE_REPORT.md`, `V260_LIMITATIONS_HONEST_LIST.md`, `V260_EVIDENCE_MANIFEST.md`, and `V260_ROLLBACK_GUIDE.md`.
- No RKDevTool, Upgrade, EraseFlash, boot/rootfs/oem/uboot write, `/etc/init.d/S03weston` change, autostart change, `/userdata/qt5` deletion, or database overwrite was performed.

## 2026-06-09 V2.5.20h-A

- Completed Human Voice Listening Acceptance with user confirmation: `听感通过`.
- Updated `HUMAN_VOICE_LISTENING_ACCEPTANCE_REPORT.md` from `PENDING_USER_CONFIRMATION` to `PASS`, with `user_confirmation=pass`, `listening_status=accepted`, and `conclusion=V2.5.20h-A PASS`.
- Created board checkpoint `/userdata/smart_retail/checkpoints/v2520h_human_tts_pass_20260609_144230`.
- Checkpoint contains 51 files, including 26 WAV files, `app.py`, `qt_kiosk/`, `tools/audio_asset_audit.py`, `tools/audio_event_matrix_test.py`, human voice reports, audio matrix report, and changelog.
- Re-ran final validation: `audio_event_matrix_test.py` `24/24 PASS`, `scan_api_matrix_test.py` `29/29 PASS`, `qml_business_api_test.py` PASS, and `/api/state` HTTP 200.
- Paid and synced the final regression-created order `ORDER20260609064446555` / `CLOUD2026060906444749808D`, leaving the board with `latest_order.payment_status=paid`, `latest_order.cloud_status=paid`, and `latest_audio_event=payment_success`.
- Added `V2520H_HUMAN_TTS_CHECKPOINT_REPORT.md`.
- No RKDevTool, Upgrade, EraseFlash, boot/rootfs/oem/uboot write, autostart change, database overwrite, cloud server code change, or major app.py/QML rewrite was performed.

## 2026-06-09 V2.5.20h

- Completed AI TTS Human Voice Asset Generation Gate for fixed Chinese operation prompts.
- Added `tools/generate_human_voice_wavs.py`, with OpenAI `gpt-4o-mini-tts` support when `OPENAI_API_KEY` is present and edge-tts neural Chinese fallback when no key is available.
- Generated and deployed PCM WAV 16 kHz mono prompt assets for `system_ready`, `scan_success`, `unknown_product`, `scan_failed`, `capture_start`, `capture_success`, `capture_busy`, `capture_failed`, `remove_last`, `cart_clear`, `total_query`, `payment_wait`, `payment_success`, `voice_ready`, `voice_processing`, `voice_success`, `voice_failed`, `input_routed_scan`, plus backend `add_cart`.
- Updated `app.py` audio event filename mapping so semantic events use same-name WAV files instead of unrelated reused prompts.
- Updated `tools/audio_asset_audit.py` to reflect the final event-to-WAV mapping and clean Chinese prompt text.
- Backed up local audio at `static/audio_backup_before_human_tts_20260609_051622`.
- Backed up board audio at `/userdata/smart_retail/static/audio_backup_before_human_tts_20260609_051659` and board app mapping at `/userdata/smart_retail/app.py.v2520h_audio_mapping_bak_20260609_051659`.
- Verified `system_ready.wav` plays after `sh /userdata/start_retail_hdmi_qml.sh`.
- Re-ran audio matrix after shortening `scan_success.wav`, `add_cart.wav`, and `payment_wait.wav`: `AUDIO_EVENT_MATRIX_CHECKS=24 PASS=24 FAIL=0`.
- Re-ran core regressions after TTS deployment: scan matrix `29/29 PASS`, QML business API PASS, input arbitration `6/6 PASS`, and capture stress `12/12 PASS`.
- Paid and synced the regression-created latest order `ORDER20260608212417878` / `CLOUD20260608212418F6B0E5`, leaving `/api/state` with `latest_order.payment_status=paid` and `latest_audio_event=payment_success`.
- Added `HUMAN_VOICE_TTS_GENERATION_REPORT.md`, `HUMAN_VOICE_FINAL_ASSET_TABLE.md`, `HUMAN_VOICE_LISTENING_CHECKLIST.md`, and `AUDIO_EVENT_MATRIX_AFTER_TTS.md`.
- Manual headset listening remains a user-side final check; these files are synthesized TTS assets, not live human recordings.
- No RKDevTool, Upgrade, EraseFlash, boot/rootfs/oem/uboot write, autostart change, database overwrite, `/userdata/qt5` deletion, or cloud server code change was performed.

## 2026-06-09 V2.5.20g Checkpoint Snapshot

- Created board checkpoint `/userdata/smart_retail/checkpoints/v2520g_cloud_paid_pass_20260609_045133` with 61 files, including `app.py`, `qt_kiosk/`, `tools/`, API/docs, final demo docs, cloud payment docs, and database backups.
- Wrote latest checkpoint pointer `/userdata/smart_retail/checkpoints/latest_v2520g_cloud_paid_pass.txt`.
- Paid and synced the regression-created final latest order `ORDER20000102064102569` / `CLOUD20260608205632317CFB`, leaving `/api/state` with `latest_order.payment_status=paid`, `latest_order.cloud_status=paid`, and `audio.latest_event=payment_success`.
- Collected readonly cloud evidence from `/root/cloud_payment_service_v1/cloud.log`, including final `POST /api/orders`, `POST /pay/CLOUD20260608205632317CFB`, and `GET /api/orders/CLOUD20260608205632317CFB` entries.
- Reconfirmed checkpoint regressions: scan matrix `29/29 PASS`, QML business API PASS, input arbitration `6/6 PASS`, capture stress `12/12 PASS`, audio event matrix `24/24 PASS`, and vision API gate `4/4 PASS`.
- Added `V2520G_CHECKPOINT_SNAPSHOT_REPORT.md`, `CLOUD_PAYMENT_PAID_PASS_EVIDENCE.md`, `BOARD_NETWORK_WORKING_STATE.md`, `CLOUD_PAYMENT_DEMO_READY_CARD.md`, and `V2520G_ROLLBACK_GUIDE.md`.
- Release Freeze remains deferred: 10-SKU final model data, real human Chinese WAV prompts, and field evidence photos are still pending.
- No RKDevTool, Upgrade, EraseFlash, boot/rootfs/oem/uboot write, `/etc/init.d/S03weston` modification, autostart persistence, database overwrite, cloud server code change, firewall change, or cloud service restart was performed.

## 2026-06-09 V2.5.20g

- Enabled Windows ICS from `WLAN` to `Realtek PCIe GbE Family Controller` using `tools/enable_windows_ics_wlan_to_realtek.ps1`; log written to `WINDOWS_ICS_ENABLE_LOG.txt`.
- Board `eth0` received `192.168.137.191/24` and default route `via 192.168.137.1 dev eth0`.
- Verified board `/health` returns `ok=true` for the configured cloud payment service.
- Verified `/api/cloud/status` returns `ok=true`, HTTP 200, and `cloud health ok`.
- Verified `tools/cloud_payment_probe.py --create-test-order` creates cloud order `CLOUD202606082032217F9F00`.
- Ran a real checkout cloud payment flow: local order `ORDER20000102062434777`, cloud order `CLOUD20260608204004347371`, cloud pay URL opened from Windows, simulated payment succeeded, board `/api/order/...` synced local order to `paid`.
- After regression tests created a newer unpaid cloud order, paid and synced final latest order `ORDER20000102062556248` / `CLOUD20260608204126ED2907` so the board was left with `latest_order.payment_status=paid` and `latest_audio_event=payment_success`.
- Fixed the payment-success audio trigger in `app.py` by committing/closing the order DB transaction before calling `play_audio("payment_success")`; board backup stored at `/userdata/smart_retail/app.py.v2520g_audio_paid_bak_20260609_043837`.
- Confirmed `/api/state.audio.latest_event=payment_success` and latest order `payment_status=paid`.
- Re-ran local regressions after the app patch and cloud retest: scan matrix `29/29 PASS`, QML business API PASS, input arbitration `6/6 PASS`, capture stress `12/12 PASS`, audio event matrix `24/24 PASS`, and vision API gate `4/4 PASS`.
- Updated cloud payment route, ICS, paid writeback, demo, failure recovery, and remaining-risk docs.
- No RKDevTool, Upgrade, EraseFlash, boot/rootfs/oem/uboot write, `/etc/init.d/S03weston` modification, autostart persistence, database overwrite, cloud server code change, firewall change, or cloud service restart was performed.

## 2026-06-09 V2.5.20f

- Re-tested board Internet outlet after connecting an Ethernet cable between the Windows PC and the board.
- Confirmed board `eth0` is now `LOWER_UP`; Windows Realtek Ethernet is `Up 100 Mbps` with `192.168.137.1/24`.
- Tried DHCP on board `eth0`; Windows did not provide a lease.
- Added temporary board Ethernet configuration `eth0 192.168.137.2/24` and default route `via 192.168.137.1 dev eth0`.
- Confirmed layer-2 adjacency: Windows ARP sees board `192.168.137.2 -> 6e-28-a4-b5-37-ab`, and board ARP sees Windows `192.168.137.1 -> b0:25:aa:6c:18:25`.
- Confirmed Windows direct no-proxy access to the configured cloud `/health` endpoint returns HTTP 200.
- Board cloud `/health` and `cloud_payment_probe` still time out, so Windows Ethernet ICS/NAT/firewall forwarding remains blocked.
- Confirmed current PowerShell is not administrator (`net session` access denied), and ICS COM status read fails with `E_ACCESSDENIED`; Codex did not modify Windows ICS/firewall settings.
- Re-ran local regressions after the Ethernet route change: scan matrix `29/29 PASS`, QML business API PASS, input arbitration `6/6 PASS`, capture stress `12/12 PASS`, audio event matrix `24/24 PASS`, and vision API gate `4/4 PASS`.
- Added `BOARD_INTERNET_OUTLET_FIX_REPORT.md`, `WINDOWS_ICS_RNDIS_SETUP_REPORT.md`, `BOARD_ROUTE_FINAL_STATE.md`, `CLOUD_PAYMENT_PAID_WRITEBACK_FINAL_RETEST.md`, and `CLOUD_PAYMENT_DEMO_STATUS_DECISION.md`.
- Updated cloud payment field commands, remaining risk, final demo script, and failure recovery card.
- No RKDevTool, Upgrade, EraseFlash, boot/rootfs/oem/uboot write, `/etc/init.d/S03weston` modification, autostart persistence, database overwrite, cloud server modification, or cloud service restart was performed.

## 2026-06-09 V2.5.20e

- Locked the cloud payment service behind a local deployment configuration; credentials, host identity and SSH paths are intentionally excluded from the public repository.
- Verified the configured cloud `/health` endpoint returns HTTP 200 and the service listens on its configured port.
- Collected board network diagnostics: `eth0/wlan0/wlan1` have no carrier, `usb0/usb1` have only `169.254.x.x`, DNS has no nameserver, and any `default dev usb0 scope link` route is a non-working link-local route.
- Collected Windows topology: Internet is on `WLAN`, while `Remote NDIS based Internet Sharing Device` is link-local `169.254.170.203/16` with no gateway and Windows IP routing disabled.
- Tried one scoped temporary route probe through `usb1 -> 169.254.170.203`; cloud ping and `/health` did not work, so the temporary route was removed.
- Ran `cloud_payment_probe`; cloud status and test-order creation remain blocked by board network timeout, so cloud paid writeback is not verified.
- Re-ran local regressions after the route probe: scan matrix `29/29 PASS`, QML business API PASS, input arbitration `6/6 PASS`, capture stress `12/12 PASS`, audio event matrix `24/24 PASS`, and vision API gate `4/4 PASS`.
- Added `CLOUD_BOARD_ROUTE_FIX_REPORT.md`, `CLOUD_PAYMENT_PAID_RETEST_REPORT.md`, `CLOUD_PAYMENT_SERVER_IDENTITY_LOCKED.md`, `CLOUD_PAYMENT_NETWORK_TOPOLOGY.md`, `CLOUD_PAYMENT_FIELD_COMMANDS.md`, and `CLOUD_PAYMENT_REMAINING_RISK.md`.
- Updated cloud payment recovery, network fix commands, final demo script, and failure recovery card.
- No RKDevTool, Upgrade, EraseFlash, boot/rootfs/oem/uboot write, `/etc/init.d/S03weston` modification, autostart persistence, database overwrite, or cloud service restart was performed.

## 2026-06-09 V2.5.20d

- Ran field blocker burn-down diagnostics for cloud network and HDMI display state.
- Classified cloud payment blocker as `board_no_default_route`: board has no default route, empty DNS, link-local USB IPs only; Windows host can reach cloud `/health`.
- Updated cloud fallback docs and field network fix commands without changing boot/rootfs or system networking permanently.
- Updated `/userdata/start_retail_hdmi_qml.sh` to log `HDMI_STATUS`, `LVDS_STATUS`, and `HDMI_FIELD_GATE`.
- Confirmed latest HDMI field gate is `DISCONNECTED_CHECK_CABLE_POWER_INPUT_SOURCE`; QML/Flask/Weston processes remain healthy.
- Extended audio asset audit to include recommended WAV filename, prompt text, reuse, and replacement recommendation.
- Added human voice replacement TODO, naming rules, and test guide.
- Added `dataset_raw/` staging structure and 10-SKU waiting-data docs.
- Added demo reset apply policy and field usage card.
- Added `FIELD_BLOCKER_BURNDOWN_REPORT.md`, `FIELD_BLOCKERS_STATUS_TABLE.md`, `RELEASE_FREEZE_DECISION_AFTER_V2520D.md`, and `REMAINING_BEFORE_RELEASE_FREEZE.md`.
- Release Freeze remains blocked; current system remains application-layer demonstrable once HDMI is connected.

## 2026-06-09 V2.5.20c

- Added cloud payment recovery probes: `GET /api/cloud/status` and `POST /api/cloud/test_order`.
- Added safe vision trigger APIs: `/api/vision/status`, `/api/vision/verify_scan`, `/api/vision/candidates`, and `/api/vision/confirm`.
- Updated QML/JS so successful scans trigger one-shot vision verification and unknown barcodes trigger candidate lookup without auto add-cart.
- Added `/api/state` vision fields, with `vision_auto_add_cart=false`.
- Added 10-SKU dataset intake, catalog import, training dry-run, model artifact export, and board install planning tools.
- Added audio asset audit and human voice recording/replacement documentation.
- Added safe demo reset tooling with backup-first behavior.
- Added cloud, vision, dataset, audio, reset, and pre-release decision reports.
- Confirmed local syntax checks pass; training dry-run correctly reports missing dataset because new 10-SKU data has not been supplied.
- No RKDevTool, Upgrade, EraseFlash, boot/rootfs/oem/uboot write, system autostart, `/etc/init.d/S03weston` edit, `/userdata/qt5` delete, or database overwrite was performed.

## 2026-06-09 V2.5.20b

- Added Full Operation Voice Broadcast coverage before Release Freeze.
- Added fixed audio events for `system_ready`, `scan_failed`, `capture_start`, `capture_success`, `capture_busy`, `capture_failed`, `remove_last`, `total_query`, and `input_routed_scan`.
- Kept dynamic TTS out of scope; events reuse existing stable WAV files where dedicated Chinese prompts are not yet present.
- Updated `play_audio()` with a lightweight lock and single active `aplay` process policy; new prompts interrupt previous prompts to avoid process buildup.
- Updated API responses where practical with latest `audio_event`, `audio_ok`, `audio_message`, and `audio_device`.
- Updated `qt_kiosk/Main.qml` so QML startup triggers `system_ready`.
- Added `RetailApi.playAudio()` in `qt_kiosk/retail_api.js`.
- Added `tools/audio_event_matrix_test.py`.
- Verified `AUDIO_EVENT_MATRIX_CHECKS=24 PASS=24 FAIL=0`.
- Verified bad audio output returns stable JSON and does not crash the scan business path.
- Verified `SCAN_API_MATRIX_CHECKS=29 PASS=29 FAIL=0`.
- Verified `QML_BUSINESS_CHECKS=41 PASS=41 FAIL=0`.
- Verified `INPUT_ARBITRATION_API_CHECKS=6 PASS=6 FAIL=0`.
- Verified `CAPTURE_STRESS_CHECKS=12 PASS=12 FAIL=0`.
- Verified `restore_default_weston.sh` and `start_retail_hdmi_qml.sh`, leaving final state in HDMI QML mode with `/api/state` HTTP 200 and `latest_event=system_ready`.
- Added `FULL_OPERATION_VOICE_BROADCAST_REPORT.md`, `AUDIO_EVENT_MATRIX_REPORT.md`, `AUDIO_BROADCAST_POLICY.md`, `QML_AUDIO_EVENT_STATUS_REPORT.md`, `FULL_OPERATION_VOICE_MANUAL_TEST_CHECKLIST.md`, and `QML_V2520B_CHANGELOG.md`.
- No RKDevTool, Upgrade, EraseFlash, boot/rootfs/oem/uboot write, `/etc/init.d/S03weston` modification, autostart persistence, `/userdata/qt5` deletion, database overwrite, terminal fallback removal, or launcher rollback breakage was performed.

## 2026-06-09 V2.5.20

- Completed Final Field Rehearsal without adding new runtime features.
- Captured local rehearsal logs under `field_rehearsal_logs/`.
- Verified ADB online, `/api/state` HTTP 200, `/userdata` free space around 365 MB, HDMI-A-1 connected, camera nodes, HyperX playback/capture, and Megahunt HID ScanBox.
- Verified `SCAN_API_MATRIX_CHECKS=29 PASS=29 FAIL=0`.
- Verified `INPUT_ARBITRATION_API_CHECKS=6 PASS=6 FAIL=0`.
- Verified `CAPTURE_STRESS_CHECKS=12 PASS=12 FAIL=0 SUCCESSES=1 NO_500=True`.
- Ran two QML business rehearsals; all business items returned `pass=true`.
- Verified second rehearsal checkout generated `ORDER20000102032417453 / ¥2.00 / unpaid`.
- Verified audio prompt output, HyperX recording, recorded-file playback, and `/speech/auto_once seconds=1 execute=0`.
- Verified `restore_default_weston.sh` then `start_retail_hdmi_qml.sh` leaves the board in HDMI QML mode with `/api/state` HTTP 200.
- Added `FINAL_FIELD_REHEARSAL_REPORT.md`, `FINAL_FIELD_REHEARSAL_CHECKLIST.md`, `FINAL_FIELD_REHEARSAL_LOG_SUMMARY.md`, `FINAL_DEMO_EVIDENCE_LIST.md`, `FINAL_DEMO_FAILURE_RESPONSE_CARD.md`, and `FINAL_READY_STATE.md`.
- Noted that physical HDMI and port photos still need to be taken by the operator before V2.5.21 Release Freeze & Evidence Pack.
- No RKDevTool, Upgrade, EraseFlash, boot/rootfs/oem/uboot write, `/etc/init.d/S03weston` modification, autostart persistence, `/userdata/qt5` deletion, database overwrite, terminal fallback removal, or launcher rollback breakage was performed.

## 2026-06-09 V2.5.18f-B

- Re-ran the USB Audio I/O gate after HyperX Cloud III was connected and enumerated.
- Confirmed ALSA device `card 2 [III]: USB-Audio - HyperX Cloud III` appears in both `aplay -l` and `arecord -l`.
- Froze app audio input/output as `plughw:CARD=III,DEV=0`.
- Verified direct hardware playback, microphone recording, and recording playback through HyperX.
- Added `/api/audio/status`, `/api/audio/set`, `/api/audio/test_output`, and `/api/audio/test_record`.
- Added audio latest-status tracking into `/api/state.audio.latest_*`.
- Added fixed-WAV voice prompt aliases: `voice_ready`, `voice_processing`, `voice_success`, and `voice_failed`.
- Updated `/speech/auto_once` and speech recording flow with prompt hooks.
- Updated `qt_kiosk/Main.qml` to show audio input/output and latest prompt status in the speech area.
- Verified `/api/audio/test_output` plays `scan_success` through `plughw:CARD=III,DEV=0`.
- Verified `/api/audio/test_record` creates `api_audio_test.wav`, and `/api/audio/test_output` can play that recorded file.
- Verified `/speech/auto_once seconds=1 execute=0` returns `ok=true`, proving the HyperX record path can enter the Whisper recognition path.
- Verified `SCAN_API_MATRIX_CHECKS=29 PASS=29 FAIL=0`.
- Verified `QML_BUSINESS_CHECKS=41 PASS=41 FAIL=0`.
- Verified `INPUT_ARBITRATION_API_CHECKS=6 PASS=6 FAIL=0`.
- Verified `restore_default_weston.sh` and `start_retail_hdmi_qml.sh` still work, leaving the board in HDMI QML mode with `/api/state` HTTP 200.
- Updated `USB_AUDIO_IO_GATE_REPORT.md`, `USB_AUDIO_DEVICE_CONFIG_REPORT.md`, `VOICE_PROMPT_FLOW_REPORT.md`, `AUDIO_QML_STATUS_REPORT.md`, `USB_AUDIO_MANUAL_TEST_CHECKLIST.md`, and `API_CONTRACT.md`.
- No RKDevTool, Upgrade, EraseFlash, boot/rootfs/oem/uboot write, `/etc/init.d/S03weston` modification, autostart persistence, `/userdata/qt5` deletion, database overwrite, terminal fallback removal, or launcher rollback breakage was performed.

## 2026-06-09 V2.5.18f

- Ran the USB Audio I/O hardware gate before implementation.
- Confirmed `plughw:CARD=III,DEV=0` is not currently exposed by ALSA.
- Confirmed `aplay -D plughw:CARD=III,DEV=0 ...` fails with `No such device`.
- Confirmed `arecord -D plughw:CARD=III,DEV=0 ...` fails with `No such device`.
- Confirmed `arecord -l` currently shows only board codec capture, not USB capture.
- Noted that the current app audio state still points to `plughw:CARD=III,DEV=0`, which is stale until the USB audio device is connected/enumerated.
- Added `USB_AUDIO_IO_GATE_REPORT.md`, `USB_AUDIO_DEVICE_CONFIG_REPORT.md`, `VOICE_PROMPT_FLOW_REPORT.md`, `AUDIO_QML_STATUS_REPORT.md`, and `USB_AUDIO_MANUAL_TEST_CHECKLIST.md`.
- Did not implement `/api/audio/*` or QML audio status changes because the hardware prerequisite failed.
- No RKDevTool, Upgrade, EraseFlash, boot/rootfs/oem/uboot write, `/etc/init.d/S03weston` modification, autostart persistence, `/userdata/qt5` deletion, database overwrite, terminal fallback removal, or launcher rollback breakage was performed.

## 2026-06-09 V2.5.19

- Froze the competition demo flow without adding new runtime features.
- Added `DEMO_FLOW_FREEZE.md` with the fixed end-to-end demo sequence: startup, hardware form, SKU006/SKU007 scanning, unknown barcode feedback, capture, speech commands, clear/re-add, checkout, and backend evidence.
- Added `DEMO_OPERATOR_CHECKLIST.md` for pre-demo checks: ADB online, `/api/state`, app/QML processes, HDMI visibility, scanner USB Host port, camera, USB audio, `/userdata` space, and start/restore scripts.
- Added `DEMO_FAILURE_FALLBACKS.md` covering QML recovery, default Weston restore, scanner wrong-port behavior, capture retry/cooldown, cloud payment fallback, voice fallback, and API recovery.
- Added `DEMO_VIDEO_SCRIPT.md` for a 3-5 minute recording script.
- Added `DEMO_JUDGE_EXPLANATION_NOTES.md` for architecture, Qt/QML runtime rationale, scanner HID behavior, capture robustness, input arbitration, voice reliability, YOLO evidence, metrics, and autostart rationale.
- Explicitly kept system-level autostart out of scope.
- No RKDevTool, Upgrade, EraseFlash, boot/rootfs/oem/uboot write, `/etc/init.d/S03weston` modification, `/userdata/qt5` deletion, database overwrite, terminal fallback removal, or launcher rollback breakage was performed.

## 2026-06-08 V2.5.18e

- Added capture robustness to `/api/capture`: mutex, cooldown, timeout handling, stable JSON feedback, and cleanup statistics.
- Added capture cleanup helpers and `POST /api/captures/cleanup`.
- Added `/api/state` capture storage fields: `capture_count` and `capture_total_size_mb`.
- Added `tools/capture_stress_test.py` for rapid capture regression.
- Added `tools/input_arbitration_api_test.py` for scan/speech API compatibility.
- Updated `qt_kiosk/Main.qml` with local capture anti-repeat guard, capture preview cache busting, capture count/storage display, barcode-like detection, speech-field input arbitration, and input route status.
- Updated `qt_kiosk/retail_api.js` with `cleanupCaptures()`.
- Added `CAPTURE_ROBUSTNESS_REPORT.md`, `CAPTURE_CLEANUP_POLICY.md`, `CAPTURE_STRESS_TEST_REPORT.md`, `INPUT_ARBITRATION_REPORT.md`, `QML_INPUT_MODE_FIX_REPORT.md`, `QML_V2518E_MANUAL_TEST_CHECKLIST.md`, and `QML_V2518E_CHANGELOG.md`.
- Verified `SCAN_API_MATRIX_CHECKS=29 PASS=29 FAIL=0`.
- Verified `BUSINESS_API_CHECKS=41 PASS=41 FAIL=0 FINAL_TOTAL=¥0.00`.
- Verified `INPUT_ARBITRATION_API_CHECKS=6 PASS=6 FAIL=0`.
- Verified `CAPTURE_STRESS_CHECKS=12 PASS=12 FAIL=0 SUCCESSES=1 NO_500=True`.
- Verified `restore_default_weston.sh` and `start_retail_hdmi_qml.sh` still work, leaving the board in HDMI QML mode with `/api/state` HTTP 200.
- Still no RKDevTool, Upgrade, EraseFlash, boot/rootfs/oem/uboot write, `/etc/init.d/S03weston` modification, autostart persistence, `/userdata/qt5` deletion, database overwrite, terminal fallback removal, or launcher rollback breakage was performed.
- Recommended next stage after manual HDMI checks: V2.5.19 Demo Flow Freeze.

## 2026-06-08 V2.5.18d

- Closed the scanner hardware/input investigation as `scanner_hid_keyboard_event_ok`.
- Field-confirmed that the scanner beeps but QML does not react when plugged into the wrong/original USB port.
- Field-confirmed that the scanner works when moved to the verified USB Host port previously used by the keyboard.
- Captured board HID evidence: `Megahunt HID ScanBox` with `Handlers=kbd ... event5`, proving the scanner is operating as HID Keyboard on the correct port.
- Added `SCANNER_DEVICE_MODE_GATE_REPORT.md`, `SCANNER_FIELD_PORT_RULES.md`, and `SCANNER_FINAL_ACCEPTANCE_CHECKLIST.md`.
- Updated `QML_SCANNER_HID_FIELD_TEST_CHECKLIST.md` with fixed port rules and competition wiring checks.
- Re-ran isolated API regressions after temporarily pausing QML to avoid live scanner input mutating the cart: `SCAN_API_MATRIX_CHECKS=29 PASS=29 FAIL=0` and `BUSINESS_API_CHECKS=41 PASS=41 FAIL_OR_UNKNOWN=0 FINAL_TOTAL=¥0.00`.
- Restarted QML through `/userdata/start_retail_hdmi_qml.sh`; board returned to HDMI QML mode with `/api/state` HTTP 200 and cart `0 / ¥0.00`.
- Still no RKDevTool, Upgrade, EraseFlash, boot/rootfs/oem/uboot write, `/etc/init.d/S03weston` modification, autostart persistence, `/userdata/qt5` deletion, database overwrite, terminal fallback removal, or launcher rollback breakage was performed.
- Recommended next stage: V2.5.19 Demo Flow Freeze after final live checks for SKU006, SKU007, unknown barcode, focus recovery, and restart recovery.

## 2026-06-08 V2.5.18c

- Updated `/api/scan` in `app.py` so success, duplicate, unknown, and empty scan paths all return stable JSON fields for QML feedback.
- Added `success`, `input`, `raw_code`, `product_id`, `product_name`, `error_reason`, `total_price_cent`, and `total_yuan` to scan responses.
- Changed unknown barcode feedback to `未录入商品：<raw>` and empty scan feedback to `扫码内容为空`.
- Updated `qt_kiosk/Main.qml` scanner feedback to distinguish `success`, `unknown`, `empty`, `duplicate`, and API error states.
- Added `recentScanStatus` to the QML scanner diagnostic panel so the user can tell whether QML received characters.
- Added `tools/scan_api_matrix_test.py` for SKU006-SKU010, unknown barcode, empty input, and field compatibility validation.
- Added `SCAN_API_MATRIX_TEST_REPORT.md`, `QML_SCANNER_FEEDBACK_FIX_REPORT.md`, `QML_UNKNOWN_BARCODE_FEEDBACK_REPORT.md`, `QML_SCANNER_HID_FIELD_TEST_CHECKLIST.md`, and `QML_V2518C_CHANGELOG.md`.
- Verified `SCAN_API_MATRIX_CHECKS=23 PASS=23 FAIL=0`.
- Verified `BUSINESS_API_CHECKS=41 PASS=41 FAIL=0 FINAL_TOTAL=¥0.00`.
- Verified `restore_default_weston.sh` and `start_retail_hdmi_qml.sh` still work, leaving the board in HDMI QML mode with `/api/state` HTTP 200.
- Current database note: `690000000001` is bound to SKU001 农夫山泉矿泉水 550ml, so unknown-barcode behavior is verified with `UNKNOWN_TEST_001`.
- No RKDevTool, Upgrade, EraseFlash, boot/rootfs/oem/uboot write, `/etc/init.d/S03weston` modification, autostart persistence, `/userdata/qt5` deletion, database overwrite, terminal fallback removal, or launcher rollback breakage was performed.

## 2026-06-08 V2.5.18b

- Added hidden QML scanner HID capture in `qt_kiosk/Main.qml` so keyboard-like scanner input can be collected without requiring the visible scan field to be clicked first.
- Added scanner buffer handling for printable characters, Backspace, Escape, Enter, and Return.
- Added shared `submitScan()` path for hidden scanner capture and manual SKU/barcode input.
- Added scanner focus recovery after refresh, capture, speech, cart, checkout, clear, and API callbacks.
- Added QML scanner diagnostic UI showing focus state, latest scan text, latest result, scan time, and error state.
- Updated `/api/scan` in `app.py` to accept `barcode`, `code`, `text`, or `product_id` fields for scanner/manual compatibility.
- Added `QML_SCANNER_INPUT_GATE_REPORT.md`, `QML_SCANNER_FOCUS_FIX_REPORT.md`, `QML_SCANNER_MANUAL_TEST_CHECKLIST.md`, `QML_SCANNER_HID_DIAGNOSTIC_LOG.md`, and `QML_V2518B_CHANGELOG.md`.
- Verified `/api/scan` accepts `barcode=SKU006`, `code=SKU006`, `text=SKU006`, and `product_id=SKU006`; each path can add 今麦郎纯净水 and return cart total `¥2.00`.
- Verified business API regression remains `41/41 PASS`, `/api/state` remains HTTP 200, and restore/start launcher round trip still works.
- Current board HID diagnostic shows a USB mouse but no obvious scanner/barcode HID device, so real scanner manual testing still requires plugging the scanner into the board USB Host port.
- No RKDevTool, Upgrade, EraseFlash, boot/rootfs/oem/uboot write, `/etc/init.d/S03weston` modification, autostart persistence, `/userdata/qt5` deletion, database overwrite, terminal fallback removal, or launcher rollback breakage was performed.

## 2026-06-08 V2.5.18

- Added `QML_CASHIER_UI_POLISH_REPORT.md`, `QML_CASHIER_UI_POLISH_CHANGELOG.md`, `QML_CASHIER_MANUAL_TEST_CHECKLIST.md`, `QML_CASHIER_LAYOUT_NOTES.md`, and `QML_CASHIER_NEXT_ACTIONS.md`.
- Reworked `qt_kiosk/Main.qml` into a clearer cashier layout with larger capture preview, clearer speech/intent/correction status, stronger quick product area, larger cart, and stronger scan/action flow.
- Reworked `HeaderBar.qml` to show terminal title, API status, payment status, and current time more clearly.
- Reworked `ActionButtons.qml` with larger touch targets: `刷新`, `拍照`, `语音`, `删除上一件`, `清空`, and `结账`.
- Reworked `ProductPanel.qml` so product cards show real product name, SKU, price, and a large `加入购物车` action area.
- Reworked `CartPanel.qml` with product/quantity/subtotal columns and a larger fixed total block.
- Reworked `StatusBar.qml` to emphasize the latest action result.
- Reworked `PaymentDialog.qml` to show order ID, amount, payment status, QR area, and payment link/path more clearly.
- Deployed only QML files after backing up board QML to `/userdata/smart_retail/qt_kiosk.v2518_bak_20260608_220338`.
- Verified QML restarts, `/api/state` remains HTTP 200, capture API still returns a valid JPEG, business API regression still passes, and restore/start launcher round trip still works.
- No RKDevTool, Upgrade, EraseFlash, boot/rootfs/oem/uboot write, `/etc/init.d/S03weston` modification, autostart persistence, `/userdata/qt5` deletion, or database overwrite was performed.

## 2026-06-08 V2.5.17b

- Added `tools/sync_real_products.py` to update only SKU006 through SKU010 in the existing products table.
- Backed up the board database to `/userdata/smart_retail/database/v2517b_backup_20260608_212935/retail_terminal.db` before product updates.
- Synced SKU006-SKU010 to real product data: 今麦郎纯净水, 舒肤佳沐浴露, 洁饶消毒剂, 大宝护肤霜, and Pantene护发素.
- Updated `app.py` product seed entries for SKU006-SKU010 so future initialization matches the real product set.
- Updated `/api/capture` to return `image_file_url` in addition to `image_url`, `image_path`, latency, and message.
- Updated `/api/state` to return `latest_capture_path`, `latest_capture_file_url`, and `latest_capture_success`.
- Updated `qt_kiosk/Main.qml` to maintain explicit capture preview state and prefer local `file://` capture images for the left preview.
- Updated `API_CONTRACT.md` for V2.5.17b capture preview fields.
- Added `QML_CAPTURE_PREVIEW_FIX_REPORT.md`, `QML_PRODUCT_DATA_SYNC_REPORT.md`, `QML_CAPTURE_PREVIEW_TEST_LOG.md`, `QML_V2517B_MANUAL_TEST_CHECKLIST.md`, and `QML_V2517B_CHANGELOG.md`.
- Verified capture creates a JPEG, HTTP image URL returns JPEG bytes, `/api/state` exposes complete capture fields, business API regression passes, and restore/start launcher round trip still works.
- No RKDevTool, Upgrade, EraseFlash, boot/rootfs/oem/uboot write, `/etc/init.d/S03weston` modification, autostart persistence, `/userdata/qt5` deletion, or database overwrite was performed.

## 2026-06-08 V2.5.17

- Added `QML_FUNCTIONAL_UI_FIX_REPORT.md`, `QML_CAPTURE_API_TEST_REPORT.md`, `QML_CHINESE_LOCALIZATION_REPORT.md`, `QML_QUICK_PRODUCTS_FIX_REPORT.md`, `QML_MANUAL_HDMI_TEST_CHECKLIST.md`, and `QML_FUNCTIONAL_UI_CHANGELOG.md`.
- Updated `app.py` so `/api/state` returns `quick_products`, `price_yuan`, `latest_capture_url`, and `latest_capture_latency_ms`.
- Updated `/api/capture` response to include `image_url` and a Chinese success message with capture path and latency.
- Reworked `qt_kiosk/Main.qml` to rebuild explicit `ListModel` objects for quick products and cart lines, avoiding fragile raw JSON array view binding.
- Localized visible QML cashier UI text to Chinese and loaded `NotoSansSC-VF.ttf` from `/userdata/qt5/share/fonts`.
- Enlarged quick product tiles, cart rows, total area, scan input, bottom action buttons, status bar text, and payment dialog text for HDMI readability.
- Updated QML components: `ActionButtons.qml`, `CartPanel.qml`, `HeaderBar.qml`, `PaymentDialog.qml`, `ProductPanel.qml`, and `StatusBar.qml`.
- Updated `API_CONTRACT.md` for V2.5.17 quick product and capture fields.
- Deployed only app-layer files to `/userdata/smart_retail` after backing up `app.py` and `qt_kiosk`; no database overwrite was performed.
- Verified `quick_products` returns SKU006 through SKU010, `/api/capture` succeeds, V2.5.16 business API tests still pass, and restore/start launcher round trip still works.
- No RKDevTool, Upgrade, EraseFlash, boot/rootfs/oem/uboot write, `/etc/init.d/S03weston` modification, autostart persistence, or `/userdata/qt5` deletion was performed.

## 2026-06-08 V2.5.16

- Added `tools/qml_business_api_test.py` for board-side API-path validation of QML cashier business flows.
- Added `QML_BUSINESS_TEST_REPORT.md`, `QML_BUSINESS_TEST_LOG_SUMMARY.md`, `QML_API_FIELD_MAPPING.md`, `QML_BUGFIX_CHANGELOG.md`, and `QML_BUSINESS_NEXT_ACTIONS.md`.
- Updated `API_CONTRACT.md` to document that `/api/scan` accepts a barcode or an active product ID in the `barcode` field.
- Verified current board state before testing: Flask, HDMI-primary Weston, and `qmlscene Main.qml` were running; `/api/state` returned HTTP 200; cart started empty.
- Verified SKU006/SKU007 add, barcode scan, remove last, remove product, clear cart, empty-cart checkout protection, non-empty checkout/order lookup, and speech command correction paths.
- Fixed `/api/scan` so the QML scan input can accept a product ID such as `SKU006` as well as a barcode.
- Deployed only `app.py` to `/userdata/smart_retail/app.py` after backing up the board copy to `/userdata/smart_retail/app.py.v2516_bak_20260608_203328`.
- Confirmed `restore_default_weston.sh` and `start_retail_hdmi_qml.sh` still work after the application patch, leaving the board back in HDMI QML kiosk mode.
- No RKDevTool, Upgrade, EraseFlash, boot/rootfs/oem/uboot write, database overwrite, `/etc/init.d/S03weston` modification, or autostart persistence was performed.

## 2026-06-08 V2.5.15

- Added `start_retail_hdmi_qml.sh` as a reversible `/userdata` launcher for HDMI-primary Weston plus QML Main.qml.
- Added `restore_default_weston.sh` to stop the QML/userdata Weston session and restore default Weston through `/etc/init.d/S03weston start`.
- Updated `start_retail_kiosk.sh` to delegate to `/userdata/start_retail_hdmi_qml.sh` when `/userdata/qt5/bin/qmlscene` exists, while preserving the terminal kiosk fallback.
- Deployed launcher scripts to `/userdata/start_retail_hdmi_qml.sh` and `/userdata/restore_default_weston.sh`.
- Confirmed `sh /userdata/start_retail_hdmi_qml.sh` starts Flask, HDMI-primary Weston, and `/userdata/qt5/bin/qmlscene /userdata/smart_retail/qt_kiosk/Main.qml`.
- Confirmed `sh /userdata/restore_default_weston.sh` restores default Weston and leaves Flask/API running.
- Confirmed a second `sh /userdata/start_retail_hdmi_qml.sh` re-enters HDMI QML kiosk successfully.
- Added `USERDATA_HDMI_QML_LAUNCHER_REPORT.md`, `USERDATA_HDMI_QML_LAUNCHER_LOG_SUMMARY.md`, `USERDATA_HDMI_QML_ROLLBACK_GUIDE.md`, and `USERDATA_HDMI_QML_TEST_CHECKLIST.md`.
- No RKDevTool, Upgrade, EraseFlash, boot/rootfs/oem/uboot write, database overwrite, `/etc/init.d/S03weston` modification, or autostart persistence was performed.

## 2026-06-08 V2.5.14c

- Added `WESTON_HDMI_OUTPUT_SELECTION_REPORT.md` documenting the temporary HDMI-primary Weston test.
- Added `WESTON_HDMI_TEST_LOGS_SUMMARY.md` summarizing Weston, red QML, Main.qml, DRM, and API evidence.
- Added `WESTON_HDMI_NEXT_PERSISTENCE_PLAN.md` with the safe route toward a later persistence/autostart gate.
- Created temporary board files under `/userdata/qt5`: `weston-hdmi-primary.ini`, `weston-hdmi-primary-layout.ini`, `VISIBLE_RED.qml`, and `start_weston_hdmi_test.sh`.
- Confirmed plain background Weston can exit after ADB shell return; `nohup weston --config=/userdata/qt5/weston-hdmi-primary.ini` keeps the compositor alive.
- Confirmed temporary Weston exposes only `HDMI-A-1` at logical `0,0 2560x1440`.
- Confirmed red QML test reports `screen 0 HDMI-A-1 2560 1440` and renders as `geometry=0,0 2560x1440`.
- Confirmed `qt_kiosk/Main.qml` runs as `QSM368ZP-WF Retail Kiosk` with `geometry=0,0 2560x1440` under the HDMI-primary Weston session.
- Left the board in the temporary working state: HDMI-primary Weston, Flask, and Main.qml running.
- No RKDevTool, Upgrade, EraseFlash, boot/rootfs/oem/uboot write, database overwrite, or autostart persistence was performed.

## 2026-06-08 V2.5.14b

- Added `QML_VISIBILITY_GATE_REPORT.md` for the QML foreground/HDMI visibility diagnosis.
- Confirmed `qmlscene` process and Flask `/api/state` health are not sufficient proof of HDMI visibility.
- Created `/userdata/qt5/VISIBLE_RED.qml` and launched it through `/userdata/qt5/bin/qmlscene`.
- Confirmed the red QML test renders through Qt Wayland-EGL and Mali-G52, but Weston configures it as `800x1280` at logical `0,0`.
- Collected Weston, DRM, and `weston-info` diagnostics under `/userdata/qt5/visibility_diag`.
- Confirmed both outputs are active: `LVDS-1` at logical `0,0 800x1280` and `HDMI-A-1` at logical `800,0 2560x1440`.
- Created `/userdata/qt5/VISIBLE_HDMI.qml` to target `Qt.application.screens[1]`; Qt selected `HDMI-A-1`, but Weston still configured the surface as `800x1280`.
- Classified the current blocker as a multi-output HDMI/LVDS output-selection issue, not a Qt runtime, QML import, or Flask API failure.
- No RKDevTool, Upgrade, EraseFlash, boot/rootfs/oem/uboot write, or database overwrite was performed.

## 2026-06-08 V2.5.14

- Added `QT_CJK_FONT_RUNTIME_REPORT.md` documenting the CJK font runtime gate.
- Added `QT_CJK_FONT_DEPLOY_LOG.md` with font source, board deployment, fontconfig, and QML validation results.
- Added `QT_KIOSK_START_SCRIPT_UPDATE.md` documenting startup script changes and board verification.
- Updated `start_retail_kiosk.sh` to prefer `/userdata/qt5/bin/qmlscene`, then `/userdata/qt5/bin/qml`, before falling back to system Qt or the terminal kiosk.
- Updated `start_retail_kiosk.sh` to source `/userdata/qt5/qt5-env.sh` when present and to detect Flask through `/proc/*/cmdline`.
- Deployed local CJK font `C:\Windows\Fonts\NotoSansSC-VF.ttf` only to `/userdata/qt5/share/fonts`; the font file was not added to the repository.
- Added `/userdata/qt5/etc/fonts/local.conf` and updated `/userdata/qt5/qt5-env.sh` so fontconfig and Qt can resolve `/userdata/qt5/share/fonts`.
- Confirmed `fc-cache` succeeds and `fc-match 'sans-serif:lang=zh-cn'` resolves to `NotoSansSC-VF.ttf`.
- Confirmed CJK QML test launches through Qt Wayland-EGL with full-screen `800x1280` configure.
- Confirmed `/userdata/start_retail_kiosk.sh` starts QML through `/userdata/qt5/bin/qmlscene` and no longer goes to terminal fallback when userdata Qt exists.
- Noted that automatic HDMI screenshot capture is blocked because `weston-screenshooter` requires Weston debug screenshooter protocol.
- No RKDevTool, Upgrade, EraseFlash, boot/rootfs/oem/uboot write, or database overwrite was performed.

## 2026-06-08 V2.5.13

- Added `QT_USERDATA_RUNTIME_DEPLOY_V2513_REPORT.md` for the board-side `/userdata/qt5` runtime deployment gate.
- Downloaded `qt5-runtime-rk3568-aarch64-glibc235.tar.gz` locally and verified sha256 `6bfe9cfaba13ab95f018f0edc00cf8c4c003ffde7624c541d1413ed0742dc543`.
- Backed up `/userdata/smart_retail` to `C:\Users\MR\Desktop\Vibecoder\backup_before_v2513_qt_runtime_20260608_181508\smart_retail`.
- Deployed the Qt runtime only under `/userdata/qt5`; no boot/rootfs/oem/uboot partition was written.
- Worked around BusyBox tar gzip limitations by extracting with `gzip -dc ... | tar -xf -`.
- Confirmed `/userdata/qt5/bin/qmlscene`, QtQuick, QtQuick Controls 2, and the Wayland EGL platform plugin are present on the board.
- Confirmed `qmlscene` dependency closure with `/lib/ld-linux-aarch64.so.1 --list`.
- Confirmed English `HELLO_QTQUICK.qml` renders through Qt Wayland-EGL under Weston.
- Confirmed Flask `/api/state` responds and `qt_kiosk/Main.qml` launches with persistent `qmlscene`.
- Remaining next-gate item: add or verify CJK fonts for Chinese text rendering.
- No RKDevTool, Upgrade, EraseFlash, or boot/rootfs/oem/uboot writes were performed.

## 2026-06-08 V2.5.12b

- Added `CLOUD_QT_SOURCE_CACHE_REPAIR_REPORT.md` documenting the libpng source-cache repair.
- Added `CLOUD_QT_LIBPNG_DOWNLOAD_FIX_LOG.md` with the exact libpng mirror/hash/cache result.
- Added `CLOUD_QT_SDK_SYMLINK_HEALTH.md` documenting repaired SDK symlink flattening issues.
- Added `CLOUD_QT_PACKAGE_ONLY_RESUME_REPORT.md` summarizing the successful cloud package-only Qt build resume.
- Added `CLOUD_QT_RUNTIME_BUILD_NEXT_DECISION.md` defining the next `/userdata/qt5` deploy gate and route risks.
- Updated `CLOUD_QT_RUNTIME_PACKAGE_FILELIST.txt` with the actual extracted runtime file list.
- Confirmed cloud package-only Qt build completed for `qt5base`, `qt5declarative`, `qt5quickcontrols2`, and `qt5wayland`.
- Generated `/root/qt5-runtime-rk3568-aarch64-glibc235.tar.gz` on the cloud host, size `40M`, unpacked runtime `114M`, sha256 `6bfe9cfaba13ab95f018f0edc00cf8c4c003ffde7624c541d1413ed0742dc543`.
- Confirmed runtime contains `qml`, `qmlscene`, QtQuick, QtQuick Controls 2, and the Wayland EGL platform plugin.
- Noted remaining next-gate risk: fontconfig exists but no actual font files were found in the extracted runtime.
- No ADB, board deployment, RKDevTool, Upgrade, EraseFlash, or boot/rootfs/oem/uboot writes were performed.

## 2026-06-08 V2.5.12

- Added `CLOUD_QT_RUNTIME_BUILD_ATTEMPT_REPORT.md` for the DigitalOcean package-only Qt runtime build attempt.
- Added `CLOUD_QT_RUNTIME_BUILD_LOG_SUMMARY.md` with the observed Buildroot stages and failure boundaries.
- Added `CLOUD_QT_RUNTIME_PACKAGE_FILELIST.txt` marking the runtime package as not generated.
- Added `CLOUD_QT_RUNTIME_SIZE_REPORT.md` with cloud output size and `/userdata` size-risk status.
- Added `CLOUD_QT_RUNTIME_NEXT_DEPLOY_GATE.md` defining the conditions required before any `/userdata/qt5` deployment.
- Confirmed package-only `qt5base` builds the internal toolchain/sysroot first and reached user-space dependencies, but stopped before Qt artifacts.
- Confirmed the final blocker was source download availability for `libpng-1.6.37`; earlier blockers included `expat` download, lost symlink semantics from Windows SDK staging, and root-build DBus group handling.
- No runtime tarball was generated; no ADB, board deploy, RKDevTool, Upgrade, EraseFlash, or boot/rootfs/oem/uboot writes were performed.

## 2026-06-08 V2.5.11

- Added `CLOUD_QT_BUILD_ENV_REPORT.md` for the DigitalOcean Ubuntu build-environment gate.
- Added `CLOUD_SDK_UPLOAD_PLAN.md` documenting SDK upload to `/root/qsm_sdk`.
- Added `CLOUD_QT_BUILD_PRECHECK.md` confirming RK3568/Qt Buildroot files on the cloud SDK copy.
- Added `CLOUD_QT_NEXT_BUILD_COMMANDS.md` with V2.5.12 package-only build command drafts.
- Prepared the cloud server with Buildroot dependencies and a temporary 16GB swapfile.
- Uploaded and extracted the SDK to the Linux filesystem on the cloud server.
- Did not run Buildroot make, ADB, RKDevTool, Upgrade, EraseFlash, or any board deployment.

## 2026-06-08 V2.5.10

- Added `QT_RUNTIME_BUILD_ATTEMPT_REPORT.md` for the Qt runtime build-attempt gate result.
- Added `QT_RUNTIME_BUILD_LOG_SUMMARY.md` summarizing the environment checks and skipped build stages.
- Added `QT_RUNTIME_PACKAGE_FILELIST.txt` as a not-generated status manifest with the expected future runtime contents.
- Added `QT_RUNTIME_DEPENDENCY_CHECK_PLAN.md` for host-side and future board-side dependency checks.
- Added `QT_RUNTIME_DEPLOY_NEXT_GATE.md` defining the conditions required before any `/userdata/qt5` deployment.
- Confirmed no usable Ubuntu/native Linux Buildroot environment is currently available; build stopped at the environment stage with no ADB, no deploy, no flash, and no board writes.

## 2026-06-08 V2.5.9

- Added `QT_BUILD_DRY_RUN_REPORT.md` for SDK build entrypoint and RK3568 Buildroot dry-run analysis.
- Added `QT_BUILD_COMMAND_PLAN.md` with Linux/WSL2 build command drafts for a Qt Quick/QML runtime.
- Added `QT_RUNTIME_EXTRACT_SCRIPT_DRAFT.sh` as a host-side `/userdata/qt5` extraction draft from Buildroot `output/target`.
- Added `QT_RUNTIME_MINIMAL_COMPONENTS.md` documenting the minimum Qt Quick/QML modules, plugins, imports, fonts, and dependency checks.
- Added `QT_RUNTIME_SIZE_RISK.md` for runtime size bands, build risks, deployment risks, and rollback strategy.
- Confirmed this gate remains analysis-only: no ADB, no deploy, no RKDevTool, no Upgrade/EraseFlash, no boot/rootfs/oem/uboot writes.

## 2026-06-08 V2.5.8

- Added `QT_RUNTIME_ACQUISITION_REPORT.md` for read-only SDK/Buildroot Qt runtime acquisition analysis.
- Added `QT_USERDATA_RUNTIME_DEPLOY_PLAN.md` for a future reversible `/userdata/qt5` Qt Quick/QML runtime trial.
- Added `QT_RUNTIME_FILELIST_EXPECTED.txt` with the expected minimal Qt Quick/QML runtime manifest.
- Confirmed the local SDK contains Qt5 Buildroot configs/packages and aarch64 cross toolchains, but no generated `buildroot/output/target` runtime artifacts yet.
- Kept this gate analysis-only: no ADB deployment, no flashing, no rootfs/boot/oem/uboot writes.

## 2026-06-08 V2.5.7

- Added `tools/qt_runtime_probe_full.ps1` for read-only ABI, libc, Wayland, Weston, DRM/GPU, font, input, and storage collection.
- Added `tools/local_official_package_scan.ps1` for local SDK/rootfs/Buildroot/Qt clue scanning.
- Added `qt_runtime_probe_report.md` summarizing the current board ABI and Qt runtime gap.
- Added `official_question_qt_runtime.md` for official/teacher support questions.
- Added `qt_userdata_runtime_plan.md` for a reversible `/userdata/qt5` runtime trial.
- Confirmed current board is aarch64 glibc 2.35 with Weston/Wayland/EGL/GLES available, but no Qt/QML runtime.

## 2026-06-08 V2.5.6

- Added `terminal_kiosk.py` as a Weston terminal cashier fallback for images without Qt/QML runtime.
- Updated `start_retail_kiosk.sh` so missing `qmlscene/qml` starts `weston-terminal --fullscreen` running `terminal_kiosk.py` instead of stopping at a static message.
- Updated `deploy_qt_kiosk_via_adb.ps1` to back up `/userdata/smart_retail` before deployment.
- Updated deployment to preserve an existing board SQLite database and push the seed database only when the remote database is missing.
- Added `README_TERMINAL_KIOSK.md`.

## 2026-06-08

- Added `/api/state`, `/api/scan`, `/api/cart/*`, `/api/checkout`, `/api/order/<order_id>`, `/api/capture`, `/api/speech/*`, and `/api/metrics` to `app.py`.
- Added speech confirmation gating for API calls so `checkout` and `clear_cart` require explicit confirmation before execution.
- Added `tools/api_smoke_test.py` for desktop or board API validation.
- Added `tools/probe_qt_env.ps1` for read-only Qt/Wayland runtime inspection through ADB.
- Added Qt/QML kiosk frontend under `qt_kiosk/`.
- Reworked `start_retail_kiosk.sh` to start Flask first, then launch QML on Wayland when `qmlscene` or `qml` exists.
- Added `deploy_qt_kiosk_via_adb.ps1` for application-only deployment to `/userdata/smart_retail`.
- Added API and kiosk documentation.
# 2026-06-10 V2.6.9-B

- Added payment QR accessibility fields: `payment_mode`, `payment_accessibility`, and `qr_user_message`.
- Updated checkout/order/QR regenerate responses so `local_debug` is explicitly marked as phone-inaccessible.
- Added `/api/cloud/status` fields for cloud health, cloud base URL, and last check timestamp.
- Updated QML PaymentDialog to show cloud/LAN/local-debug mode, QR image, payment link, and local-debug warning.
- Exposed numeric voice command menu through `/api/state` as `voice_menu_items` and `voice_menu_prompt`.
- Added tests for payment QR accessibility, cloud mode selection, QML voice menu state, and speech error feedback.
- Regression results: payment accessibility 8/8 PASS, cloud mode 2/2 PASS, voice menu 3/3 PASS, speech error 4/4 PASS, audio event 24/24 PASS, capture stress 12/12 PASS, RKNN smoke PASS.
- Current release decision: automated PASS, Release Freeze held until HDMI visual confirmation because the board reported HDMI disconnected during this run.

# 2026-06-10 V2.6.10

- Added phone-first payment fields `phone_demo_ready` and `phone_demo_status`.
- Added `POST /api/order/<order_id>/promote_cloud` for upgrading an existing unpaid local order to a cloud payment order after network recovery.
- Rewrote QML `PaymentDialog.qml` to clearly show cloud/LAN/local-debug mode, phone accessibility, QR content, cloud check, and cloud promotion.
- Added numbered voice phrase parser for commands such as `小售小售四号结账`.
- Added conflict handling: operation phrase wins over mismatched number and returns `conflict_warning=true`.
- Updated voice menu prompt to numbered phrase wording: `1号查询总价` through `0号取消`.
- Added tests: `payment_phone_first_cloud_test.py`, `speech_numbered_phrase_test.py`, and `speech_guard_background_worker_test.py`.
- Regression: phone-first payment 6/6 PASS, numbered phrase 10/10 PASS, speech guard worker 7/7 PASS, audio event 24/24 PASS, 10-SKU scan 43/43 PASS, RKNN CLI PASS.
- Release Freeze remains held until cloud network is restored for a true phone-scannable cloud payment demo, or the final demo explicitly presents local debug as offline fallback.

# 2026-06-10 V2.6.10-A

- Ran final cloud phone payment retest as a network-only gate with no application code changes.
- Confirmed Windows host can reach the cloud payment health endpoint and can ping the board at `192.168.137.191`.
- Confirmed board app, Weston HDMI QML, and RKNN CLI backend remain running; HDMI reports connected.
- Confirmed board eth0 is `192.168.137.191/24` with default route via `192.168.137.1`.
- Board cannot ping the Windows gateway and cannot reach the configured cloud `/health`; `/api/cloud/status` reports `cloud_health_ok=false`.
- `payment_phone_first_cloud_test.py` remains 6/6 PASS for LAN/local fallback and clear cloud-offline behavior; `rknn_cli_smoke_test.py` remains PASS.
- Minimal regression observations: `scan_api_matrix_test.py` 36/39 PASS and `qml_business_api_test.py` 39/41 PASS; review before final freeze.
- Decision: V2.6.10-A PARTIAL PASS, Release Freeze HOLD until Windows ICS/NAT is restored and board cloud paid writeback is retested.

# 2026-06-10 V2.6.10-B

- Re-ran `tools/enable_windows_ics_wlan_to_realtek.ps1` from an elevated PowerShell.
- Confirmed ICS sharing: WLAN public, Realtek private, Realtek `192.168.137.1`, SharedAccess running.
- Reapplied board eth0 route: `192.168.137.191/24`, default via `192.168.137.1`.
- Board `/health` returned HTTP 200; cloud health blocker resolved for that test session.
- `cloud_payment_probe.py --create-test-order` passed cloud status and cloud test order creation.
- Real checkout cloud order `ORDER20260610093929608` / `CLOUD2026061009392945A872` was paid through the cloud payment page.
- Board synced `payment_status=paid`, `cloud_status=paid`, and played `payment_success`.
- Sequential final regression: phone-first cloud payment 7/7 PASS, scan API matrix 39/39 PASS, QML business 41/41 PASS, RKNN CLI PASS.
- Decision: V2.6.10-B PASS, Release Freeze READY for V2.6.11.

# 2026-06-10 V2.6.11

- Created `release_v2611/` as the final release evidence package directory.
- Pulled deployed board artifacts from `/userdata/smart_retail`: `app.py`, QML kiosk, audio prompts, product images, tools, RKNN model, ONNX fallback artifacts, RKNN CLI bridge, API docs, changelog, and SQLite database backups.
- Captured final board state into `release_v2611/evidence/logs/board_final_state.txt`.
- Ran final sequential regression: payment phone-first cloud 7/7 PASS, 10-SKU scan 43/43 PASS, scan API matrix 39/39 PASS, QML business 41/41 PASS, input arbitration PASS, capture stress PASS, audio event matrix PASS, vision tests PASS, RKNN CLI PASS, speech guard/numeric safety tests PASS, payment QR accessibility 8/8 PASS.
- Added final release documents: `RELEASE_README.md`, `RELEASE_FREEZE_REPORT.md`, `FINAL_SYSTEM_STATUS.md`, `FINAL_TEST_RESULTS.md`, `FINAL_EVIDENCE_MANIFEST.md`, and `FINAL_JUDGE_QA.md`.
- Release scope remains evidence/package only: no flashing, no RKDevTool, no boot/rootfs/oem/uboot writes, no autostart, no database overwrite, no cloud server code changes, and no new features.
- Decision: V2.6.11 Release Freeze PASS.
# V2.6.11-A Field Hotfix - 2026-06-10

- Added cloud `GET/POST /pay/<cloud_order_id>/success` paid route.
- Updated cloud pay page to use explicit pure HTML form action and large submit button.
- Added cloud pay success page with order id, amount, and paid time.
- Added backup success link for mobile browsers.
- Hardened voice parser around full numbered phrases.
- Added `recommended_phrase` and `button_phrase` to voice menu payload.
- Updated QML voice menu to show full phrases instead of short digit-only prompts.
- Added `tools/speech_numbered_phrase_hotfix_test.py`.
- Added `tools/cloud_pay_button_hotfix_test.py`.
- Verified:
  - `CLOUD_PAY_BUTTON_HOTFIX_CHECKS=8 PASS=8 FAIL=0`
  - `SPEECH_NUMBERED_PHRASE_HOTFIX_CHECKS=15 PASS=15 FAIL=0`
  - `PAYMENT_PHONE_FIRST_CLOUD_CHECKS=7 PASS=7 FAIL=0`
  - `SCAN_API_MATRIX_CHECKS=39 PASS=39 FAIL=0`
  - `QML_BUSINESS_CHECKS=41 PASS=41 FAIL=0`
  - `AUDIO_EVENT_MATRIX_CHECKS=24 PASS=24 FAIL=0`
  - RKNN CLI smoke PASS

# V2.6.11-E QML Layout Polish Hotfix - 2026-06-10

- Fixed the RKNN/vision reference-score display by splitting long vision status text into separate conclusion, reference-score, and latency fields.
- Added fixed-width non-eliding score badges in `qt_kiosk/Main.qml` so `参考分` remains visible on HDMI.
- Updated Top-3 vision text to wrap instead of compressing the score row.
- Reworked `qt_kiosk/components/ProductPanel.qml` into a compact 5 x 2 grid so all 10 quick products fit on one screen without scrolling.
- Kept full product names in API/database while using short card labels for long names on the kiosk panel.
- Synced `dataset_raw_v260/manifest.csv` test metadata prices to the current deployed 10-SKU database prices; no database rows were changed.
- Verified:
  - `V260_SCAN_10SKU_CHECKS=43 PASS=43 FAIL=0`
  - `SCAN_API_MATRIX_CHECKS=39 PASS=39 FAIL=0`
  - `QML_BUSINESS_CHECKS=45 PASS=45 FAIL=0`
  - `VISION_MODEL_STATUS_CHECKS=6 PASS=6 FAIL=0`
  - `VISION_NO_REPEAT_ADD_CHECKS=3 PASS=3 FAIL=0`
  - `PAYMENT_PHONE_FIRST_CLOUD_CHECKS=7 PASS=7 FAIL=0`
  - `AUDIO_EVENT_MATRIX_CHECKS=24 PASS=24 FAIL=0`
  - RKNN CLI smoke PASS
- Decision: automated PASS; final HDMI human glance still recommended to confirm the product grid and score badge appearance.

# V2.6.11-F Vision Score Empty Text Micro Hotfix - 2026-06-10

- Fixed QML empty vision score text in `qt_kiosk/Main.qml`.
- Invalid or missing confidence values now display `视觉参考` instead of `参考分：-`.
- Valid confidence values still display `参考分：xx%`.
- No backend fields, database rows, RKNN runtime, cloud payment, or business logic were changed.
- Board backup before patch: `/userdata/smart_retail/backups/v2611f_before_score_text_20260610_141513`.
- Verified:
  - QML launcher restart PASS, HDMI connected during restart.
  - RKNN CLI smoke PASS.
  - `QML_BUSINESS_CHECKS=45 PASS=45 FAIL=0`.
- Decision: V2.6.11-F automated PASS; final HDMI visual glance recommended for the empty-score text.

# V2.6.11-G Responsive HDMI Layout Hotfix - 2026-06-14

- Added responsive layout variables to `qt_kiosk/Main.qml` for 1920x1080 and larger HDMI displays.
- Rebalanced the main body so the right cart panel has a protected responsive width and no longer depends on the previous large-display geometry.
- Compressed recognition, capture, vision, speech, scanner, input, action, and status areas in compact HDMI mode.
- Rewrote `ProductPanel.qml` as a compact responsive 5 x 2 10-SKU grid with no normal 1080p scrolling requirement.
- Rewrote `CartPanel.qml` with compact margins, row heights, internal cart scrolling, and a protected bottom total bar.
- Added compact sizing to `HeaderBar.qml`, `PersistentVoiceHintBar.qml`, `ActionButtons.qml`, `StatusBar.qml`, and `PaymentDialog.qml`.
- Updated payment dialog QR/text/button sizing for 1920x1080.
- No Flask business logic, database, RKNN runtime, cloud server, boot/rootfs, or autostart behavior was changed.
- Board backup before patch: `/userdata/smart_retail/backups/v2611g_before_responsive_layout_20000101_071836`.
- Verified:
  - QML launcher restart PASS; HDMI connected.
  - `QML_BUSINESS_CHECKS=45 PASS=45 FAIL=0`
  - `SCAN_API_MATRIX_CHECKS=39 PASS=39 FAIL=0`
  - `PAYMENT_PHONE_FIRST_CLOUD_CHECKS=6 PASS=6 FAIL=0` in local_debug fallback because board cloud route is unavailable.
  - RKNN CLI smoke PASS.
  - `AUDIO_EVENT_MATRIX_CHECKS=24 PASS=24 FAIL=0`
- Decision: automated PASS; final HDMI human visual confirmation required for the new monitor.

# 2026-09-22 毕昇杯初赛修订与未知条码新图流程

- Added the five-chapter preliminary paper deliverable under `docs/competition/deliverables/`.
- Standardized the registered title, four member names and instructor in the paper; removed unverified team labels and private contact details.
- Added `capture=true` semantics to the unknown-barcode vision candidate flow. A fresh capture is required, old preview images are not reused after capture failure, and the candidate path never auto-adds to the cart.
- Added isolated regression tools `tools/test_unknown_barcode_capture.py` and `tools/test_unknown_barcode_qml.js`.
- Verified local logic tests: Python 12/12 PASS and Node/QML branch test PASS. These tests use isolated data and doubles; no ADB deployment or live board claim is made.
- Added the competition revision, field acceptance, BOM and evidence checklists.

# 2026-09-22 板端拍照冷却时钟回拨修复

- Fixed capture cooldown handling when the board RTC is earlier than the persisted last-capture timestamp after reboot.
- A future timestamp is now treated as clock skew instead of an active cooldown; normal `0 <= elapsed < cooldown` protection remains unchanged.
- Added a regression test for the future-timestamp case. Local isolated regression is now `13/13 PASS`.
- Deployed only `app.py` to the board after backing up the application, QML files and database. No database rows were cleared or overwritten.
- Board validation: `/api/capture` returned `ok=true` with a fresh JPEG; `POST /api/vision/candidates {"capture":true}` returned a fresh capture, `backend=rknn_cli`, and `auto_add_cart=false`; cart remained unchanged.
- Board field limitations at this check: scanner and HyperX USB devices were not enumerated, Ethernet had `NO-CARRIER`, and board system time remained `2000-01-01`.

# 2026-09-22 板端潜在问题审计与音频状态诚实化

- Added `audio_device_available()` and an early ALSA card check before asynchronous `aplay` starts. A missing configured card now reports `audio_ok=false` and `audio device unavailable` without failing the main business action.
- Added `tools/test_audio_device_guard.py` covering named cards, numeric cards, missing cards and host environments without `/proc/asound`.
- Restarted the running Flask process after deployment so the board loaded the new Python code; Weston, QML, database and launcher configuration were preserved.
- Board validation: audio event matrix `24/24 PASS`, including the missing-device negative case; capture preview stability `5/5 PASS`; RKNN CLI smoke `PASS`; unknown barcode returned a stable JSON error and did not change the cart.
- Current board evidence: HDMI `connected`, HyperX Cloud III enumerated as ALSA card `2 [III]`, `active_backend=rknn_cli`, `/userdata` approximately 251 MB free.
- Remaining field conditions are explicit rather than masked: board RTC is `2000-01-01`, `eth0` is `NO-CARRIER` until the network cable is connected, and scanner HID must be checked with the scanner physically attached. No database overwrite, flashing, RKDevTool, boot/rootfs write or autostart change was performed.
