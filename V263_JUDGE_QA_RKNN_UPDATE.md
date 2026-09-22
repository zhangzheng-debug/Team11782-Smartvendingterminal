# V2.6.3 Judge QA RKNN Update

Q: Is RKNN/NPU actually used?

A: Yes. The project model was converted to RKNN and deployed to `/userdata/smart_retail/models/vision_10sku_rknn_v263`. Flask now reports `active_backend=rknn_cli`, and the board-side C CLI returns `backend=rknn_cli`, `npu=true`.

Q: Why use a CLI instead of Python RKNNLite?

A: The board Python RKNNLite wheel did not match the board Python 3.8 environment. The board already has working RKNN C runtime, so a small C CLI is safer and avoids system Python pollution.

Q: Does vision automatically add products to cart?

A: No. Barcode scanning is the add-to-cart authority. Vision verifies or suggests candidates only.

Q: What happens if RKNN fails?

A: ONNX Runtime CPU fallback remains installed and the API does not crash the cashier workflow.

Q: What did V2.6.4 add?

A: V2.6.4 did not add new functionality. It froze field-demo evidence for RKNN/NPU: active backend status, CLI smoke, Flask backend test, no-repeat-add test, and final regression results.

Q: What is the best one-sentence explanation?

A: The project runs a custom 10-SKU model through RKNN/NPU on the RK3568 board, while keeping barcode scanning as the stable billing input and using vision only for verification and unknown-barcode candidates.
