# Qt Kiosk JSON API Contract

Backend remains Flask + SQLite. The Qt/QML kiosk must call only these HTTP APIs and must not access SQLite or shell commands directly.

Base URL on the board:

```text
http://127.0.0.1:5000
```

## GET /api/state

Returns terminal state for the full-screen cashier UI.

Response:

```json
{
  "ok": true,
  "terminal_id": "QSM368ZP-WF-001",
  "time": "2026-06-08 10:30:00",
  "cart": {
    "items": [],
    "count": 0,
    "line_count": 0,
    "total_cent": 0,
    "total_text": "0.00"
  },
  "products": [],
  "quick_products": [],
  "latest_capture": "",
  "latest_capture_url": "",
  "latest_capture_file_url": "",
  "latest_capture_path": "",
  "latest_capture_latency_ms": 0,
  "latest_capture_success": false,
  "latest_speech_text": "",
  "latest_speech_parsed": {},
  "latest_vision": {},
  "latest_order": {},
  "audio": {
    "output_device": "plughw:CARD=III,DEV=0",
    "input_device": "plughw:CARD=III,DEV=0"
  },
  "metrics": {}
}
```

V2.5.17 adds `quick_products` for the QML quick product grid. It contains
SKU006 through SKU010 when those products are active. Product objects include
`product_id`, `product_name`, `short_name`, `price_cent`, `price_yuan`, and
`price_text`.

V2.5.17b adds full capture preview fields:

- `latest_capture`: relative static path such as `captures/xxx.jpg`
- `latest_capture_url`: full HTTP URL
- `latest_capture_file_url`: local `file://` URL for QML preview
- `latest_capture_path`: absolute board path
- `latest_capture_latency_ms`: capture latency
- `latest_capture_success`: boolean capture result flag

V2.6.7 adds wake-word numeric voice-session fields:

- `voice_mode`: `idle`, `command_listening`, `command_executing`, `timeout`, `failed`, or `cancelled`
- `voice_menu`: current numeric menu payload
- `voice_prompt`: current operator prompt
- `latest_voice_session_raw_text`: latest recognized wake/command text
- `latest_voice_session_digit`: normalized digit, if any
- `latest_voice_session_intent`: normalized action intent
- `latest_voice_session_message`: user-facing session message
- `latest_voice_session_action_result`: last action payload

Voice recording in QML should use the wake/numeric session by default. The
legacy free-text command endpoint remains available for manual typed testing.

V2.6.11-B adds payment paid UI sync fields for QML:

- `latest_order.payment_status`: `unpaid` or `paid`
- `latest_order.order_status`: order lifecycle status
- `latest_order.cloud_status`: cloud order status when a cloud order exists
- `latest_order.cloud_paid_at`: cloud paid timestamp
- `latest_order.last_sync_at`: latest cloud sync timestamp
- `latest_order.last_sync_status`: latest synced cloud status
- `latest_order.message`: user-facing payment message such as `等待支付确认` or `支付成功`
- `audio.latest_event`: expected to become `payment_success` after paid sync

## POST /api/order/<order_id>/sync_cloud

Synchronize one local order with the cloud payment service. QML payment dialogs
call this while waiting for the phone/cloud payment result.

Request body:

```json
{}
```

Paid response:

```json
{
  "ok": true,
  "success": true,
  "updated": true,
  "status": "paid",
  "cloud_status": "paid",
  "message": "支付成功",
  "cloud": {},
  "order": {
    "order_id": "ORDER...",
    "payment_status": "paid",
    "order_status": "paid",
    "cloud_status": "paid",
    "paid_at": "2026-06-10 11:00:26",
    "last_sync_at": "2026-06-10 11:00:28",
    "last_sync_status": "paid"
  },
  "latest_order": {},
  "audio_event": "payment_success",
  "audio_ok": true
}
```

Cloud unreachable response remains JSON and must not crash the caller:

```json
{
  "ok": false,
  "success": false,
  "error_reason": "cloud_unreachable",
  "message": "云端暂不可达，稍后自动重试",
  "order": {}
}
```

## POST /api/payment/sync_latest

