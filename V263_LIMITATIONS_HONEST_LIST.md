# V2.6.3 Limitations Honest List

- RKNN INT8 was built but is not default because it had 1/117 top1 mismatch versus ONNX.
- Flask RKNN path uses subprocess CLI, not an in-process long-lived RKNN context. This is simpler and safer for the demo, but it adds process-launch overhead.
- Vision is verification/suggestion only. It does not continuously auto-add cart items.
- Live camera captures may be lower confidence than curated product images depending on lighting and framing.
- The board uses a deployed `/userdata` runtime path. No rootfs integration or autostart was done.
- V2.6.4 technical evidence is complete, but physical evidence photos/videos still need to be captured by the user for the final release pack.
- Cloud paid writeback depends on the known Windows ICS/Ethernet route remaining unchanged during the field demo.
