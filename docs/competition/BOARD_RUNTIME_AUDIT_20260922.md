# Board Runtime Audit 2026-09-22

## Scope

This audit checks the live QSM368ZP board after the capture cooldown fix. It does not flash the device, change boot/rootfs files, modify the database catalog, or change the cloud server.

## Fixes applied

- Capture cooldown now ignores a persisted future timestamp when the board RTC has moved backwards. A real recent capture still observes the 1.8 second cooldown.
- ALSA playback now checks the configured concrete card before asynchronous playback. Missing hardware is reported as `audio_ok=false`; it cannot make capture, scan, cart or checkout fail.

## Board evidence

| Check | Result |
|---|---|
| ADB | `device` |
| HDMI DRM | `connected` |
| Flask/QML/Weston | running after restart |
| Vision backend | `active_backend=rknn_cli` |
| RKNN CLI smoke | PASS, about 16 ms in the observed run |
| Capture preview stability | 5/5 fresh JPEG + thumbnail captures |
| Unknown barcode | stable JSON `unknown_barcode`; cart unchanged |
| Audio event matrix | 24/24 PASS, including missing-device negative case |
| HyperX Cloud III | ALSA card `2 [III]` present during final check |
| `/userdata` | about 251 MB free; no cleanup/destructive action performed |

## Explicit remaining conditions

- The board RTC still reports `2000-01-01`; evidence filenames use that board clock and should not be treated as wall-clock timestamps.
- `eth0` was `NO-CARRIER` during the audit; cloud payment needs a connected network path and a fresh health check.
- Scanner HID was not asserted by this audit because the scanner must be physically present at the verified USB Host port.
- The persistent board catalog was not rewritten. The live database is the source of current product names and prices; catalog changes require a separate reviewed migration and backup.

## Safety boundary

No RKDevTool Upgrade/EraseFlash, flashing, boot/rootfs/oem/uboot write, `/etc/init.d/S03weston` change, autostart change, cloud-server change or database overwrite was performed.
