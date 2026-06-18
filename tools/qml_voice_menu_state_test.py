#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V2.6.9-B /api/state voice menu visibility data test."""

import json
import sys
import urllib.request

BASE = "http://127.0.0.1:5000"


def main():
    with urllib.request.urlopen(BASE + "/api/state", timeout=15) as resp:
        state = json.loads(resp.read().decode("utf-8", "replace") or "{}")
    items = state.get("voice_menu_items") or ((state.get("voice_menu") or {}).get("items") or [])
    digits = {str(i.get("digit")) for i in items}
    checks = [
        {"name": "voice menu exists", "pass": bool(items), "items": items},
        {"name": "all fixed digits present", "pass": {"0", "1", "2", "3", "4", "5"}.issubset(digits), "digits": sorted(digits)},
        {"name": "prompt present", "pass": bool(state.get("voice_menu_prompt") or (state.get("voice_menu") or {}).get("command_prompt")), "prompt": state.get("voice_menu_prompt")},
    ]
    p = sum(1 for c in checks if c["pass"])
    f = len(checks) - p
    print(json.dumps({"ok": f == 0, "checks": checks, "summary": {"total": len(checks), "pass": p, "fail": f}}, ensure_ascii=False, indent=2))
    print("QML_VOICE_MENU_STATE_CHECKS=%d PASS=%d FAIL=%d" % (len(checks), p, f))
    return 0 if f == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
