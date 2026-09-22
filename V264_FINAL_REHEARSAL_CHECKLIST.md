# V2.6.4 Final Rehearsal Checklist

Before demo:

- [ ] HDMI connected and QML cashier visible.
- [ ] Scanner inserted into the verified USB Host/HID port.
- [ ] HyperX Cloud III inserted into the verified USB audio port.
- [ ] Camera connected.
- [ ] Ethernet/ICS route still working if cloud payment is shown.
- [ ] Flask, Weston, and qmlscene running:

```sh
pgrep -af 'app.py|weston|qmlscene'
```

- [ ] RKNN active:

```sh
cd /userdata/smart_retail
wget -qO- http://127.0.0.1:5000/api/vision/status | head -c 2000
python3 tools/rknn_cli_smoke_test.py
python3 tools/vision_rknn_cli_backend_test.py
```

Demo flow:

- [ ] Start/recover QML if needed: `sh /userdata/start_retail_hdmi_qml.sh`.
- [ ] Scan/type `SKU001`; cart increases once.
- [ ] Trigger vision verify; cart must not increase again.
- [ ] Show `active_backend=rknn_cli`, Top-3, confidence, and latency.
- [ ] Scan/type `UNKNOWN_TEST_001`; show unknown product feedback and vision candidates.
- [ ] Capture image; show latest preview and capture latency.
- [ ] Voice/text command: `一共多少钱`.
- [ ] Voice/text command: `我要截正`; explain correction to checkout intent.
- [ ] Checkout; show order and, if network is available, cloud paid writeback.
- [ ] Play/trigger voice broadcast.

Final regression command:

```sh
cd /userdata/smart_retail
python3 tools/scan_v260_10sku_test.py --manifest dataset_raw_v260/manifest.csv
python3 tools/scan_api_matrix_test.py
python3 tools/qml_business_api_test.py
python3 tools/input_arbitration_api_test.py
python3 tools/capture_stress_test.py
python3 tools/audio_event_matrix_test.py
python3 tools/vision_model_status_test.py
python3 tools/vision_predict_smoke_test.py
python3 tools/vision_scan_verify_test.py
python3 tools/vision_no_repeat_add_test.py
python3 tools/rknn_cli_smoke_test.py
wget -qO- http://127.0.0.1:5000/api/state | head -c 1500
```

Pass condition:
- All automated tests pass.
- QML remains visible.
- RKNN backend remains active.
- No repeated visual add-to-cart occurs.