Synchronize the latest local order with the cloud payment service. The latest
order is selected deterministically by `created_at DESC, rowid DESC`.

Response shape matches `/api/order/<order_id>/sync_cloud`.

## GET /api/order/<order_id>

Returns the full order payload used by QML, including QR URL, payment mode,
cloud order fields, paid fields, and item lines.

## V2.6.11-C Demo Price Policy

SKU001-SKU010 expose campus convenience-store demo reference prices through
`/api/state.products`, `/api/state.quick_products`, cart items, and order items.
These prices are not real-time online prices.

Price update safety script:

```sh
python3 tools/update_v2611c_demo_prices.py --dry-run
python3 tools/update_v2611c_demo_prices.py --apply
```

The script only updates `products.price_cent` for SKU001-SKU010 and backs up the
database before apply.

## V2.6.11-D Checkout UI Action Contract

Checkout responses can carry an explicit UI action for QML:

```json
{
  "intent": "checkout",
  "ui_action": "open_payment_dialog",
  "order": {},
  "audio_event": "payment_wait"
}
```

QML must call `openPaymentDialog(order)` when `ui_action` is
`open_payment_dialog`. This applies to button checkout and voice checkout.

When checkout is blocked, for example an empty cart:

```json
{
  "success": false,
  "intent": "checkout",
  "ui_action": "show_error",
  "error_reason": "cart_empty",
  "message": "购物车为空，不能结账"
}
```

## GET /api/speech/menu

Return the current wake/numeric voice menu.

Response:

```json
{
  "ok": true,
  "voice_mode": "idle",
  "menu": {
    "wake_prompt": "先说：小售小售",
    "command_prompt": "请说数字指令：1 查询总价...",
    "candidate_mode": false,
    "items": [
      { "digit": "1", "intent": "query_total_price", "label": "查询总价" },
      { "digit": "2", "intent": "remove_last", "label": "删除上一件" },
      { "digit": "3", "intent": "clear_cart", "label": "清空购物车" },
      { "digit": "4", "intent": "checkout", "label": "结账" },
      { "digit": "5", "intent": "camera_capture", "label": "拍照识别" },
      { "digit": "0", "intent": "cancel", "label": "取消" }
    ]
  }
}
```

When a manual vision-candidate menu is active, digits `1` through `3` map to
explicit candidate confirmation. Vision never auto-adds to the cart without a
scan or explicit candidate confirmation.

## POST /api/speech/session_step

State-machine endpoint for QML voice recording. In `idle`, it only accepts a
wake word. Without a wake word, no command is executed.

Test-mode request with injected text:

```json
{ "text": "小售小售", "reset": true }
```

Response after wake:

```json
{
  "ok": true,
  "success": true,
  "voice_mode": "command_listening",
  "stage": "wake",
  "wake_detected": true,
  "message": "唤醒成功，请说数字指令"
}
```

Next command request:

```json
{ "text": "四" }
```

Response:

```json
{
  "ok": true,
  "success": true,
  "voice_mode": "command_executing",
  "next_voice_mode": "idle",
  "digit": "4",
  "intent": "checkout",
  "executed": true,
  "message": "已生成订单 ORDER..."
}
```

Safety response when not woken:

```json
{
  "ok": true,
  "success": false,
  "voice_mode": "idle",
  "stage": "wake",
  "executed": false,
  "error_reason": "no_wake",
  "message": "请先说：小售小售"
}
```

## POST /api/speech/wake_once

Record/recognize once, or accept test-mode JSON `text`, and only classify
wake/no-wake. It does not execute cashier commands.

## POST /api/speech/command_once

After a successful wake, record/recognize once, normalize the numeric command,
execute the closed-domain command, and return the action result. If the voice
session is not already in `command_listening`, it returns `not_woken` and
executes nothing.

## POST /api/speech/cancel

Cancel the current voice session and return to the safe idle path.

## POST /api/scan

Add an item by barcode. V2.5.16 also accepts an active product ID such as
`SKU006` in the same `barcode` field for manual kiosk input.

