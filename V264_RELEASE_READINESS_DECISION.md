# V2.6.4 Release Readiness Decision

Decision: READY_FOR_RELEASE_FREEZE_AFTER_PHYSICAL_EVIDENCE_CAPTURE

Technical readiness: PASS

Reasons:
- HDMI QML cashier is running.
- RKNN/NPU backend is active: `active_backend=rknn_cli`.
- RKNN direct CLI smoke test passes.
- Flask RKNN backend test passes.
- ONNX Runtime fallback remains available.
- 10-SKU scan matrix passes.
- Main cashier API regression passes.
- Capture stress, audio matrix, input arbitration, and vision no-repeat-add pass.
- Cloud payment paid writeback was previously verified and remains part of the demo plan if network setup is unchanged.

Release freeze blocker:
- Not a software blocker.
- User still needs final physical evidence photos/videos for the release evidence pack.

Recommended next step:
- Capture evidence listed in `V264_RKNN_EVIDENCE_MANIFEST.md`.
- Then proceed to `V2.6.5 Release Freeze & Evidence Pack`.

Do not do before release freeze:
- Do not add new features.
- Do not change boot/rootfs/autostart.
- Do not retrain or replace the RKNN model unless a new model gate is opened.
- Do not modify the cloud payment server.

Honest limitation for judges:

```text
The current 10-SKU visual model is a low-sample baseline. It demonstrates the end-to-end RKNN/NPU deployment workflow and verification/candidate loop, but production accuracy would require more lighting, angle, and packaging variation data.
```
