# V2.6.3 RKNN Classification CLI Runner

This is a minimal C++ RKNN Runtime bridge for the 10-SKU classifier.

It intentionally avoids board-side Python RKNNLite. Python/PIL can preprocess an image into a raw RGB tensor, then this CLI loads the `.rknn` model through `librknnrt.so` and returns JSON.

Input format:

```text
224 * 224 * 3 RGB uint8 raw tensor
```

Example:

```sh
LD_LIBRARY_PATH=./lib ./vision_rknn_cli \
  --model /userdata/smart_retail/models/vision_10sku_rknn_v263/vision_10sku_v263_default.rknn \
  --input /tmp/vision_rknn_input.rgb \
  --labels /userdata/smart_retail/models/vision_10sku_rknn_v263/labels.txt \
  --topk 3 \
  --json
```