V2.5.18b scanner HID compatibility accepts any of these JSON fields and treats
the first non-empty value as the scan text:

- `barcode`
- `code`
- `text`
- `product_id`

Request:

```json
{ "barcode": "6954767474670" }
```

Equivalent V2.5.18b requests:

```json
{ "code": "SKU006" }
{ "text": "SKU006" }
{ "product_id": "SKU006" }
```

Success returns `status=added`, the matched product, and the refreshed cart.
Unknown barcode/product ID returns `ok=false`, `status=unknown_barcode`.

V2.5.18c standardizes scan responses for cashier feedback. Every scan response
now includes:

- `ok`: boolean
- `success`: boolean
- `input`: normalized submitted text
- `raw_code`: normalized submitted text
- `barcode`: normalized submitted text
- `product_id`: matched product ID, or empty string
- `product_name`: matched product name, or empty string
- `message`: operator-facing text
- `error_reason`: empty on success, otherwise a reason such as `unknown_barcode`
  or `empty_scan`
- `cart`: refreshed cart
- `total_price_cent`: cart total in cents
- `total_yuan`: cart total in yuan

Unknown barcode example:

```json
{
  "ok": false,
  "success": false,
  "status": "unknown_barcode",
  "error": "unknown_barcode",
  "error_reason": "unknown_barcode",
  "input": "UNKNOWN_TEST_001",
  "raw_code": "UNKNOWN_TEST_001",
  "barcode": "UNKNOWN_TEST_001",
  "product_id": "",
  "product_name": "",
  "message": "未录入商品：UNKNOWN_TEST_001",
  "cart": {},
  "total_price_cent": 0,
  "total_yuan": 0.0
}
```

Empty scan example:

```json
{
  "ok": false,
  "success": false,
  "status": "empty_scan",
  "error": "empty_scan",
  "error_reason": "empty_scan",
  "message": "扫码内容为空"
}
```

## POST /api/cart/add

Request:

```json
{ "product_id": "SKU006", "quantity": 1 }
```

Returns the added product and refreshed cart.

## POST /api/cart/remove_last

Removes one unit from the latest cart line.

## POST /api/cart/remove_product

Request:

```json
{ "product_id": "SKU006" }
```

Removes one unit of the specified product from the cart.

## POST /api/cart/clear

Clears the cart and keeps the existing `play_audio("cart_clear")` behavior.

## POST /api/checkout

Creates an order with the existing `create_order()` flow. Empty cart returns HTTP 400:

```json
{ "ok": false, "error": "cart_empty", "message": "cart is empty, cannot checkout" }
```

Success includes:

```json
{
  "ok": true,
  "order_id": "ORDER...",
  "checkout_url": "/checkout/ORDER...",
  "qr_image_url": "/static/qrcodes/ORDER....svg",
  "payment_url": "http://...",
  "total_cent": 200
}
```

## GET /api/order/<order_id>

Returns order, order items, payment status, cloud fields, local checkout URL, and QR image URL. The route calls the existing cloud sync path before reading status.

## POST /api/capture

Calls the existing `capture_image()` function.

V2.5.18e adds capture robustness:

- single capture mutex, no re-entry
- cooldown for rapid repeated clicks
- timeout handling for camera/GStreamer capture
- stable JSON for success, busy, cooldown, timeout, and failure
- lightweight cleanup after successful capture

Success:

```json
{
  "ok": true,
  "success": true,
  "error_reason": "",
  "image_path": "captures/xxx.jpg",
  "image_url": "http://127.0.0.1:5000/static/captures/xxx.jpg",
  "image_file_url": "file:///userdata/smart_retail/static/captures/xxx.jpg",
  "latency_ms": 123,
  "message": "拍照成功：captures/xxx.jpg (123 ms)",
  "capture_count": 26,
  "cleanup_deleted_count": 0
}
```

`/api/state` then exposes the same capture through `latest_capture`,
`latest_capture_url`, and `latest_capture_latency_ms`.

Busy/cooldown/timeout examples:

```json
{
  "ok": false,
  "success": false,
  "error_reason": "capture_busy",
  "message": "摄像头正在拍照，请稍后再试",
  "capture_count": 26,
  "cleanup_deleted_count": 0
}
```

