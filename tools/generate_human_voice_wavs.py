#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate fixed Chinese voice prompt WAV assets.

Provider order:
1. OpenAI Audio Speech when OPENAI_API_KEY is present.
2. edge-tts neural voice fallback when edge_tts and imageio_ffmpeg are installed.

The script writes PCM WAV files matching app.py AUDIO_EVENTS names.
"""

import argparse
import asyncio
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path


PROMPTS = {
    "system_ready.wav": "系统已启动",
    "scan_success.wav": "商品已加入购物车",
    "unknown_product.wav": "未录入商品，请重新扫码",
    "scan_failed.wav": "扫码失败，请重试",
    "add_cart.wav": "商品已加入购物车",
    "capture_start.wav": "开始拍照",
    "capture_success.wav": "拍照完成",
    "capture_busy.wav": "摄像头忙，请稍后",
    "capture_failed.wav": "拍照失败，请重试",
    "remove_last.wav": "已删除上一件商品",
    "cart_clear.wav": "购物车已清空",
    "total_query.wav": "已查询总价，请查看屏幕",
    "payment_wait.wav": "已生成订单，请扫码支付",
    "payment_success.wav": "支付成功",
    "voice_ready.wav": "请说话",
    "voice_processing.wav": "正在识别",
    "voice_success.wav": "识别成功",
    "voice_failed.wav": "未识别，请重试",
    "input_routed_scan.wav": "检测到条码，已转为扫码",
}


def post_openai_tts(text, out_path, model, voice):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    payload = {
        "model": model,
        "voice": voice,
        "input": text,
        "instructions": "用清晰、自然、友好的中文收银台提示音语气朗读，速度稍快但不要急促。",
        "response_format": "wav",
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/audio/speech",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            out_path.write_bytes(resp.read())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        raise RuntimeError("OpenAI TTS failed: HTTP %s %s" % (exc.code, body[:500]))


async def edge_tts_to_mp3(text, mp3_path, voice, rate, volume):
    import edge_tts

    communicate = edge_tts.Communicate(text, voice=voice, rate=rate, volume=volume)
    await communicate.save(str(mp3_path))


def ffmpeg_exe():
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return shutil.which("ffmpeg")


def convert_to_pcm_wav(input_path, out_path, sample_rate):
    ffmpeg = ffmpeg_exe()
    if not ffmpeg:
        if input_path.suffix.lower() == ".wav":
            shutil.copy2(input_path, out_path)
            return
        raise RuntimeError("ffmpeg not found. Install imageio-ffmpeg or ffmpeg.")
    cmd = [
        ffmpeg,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(input_path),
        "-ar",
        str(sample_rate),
        "-ac",
        "1",
        "-sample_fmt",
        "s16",
        "-af",
        "loudnorm=I=-17:LRA=9:TP=-1.5",
        str(out_path),
    ]
    subprocess.check_call(cmd)


def generate_one(provider, text, out_path, args):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        if provider == "openai":
            raw = tmp_dir / "raw.wav"
            post_openai_tts(text, raw, args.openai_model, args.openai_voice)
        elif provider == "edge":
            raw = tmp_dir / "raw.mp3"
            asyncio.run(edge_tts_to_mp3(text, raw, args.edge_voice, args.edge_rate, args.edge_volume))
        else:
            raise ValueError("unknown provider: " + provider)
        convert_to_pcm_wav(raw, out_path, args.sample_rate)


def choose_provider(requested):
    if requested != "auto":
        return requested
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    return "edge"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=["auto", "openai", "edge"], default="auto")
    parser.add_argument("--out-dir", default="static/audio_tts_generated")
    parser.add_argument("--install-to", default="")
    parser.add_argument("--backup", action="store_true")
    parser.add_argument("--sample-rate", type=int, default=16000)
    parser.add_argument("--openai-model", default="gpt-4o-mini-tts")
    parser.add_argument("--openai-voice", default="coral")
    parser.add_argument("--edge-voice", default="zh-CN-XiaoxiaoNeural")
    parser.add_argument("--edge-rate", default="+0%")
    parser.add_argument("--edge-volume", default="+0%")
    parser.add_argument("--only", default="", help="comma-separated filenames")
    args = parser.parse_args()

    selected = set(x.strip() for x in args.only.split(",") if x.strip())
    prompts = {k: v for k, v in PROMPTS.items() if not selected or k in selected}
    provider = choose_provider(args.provider)
    out_dir = Path(args.out_dir)

    rows = []
    for filename, text in prompts.items():
        out_path = out_dir / filename
        generate_one(provider, text, out_path, args)
        rows.append({"filename": filename, "text": text, "provider": provider, "path": str(out_path), "bytes": out_path.stat().st_size})
        print("generated", filename, text, out_path)

    backup_dir = ""
    if args.install_to:
        install_dir = Path(args.install_to)
        if args.backup:
            backup_dir = str(install_dir.parent / ("audio_backup_before_human_tts_" + time.strftime("%Y%m%d_%H%M%S")))
            shutil.copytree(install_dir, backup_dir)
            print("backup", backup_dir)
        for filename in prompts:
            shutil.copy2(out_dir / filename, install_dir / filename)
            print("installed", install_dir / filename)

    manifest = {
        "ok": True,
        "provider": provider,
        "out_dir": str(out_dir),
        "install_to": args.install_to,
        "backup_dir": backup_dir,
        "sample_rate": args.sample_rate,
        "assets": rows,
        "ai_voice_disclosure": "Generated voice assets may be AI-generated TTS and should be described as synthesized prompts in release docs.",
    }
    manifest_path = out_dir / "human_voice_tts_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

