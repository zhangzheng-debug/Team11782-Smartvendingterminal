#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2.6.6 fixed command fuzzy matcher gate."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import parse_speech_intent  # noqa: E402


CASES = [
    ("我要结账", "checkout"),
    ("我要有结仭", "checkout"),
    ("我要结仭", "checkout"),
    ("我要截正", "checkout"),
    ("我要节证", "checkout"),
    ("我要接着", "checkout"),
    ("删除上一件", "remove_last"),
    ("三推上一件", "remove_last"),
    ("山推上一间", "remove_last"),
    ("分推上一件", "remove_last"),
    ("清空购物车", "clear_cart"),
    ("轻空告我车", "clear_cart"),
    ("进公告车", "clear_cart"),
    ("一共多少钱", "query_total_price"),
    ("一个五波捣钱", "query_total_price"),
    ("拍照", "camera_capture"),
    ("拍到", "camera_capture"),
    ("乱七八糟", "unknown"),
]


def main():
    checks = []
    for text, expected in CASES:
        parsed = parse_speech_intent(text)
        got = parsed.get("intent")
        checks.append({
            "text": text,
            "expected": expected,
            "got": got,
            "pass": got == expected,
            "canonical_command": parsed.get("canonical_command", ""),
            "match_method": parsed.get("match_method", parsed.get("reason", "")),
            "correction_hit": parsed.get("correction_hit", False),
            "confirm_required": parsed.get("confirm_required", False),
        })
    ok = all(c["pass"] for c in checks)
    print(json.dumps({"ok": ok, "checks": checks}, ensure_ascii=False, indent=2))
    print("SPEECH_FUZZY_COMMAND_CHECKS=%d PASS=%d FAIL=%d" % (
        len(checks), sum(1 for c in checks if c["pass"]), sum(1 for c in checks if not c["pass"])
    ))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
