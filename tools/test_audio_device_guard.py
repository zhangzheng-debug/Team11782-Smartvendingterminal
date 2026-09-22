#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit checks for truthful ALSA device availability reporting."""

import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class AudioDeviceGuardTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="qsm_audio_guard_")
        self.addCleanup(self.temp.cleanup)
        copied = Path(self.temp.name) / "app.py"
        shutil.copy2(ROOT / "app.py", copied)
        spec = importlib.util.spec_from_file_location("isolated_audio_guard", copied)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def test_host_without_proc_asound_keeps_test_compatibility(self):
        missing = Path(self.temp.name) / "missing-asound"
        self.assertTrue(self.module.audio_device_available("plughw:CARD=III,DEV=0", missing))

    def test_present_named_card_is_available(self):
        proc = Path(self.temp.name) / "asound"
        proc.mkdir()
        (proc / "cards").write_text(" 2 [III ]: USB-Audio - HyperX\n", encoding="utf-8")
        self.assertTrue(self.module.audio_device_available("plughw:CARD=III,DEV=0", proc))

    def test_missing_named_card_is_unavailable(self):
        proc = Path(self.temp.name) / "asound"
        proc.mkdir()
        (proc / "cards").write_text(" 0 [rockchiprk809co]: rk809\n", encoding="utf-8")
        self.assertFalse(self.module.audio_device_available("plughw:CARD=III,DEV=0", proc))

    def test_numeric_card_directory_is_available(self):
        proc = Path(self.temp.name) / "asound"
        (proc / "card0").mkdir(parents=True)
        (proc / "cards").write_text(" 0 [rockchiprk809co]: rk809\n", encoding="utf-8")
        self.assertTrue(self.module.audio_device_available("plughw:0,0", proc))


if __name__ == "__main__":
    unittest.main(verbosity=2)