```json
{
  "ok": false,
  "success": false,
  "error_reason": "capture_cooldown",
  "message": "拍照过于频繁，请稍后再试"
}
```

```json
{
  "ok": false,
  "success": false,
  "error_reason": "capture_timeout",
  "message": "拍照超时，请重新尝试"
}
```

## POST /api/captures/cleanup

Deletes old capture images according to the V2.5.18e cleanup policy. It keeps
the current `latest_capture`, protects the newest 20 images, keeps at most 50
images by default, and tries to keep capture storage under 100 MB.

Response:

```json
{
  "ok": true,
  "deleted_count": 0,
  "remaining_count": 26,
  "capture_count": 26,
  "total_size_mb": 5.3,
  "capture_total_size_mb": 5.3,
  "message": "已清理旧照片 0 张，剩余 26 张"
}
```

V2.5.18e `/api/state` capture storage fields:

- `capture_count`
- `capture_total_size_mb`

## POST /api/speech/execute

Request:

```json
{ "text": "我要截止", "confirmed": false }
```

The API parses with V2.5.4 `parse_speech_intent()`. For risky commands such as `checkout` and `clear_cart`, the first call returns `confirm_required=true` and does not execute. Send the same text with `"confirmed": true` to execute.

Response includes:

```json
{
  "ok": true,
  "text": "我要截止",
  "intent": "checkout",
  "corrected": true,
  "confirm_required": true,
  "result": "confirmation required"
}
```

## POST /api/speech/auto_once

Compatibility wrapper for the existing `/speech/auto_once` JSON route.

## GET /api/metrics

Returns a compact status payload for the kiosk status bar:

## V2.5.18f Audio API

USB Audio I/O is frozen on:

```text
plughw:CARD=III,DEV=0
```

The board enumerates HyperX Cloud III as ALSA card `III`, with playback and
capture both present.

Current `/api/state` reports audio config and latest audio activity:

```json
{
  "audio": {
    "output_device": "plughw:CARD=III,DEV=0",
    "input_device": "plughw:CARD=III,DEV=0",
    "latest_event": "cart_clear",
    "latest_action": "play",
    "latest_success": true,
    "latest_message": "started",
    "latest_device": "plughw:CARD=III,DEV=0",
    "latest_latency_ms": 12,
    "latest_path": "/userdata/smart_retail/static/audio/cart_clear.wav",
    "latest_time": "2000-01-02 03:05:59"
  }
}
```

### GET /api/audio/status

Returns ALSA diagnostics, current app audio devices, latest audio event, known
audio event keys, and recent audio logs.

### POST /api/audio/set

Accepts JSON or form data:

```json
{
  "output_device": "plughw:CARD=III,DEV=0",
  "input_device": "plughw:CARD=III,DEV=0"
}
```

Response:

```json
{
  "ok": true,
  "output_device": "plughw:CARD=III,DEV=0",
  "input_device": "plughw:CARD=III,DEV=0",
  "message": "audio devices updated"
}
```

### POST /api/audio/test_output

Accepts:

```json
{
  "event": "scan_success"
}
```

`event` can be an `AUDIO_EVENTS` key, `tone`, a wav filename, or an absolute wav
path. Playback uses `get_audio_output_device()`.

### POST /api/audio/test_record

Accepts:

```json
{
  "seconds": 2,
  "filename": "api_audio_test.wav"
}
```

Recording uses `get_audio_input_device()` and writes under `static/audio`.

### Voice Prompt Events

V2.5.18f adds fixed-WAV prompt aliases:

```text
voice_ready
voice_processing
voice_success
voice_failed
```

## V2.5.20b Full Operation Broadcast

All major user-visible operations now map to fixed audio events. Dynamic TTS is
still out of scope.

Audio status in API responses, where practical:

```json
{
  "audio_event": "scan_success",
  "audio_ok": true,
  "audio_message": "started",
  "audio_device": "plughw:CARD=III,DEV=0"
}
```

`/api/state.audio` remains the authoritative latest audio status:

