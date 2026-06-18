#!/usr/bin/env python3
"""Safe demo reset: back up DB, clear cart/temp state, optionally trim captures."""

import argparse
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path


DEFAULT_STATE_KEYS = [
    "latest_audio_event", "latest_audio_action", "latest_audio_success", "latest_audio_message",
    "latest_audio_latency_ms", "latest_speech_text", "latest_speech_parsed",
    "latest_vision", "latest_vision_mode", "latest_vision_result", "latest_vision_top1_product_id",
    "latest_vision_top1_name", "latest_vision_confidence", "latest_vision_match_scan",
    "latest_vision_message", "latest_vision_latency_ms", "last_scan_barcode", "last_scan_epoch",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="database/retail_terminal.db")
    parser.add_argument("--capture-dir", default="static/captures")
    parser.add_argument("--keep-captures", type=int, default=5)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        raise SystemExit("DB not found: %s" % db_path)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = db_path.with_name(db_path.stem + "_before_demo_reset_" + ts + db_path.suffix)
    print("DEMO_RESET mode=%s" % ("apply" if args.apply else "dry-run"))
    print("DB_BACKUP_PLANNED %s" % backup)
    if not args.apply:
        print("DRY_RUN no changes")
        return 0

    shutil.copy2(str(db_path), str(backup))
    conn = sqlite3.connect(str(db_path))
    conn.execute("DELETE FROM cart_items")
    for key in DEFAULT_STATE_KEYS:
        conn.execute("DELETE FROM app_state WHERE key=?", (key,))
    conn.commit()
    conn.close()

    cap_dir = Path(args.capture_dir)
    captures = sorted([p for p in cap_dir.glob("*.jpg") if p.is_file()], key=lambda p: p.stat().st_mtime, reverse=True)
    deleted = 0
    for path in captures[args.keep_captures:]:
        path.unlink()
        deleted += 1
    print("DEMO_RESET_APPLIED backup=%s deleted_captures=%d kept=%d" % (backup, deleted, min(len(captures), args.keep_captures)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
