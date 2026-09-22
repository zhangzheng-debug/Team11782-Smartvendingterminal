# Vision API Contract

Vision is a safe assistive path. Barcode scan is still the primary cashier action. Vision never continuously auto-adds products and does not repeat-add after a scan verification.

## `GET /api/vision/status`

Returns current model/config/backend status and the latest vision result.

Key fields:

- `ok`
- `vision_enabled`
- `model_available`
- `backend`
- `backend_reason`
- `model_version`
- `class_count`
- `labels`
- `model_path`
- `confidence_threshold_high`
- `confidence_threshold_low`
- `policy`
- `auto_add_cart`
- `message`

## `POST /api/vision/predict`

Request:

```json
{"image_path":"captures/capture_x.jpg"}
```

If `image_path` is omitted, the API uses the latest capture path.

Response fields:

- `ok`
- `result`
- `model_available`
- `backend`
- `image_path`
- `top1`
- `top3`
- `candidates`
- `latency_ms`
- `message`

When the model is unavailable, the response must honestly report `result=model_unavailable` or a clear backend reason and may return placeholder candidates with `confidence=0.0`.

## `POST /api/vision/verify_scan`

Request:

```json
{"barcode":"SKU001","image_path":"captures/capture_x.jpg"}
```

Logic:

- The scan path may already have added one item.
- Vision only verifies the scan result.
- Match returns `result=verified_match`.
- Mismatch returns `result=verified_mismatch`.
- Unavailable model returns `result=verification_pending_no_model`.
- This endpoint must not add to the cart.

Response fields:

- `ok`
- `mode`
- `result`
- `raw_code`
- `scanned_product_id`
- `scanned_product_name`
- `top1_product_id`
- `top1_name`
- `confidence`
- `match_scan`
- `candidates`
- `latency_ms`
- `message`
- `auto_add_cart=false`

## `POST /api/vision/candidates`

Request:

```json
{"image_path":"captures/capture_x.jpg","limit":3}
```

Returns Top-3 candidates for unknown-barcode or manual-capture workflows. Candidates are suggestions only and do not mutate the cart.

The optional `capture` field controls whether the request must obtain a fresh
photo before prediction:

```json
{"capture":true,"limit":3}
```

When `capture=true`, the server uses the existing capture mutex, cooldown,
timeout, cleanup and camera error handling. It ignores a supplied or previously
displayed image path. A busy, cooldown, timeout, missing file, unavailable
model or failed prediction returns an explicit failure with empty candidates;
the previous image is never used as a substitute. A successful fresh request
returns its capture metadata and `auto_add_cart=false`.

When `capture` is omitted or false, legacy diagnostic calls may continue to use
`image_path` or the latest capture path. This compatibility path does not
change the rule that candidates never add to the cart.

## `POST /api/vision/confirm`

Request:

```json
{"product_id":"SKU001","confirmed":true}
```

Adds one item only after explicit manual confirmation. If `confirmed=false`, nothing is added.

## V2.6.0 Model Location

Board target:

```text
/userdata/smart_retail/models/vision_10sku_v260/
  best.pt
  model.onnx
  labels.txt
  class_map.json
  model_metadata.json
```

Backend priority:

1. `onnxruntime`
2. `ultralytics`/PyTorch
3. disabled/fallback with honest status
# V2.6.2 RKNN/NPU Backend Note

Current active backend remains:

```text
backend=onnxruntime
```

V2.6.2 discovered that the board has an initialized RKNPU device and RKNN C runtime. A vendor YOLOv5 RKNN demo runs successfully, but the project 10-SKU `.rknn` model has not been exported yet and board Python RKNNLite is missing for Python 3.8.

Future backend priority:

```text
1. rknn
2. onnxruntime
3. disabled / pending
```

Business behavior must remain unchanged:

- `/api/scan` is still the primary cart-add path.
- `/api/vision/verify_scan` must not add another cart item.
- `/api/vision/candidates` must not add a cart item.
- `/api/vision/confirm` is the only explicit visual candidate add path.
- Low confidence must not auto-confirm.