```json
{
  "audio": {
    "output_device": "plughw:CARD=III,DEV=0",
    "input_device": "plughw:CARD=III,DEV=0",
    "latest_event": "system_ready",
    "latest_action": "play",
    "latest_success": true,
    "latest_message": "Playing WAVE ...",
    "latest_device": "plughw:CARD=III,DEV=0",
    "latest_latency_ms": 412
  }
}
```

Supported broadcast events:

```text
system_ready
scan_success
unknown_product
scan_failed
capture_start
capture_success
capture_busy
capture_failed
add_cart
remove_last
cart_clear
total_query
payment_wait
payment_success
voice_ready
voice_processing
voice_success
voice_failed
input_routed_scan
```

Playback policy:

```text
new prompt interrupts previous prompt
audio failure updates latest_audio state
audio failure must not crash core business APIs
```

## V2.5.20c Cloud Payment Recovery

`GET /api/cloud/status` returns current cloud base URL, health URL, latency, and health payload.

`POST /api/cloud/test_order` creates a one-cent cloud-only probe order without changing local cart/product data.

## V2.5.20c Vision Trigger APIs

Vision is verification/fallback only. Barcode scan remains the primary automatic add-to-cart path.

- `GET /api/vision/status`
- `POST /api/vision/verify_scan`
- `POST /api/vision/candidates`
- `POST /api/vision/confirm`

`/api/vision/verify_scan` and `/api/vision/candidates` never add cart items. `/api/vision/confirm` adds one item only after explicit manual confirmation.

`/api/state` now also exposes `vision_enabled`, `vision_auto_add_cart`, `latest_vision_mode`, `latest_vision_result`, `latest_vision_top1_product_id`, `latest_vision_confidence`, `latest_vision_match_scan`, `latest_vision_message`, and `latest_vision_latency_ms`.

The final 10-SKU vision model is not claimed complete until new data is trained, exported, installed, and field-tested.

## V2.6.0 10-SKU Vision Baseline APIs

V2.6.0 adds a 10-SKU baseline model package under:

```text
/userdata/smart_retail/models/vision_10sku_v260/
```

Expected files:

- `model.onnx`
- `best.pt`
- `labels.txt`
- `class_map.json`
- `model_metadata.json`

`POST /api/vision/predict` is now available. It accepts `image_path`; if omitted, the backend uses the latest capture. It returns `top1`, `top3`, `candidates`, `backend`, `model_available`, `latency_ms`, and a human-readable `message`.

`GET /api/vision/status` must report backend state honestly:

- `backend=onnxruntime` when ONNX inference dependencies are available;
- `backend=ultralytics` when PyTorch/Ultralytics fallback is available;
- `backend=onnxruntime_missing`, `ultralytics_missing`, or `disabled` when board inference is unavailable.

Safe business rule:

```text
barcode scan adds once
vision verifies or suggests only
vision confirm may add one item only after explicit user confirmation
vision never continuously auto-adds
```

The current V2.6.0 model is a low-sample baseline trained from 117 images. Do not describe it as the final high-confidence visual recognition model.
# V2.6.2 RKNN/NPU Vision Status

The V2.6.2 RKNN/NPU gate is discovery-only for the project model. The board can run RKNN C demos and has NPU runtime support, but the active app vision backend remains ONNX Runtime until a project `.rknn` model and usable runtime are available.

Expected current status:

```json
{
  "backend": "onnxruntime",
  "model_available": true,
  "policy": "barcode_adds_once_vision_verifies_only"
}
```

Future RKNN status fields should include:

```json
{
  "active_backend": "rknn",
  "rknn_available": true,
  "onnxruntime_available": true,
  "rknn_model_path": "/userdata/smart_retail/models/vision_10sku_rknn_v262/vision_10sku_v262_default.rknn",
  "last_inference_latency_ms": 0
}
```

No current API endpoint should claim `active_backend=rknn` until the 10-SKU RKNN model is exported and validated.

# V2.6.3 RKNN CLI Vision Backend

V2.6.3 exports the 10-SKU ONNX model to RKNN and deploys a board-side C runtime CLI. The active board backend may now report `rknn_cli` only when all of these are present:

- `/userdata/smart_retail/bin/vision_rknn_cli_v263/vision_rknn_cli`
- `/userdata/smart_retail/bin/vision_rknn_cli_v263/lib/librknnrt.so`
- `/userdata/smart_retail/models/vision_10sku_rknn_v263/vision_10sku_v263_default.rknn`
- `/userdata/smart_retail/models/vision_10sku_rknn_v263/labels.txt`

`GET /api/vision/status` may include:

```json
{
  "backend": "rknn_cli",
  "active_backend": "rknn_cli",
  "backend_reason": "rknn_cli_available",
  "rknn_cli_available": true,
  "rknn_model_available": true,
  "rknn_labels_available": true,
  "rknn_cli_path": "/userdata/smart_retail/bin/vision_rknn_cli_v263/vision_rknn_cli",
  "rknn_model_path": "/userdata/smart_retail/models/vision_10sku_rknn_v263/vision_10sku_v263_default.rknn",
  "model_version": "v263_rknn_10sku_baseline"
}
```

`POST /api/vision/predict` returns RKNN candidates with `source=rknn_cli` when RKNN is active:

```json
{
  "ok": true,
  "backend": "rknn_cli",
  "active_backend": "rknn_cli",
  "result": "predicted",
  "message": "RKNN NPU vision prediction complete; no automatic cart add",
  "top1": {
    "product_id": "SKU001",
    "product_name": "三元酸奶",
    "confidence": 0.9976,
    "source": "rknn_cli"
  },
  "auto_add_cart": false
}
```

Fallback policy:

- Prefer RKNN CLI when available.
- Fall back to ONNX Runtime if RKNN CLI fails and ONNX Runtime is available.
- Keep barcode scanning as the only automatic add-to-cart authority.
- Vision remains verification/suggestion only.
# V2.6.5 Field UX Hardening Addendum

## `GET /api/state`

Additional V2.6.5 fields:

```json
{
  "quick_product_count": 10,
  "quick_products": ["SKU001 ... SKU010"],
  "cart_items": [],
  "cart_count": 0,
  "cart_total_cent": 0,
  "cart_total_yuan": 0.0,
  "cart_total_consistency_ok": true,
  "cart_total_items_sum_cent": 0,
  "latest_capture_status": "idle",
  "latest_capture_message": "",
  "latest_capture_error_reason": "",
  "latest_speech_status": "idle",
  "latest_speech_message": "",
  "latest_vision_job_status": "done",
  "active_backend": "rknn_cli"
}
```

`quick_products` is intentionally limited to SKU001-SKU010 for the field kiosk panel.

V2.6.6 additional fields:

```json
{
  "cart_total_recomputed_cent": 0,
  "latest_capture_id": "capture_YYYYMMDD_HHMMSS_mmm",
  "latest_capture_updated_at": "epoch_seconds",
  "latest_capture_thumb": "captures/thumbs/name_thumb.jpg",
  "latest_capture_thumb_url": "http://127.0.0.1:5000/static/captures/thumbs/name_thumb.jpg"
}
```

## `POST /api/vision/verify_scan`

Request:

```json
{
  "barcode": "SKU001",
  "image_path": "",
  "capture": true
}
```

When `capture=true`, the backend captures a fresh image before RKNN verification. Cart is not modified by this endpoint.

## Speech parsed fields

V2.6.6 command parsing may return:

```json
{
  "raw_text": "我要有结仭",
  "normalized_text": "我要有结仭",
  "canonical_command": "我要结账",
  "intent": "checkout",
  "confidence": 0.98,
  "match_method": "alias",
  "correction_hit": true,
  "confirm_required": true
}
```

Supported fixed commands:

```text
一共多少钱 -> query_total_price
删除上一件 -> remove_last
清空购物车 -> clear_cart
我要结账 -> checkout
拍照 -> camera_capture
```

## `POST /api/system/reset_busy_flags`

Resets display-level capture/speech busy flags and attempts to stop stale capture/Whisper subprocesses.

Response:

```json
{"ok": true, "capture_status": "idle", "speech_status": "idle"}
```

## `POST /api/speech/reset`

Resets speech status and attempts to stop stale Whisper subprocesses.

Response:

```json
{"ok": true, "status": "idle"}
```

# V2.6.8 Voice Guard and Payment QR Addendum

## Wake plus command

`POST /api/speech/session_step` accepts wake-plus-command text in one utterance:

```json
{"text": "小售小售我要结账"}
```

Expected response fields include:

```json
{
  "ok": true,
  "stage": "wake_plus_command",
  "executed": true,
  "digit": "4",
  "intent": "checkout",
  "message": "已生成订单 ORDER..."
}
```

Wake-only text such as `小售小售` must not execute a cashier action.

## Button direct numeric mode

QML can call:

```json
{"button_wake": true}
```

Then the next command may be just `一`, `二`, `四`, or another supported digit alias. The operator does not need to say the wake word again after pressing the button.

## Voice guard APIs

- `POST /api/speech/guard/start`
- `POST /api/speech/guard/stop`
- `GET /api/speech/guard/status`
- `POST /api/speech/guard/tick`
- `POST /api/speech/guard/cleanup`
- `POST /api/speech/recordings/cleanup`

Guard status is also exposed in `/api/state`:

```json
{
  "voice_guard_enabled": false,
  "voice_guard_status": "off",
  "voice_guard_message": "",
  "voice_guard_runtime_sec": 0,
  "voice_guard_recording_count": 0,
  "voice_guard_total_size_mb": 0.0,
  "voice_guard_dir": "/userdata/smart_retail/static/audio/voice_guard"
}
```

Guard mode still requires wake detection before action execution. Recordings are bounded under `static/audio/voice_guard/`.

# V2.6.9-B Payment Accessibility and Voice Menu Contract

## Payment accessibility fields

Order JSON from `POST /api/checkout`, `/api/state.latest_order`, `/api/order/<order_id>`, and `/api/payment/qr/regenerate` includes:

```json
{
  "payment_mode": "cloud | lan | local_debug",
  "payment_accessibility": "phone_accessible | same_lan_required | local_debug_only | unknown",
  "payment_qr_content": "http://...",
  "payment_qr_url": "http://127.0.0.1:5000/static/qrcodes/ORDER.png",
  "payment_qr_file_url": "file:///userdata/smart_retail/static/qrcodes/ORDER.png",
  "cloud_pay_url": "http://<payment-host>:8000/pay/...",
  "local_pay_url": "http://127.0.0.1:5000/pay/ORDER...",
  "board_lan_ip": "192.168.x.x",
  "qr_exists": true,
  "qr_error": "",
  "qr_user_message": "云端支付，手机可扫码访问"
}
```

Mode policy:

- `cloud`: QR content is `cloud_pay_url`; `payment_accessibility=phone_accessible`.
- `lan`: QR content is `http://<board_lan_ip>:5000/pay/<order_id>`; `payment_accessibility=same_lan_required`.
- `local_debug`: QR content may be `127.0.0.1`; `payment_accessibility=local_debug_only`; phone scan must be described as unavailable.

## Cloud status

`GET /api/cloud/status` returns:

```json
{
  "ok": true,
  "cloud_enabled": true,
  "cloud_base_url": "http://<payment-host>:8000",
  "cloud_health_ok": false,
  "error": "network error text",
  "last_checked_at": "2026-06-09 21:53:46"
}
```

## Voice menu state

`GET /api/state` includes:

```json
{
  "voice_menu_items": [
    {"digit": "1", "label": "查询总价", "intent": "query_total_price"},
    {"digit": "2", "label": "删除上一件", "intent": "remove_last"},
    {"digit": "3", "label": "清空购物车", "intent": "clear_cart"},
    {"digit": "4", "label": "结账", "intent": "checkout"},
    {"digit": "5", "label": "拍照识别", "intent": "camera_capture"},
    {"digit": "0", "label": "取消", "intent": "cancel"}
  ],
  "voice_menu_prompt": "请说数字指令：1 查询总价，2 删除上一件，3 清空购物车，4 结账，5 拍照识别，0 取消"
}
```

Speech error responses include `success=false`, `executed=false`, `error_reason`, and a user-visible `message`.

# V2.6.10 Phone-First Cloud Payment and Numbered Voice Contract

## Phone demo readiness

Order JSON includes:

```json
{
  "phone_demo_ready": true,
  "phone_demo_status": "phone_demo_ready"
}
```

Values:

- `true` / `phone_demo_ready`: cloud payment URL is available and QR content is `cloud_pay_url`.
- `"conditional"` / `same_lan_required`: LAN payment URL is available; phone must be on the same LAN.
- `false` / `local_debug_only`: local debug QR only; phone cannot access the QR content.

## Promote local order to cloud

```text
POST /api/order/<order_id>/promote_cloud
```

Success response includes updated `order` with:

- `payment_mode=cloud`
- `payment_accessibility=phone_accessible`
- `phone_demo_ready=true`
- `cloud_pay_url`
- regenerated QR PNG

Failure response is JSON and does not create a duplicate local order:

```json
{
  "ok": false,
  "success": false,
  "error_reason": "cloud_create_failed",
  "message": "云端订单创建失败，请检查网络和云支付服务"
}
```

## Numbered voice phrase

Recommended wake command format:

```text
小售小售一号查询总价
小售小售二号删除上一件
小售小售三号清空购物车
小售小售四号结账
小售小售五号拍照识别
小售小售零号取消
```

If number and action phrase conflict, the action phrase wins and response includes `conflict_warning=true`.

## Payment QR fields

Order JSON now includes QR and payment URL fields:

```json
{
  "payment_qr_content": "http://...",
  "payment_qr_path": "/userdata/smart_retail/static/qrcodes/ORDER.svg",
  "payment_qr_url": "http://127.0.0.1:5000/static/qrcodes/ORDER.svg",
  "payment_qr_file_url": "file:///userdata/smart_retail/static/qrcodes/ORDER.svg",
  "qr_exists": true,
  "qr_error": "",
  "payment_url_type": "cloud",
  "preferred_payment_url": "http://<payment-host>:8000/pay/..."
}
```

When cloud payment is unavailable, `payment_url_type` is `local_fallback` and the local QR remains explicit.

## `POST /api/payment/qr/regenerate`

Request:

```json
{"order_id": "ORDER..."}
```

If `order_id` is omitted, the latest order is used. The response returns `ok`, `success`, `order`, `qr_exists`, `qr_error`, and `payment_qr_content`.

# V2.6.9 Final Voice and QR Contract

## Payment URL mode

Order JSON now distinguishes payment modes:

```json
{
  "payment_mode": "cloud",
  "payment_url_type": "cloud",
  "local_debug_only": false,
  "board_lan_ip": "192.168.137.191",
  "board_lan_iface": "eth0",
  "payment_qr_path": "/userdata/smart_retail/static/qrcodes/ORDER.png",
  "payment_qr_file_url": "file:///userdata/smart_retail/static/qrcodes/ORDER.png",
  "qr_exists": true,
  "qr_message": "云端支付二维码"
}
```

Modes:
- `cloud`: QR content is `cloud_pay_url`.
- `local`: QR content is `http://<board_lan_ip>:5000/pay/<order_id>`.
- `local_debug`: QR content may be `127.0.0.1`; this is explicitly marked as not phone-accessible.

QR image files are PNG-first. SVG may exist as a compatibility artifact.

## Numeric-only button command

After QML button wake, command recognition uses numeric-only parsing. Natural phrases such as `我要结账` are rejected unless a clear number is detected. The response includes:

```json
{
  "success": false,
  "executed": false,
  "error_reason": "natural_language_not_allowed",
  "message": "请说数字 1/2/3/4/5/0，不要说自然语言命令"
}
```

## Inline wake command

`POST /api/speech/session_step` supports inline wake execution:

```json
{"text": "小售小售我要结账"}
```

returns digit `4` and intent `checkout`. `小售小售` without an explicit command defaults to safe command `1 查询总价`.
