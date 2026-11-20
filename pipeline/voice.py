#!/usr/bin/env python3
"""تجميع التعليق الصوتي من مقاطع منفصلة (سرد/حوار/مؤثر) إلى ملف واحد لكل مشهد.

كل مشهد في scenes.json ممكن يكون فيه `segments` بدل `vo`:
    {"kind": "narration"|"dialogue"|"whisper", "speaker": "ياسين", "text": "...",
     "audio": "assets/audio/ep02/scene-01-s1.mp3", "pre": 0.0, "post": 0.5}

السكربت بيقرأ المقاطع بترتيبها، يحط فاصل زمني بينها (pre/post)، ويعمل ملف
WAV 48k mono لكل مشهد: assets/audio/ep02/scene-NN.wav

بعد كده render.py بيتعامل معاه زي أي vo_file عادي.
"""
import json
import os
import subprocess
import sys

import imageio_ffmpeg
import numpy as np

FF = imageio_ffmpeg.get_ffmpeg_exe()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000


def decode(path, sr=SR):
    raw = subprocess.run(
        [FF, "-hide_banner", "-loglevel", "error", "-i", path,
         "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
        capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0


def trim_silence(x, thresh=0.004, pad=0.05, sr=SR):
    """يقصّ الصمت الزايد في الأول والآخر (بييجي كتير من TTS)."""
    if not len(x):
        return x
    win = int(0.02 * sr)
    n = len(x) // win
    if n == 0:
        return x
    env = np.abs(x[: n * win]).reshape(n, win).max(axis=1)
    idx = np.where(env > thresh)[0]
    if not len(idx):
        return x
    a = max(int(idx[0] * win) - int(pad * sr), 0)
    b = min(int((idx[-1] + 1) * win) + int(pad * sr), len(x))
    return x[a:b]


def fade(x, ms=12, sr=SR):
    k = max(int(sr * ms / 1000), 1)
    if len(x) < 2 * k:
        return x
    x = x.copy()
    x[:k] *= np.linspace(0, 1, k)
    x[-k:] *= np.linspace(1, 0, k)
    return x


def write_wav(path, x, sr=SR):
    x = np.clip(x, -1, 1)
    pcm = (x * 32767).astype("<i2").tobytes()
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y",
                    "-f", "s16le", "-ar", str(sr), "-ac", "1", "-i", "-",
                    "-c:a", "pcm_s16le", path], input=pcm, check=True)


def assemble(segments, out_path, sr=SR, default_pre=0.10, default_post=0.42):
    """segments: list of dicts with `audio` path + optional pre/post (seconds)."""
    parts = []
    for i, seg in enumerate(segments):
        p = os.path.join(ROOT, seg["audio"])
        if not os.path.exists(p):
            raise SystemExit(f"مقطع ناقص: {p}")
        x = fade(trim_silence(decode(p, sr)), sr=sr)
        pre = seg.get("pre", 0.0 if i == 0 else default_pre)
        post = seg.get("post", default_post)
        if pre:
            parts.append(np.zeros(int(pre * sr), dtype=np.float32))
        parts.append(x)
        if post:
            parts.append(np.zeros(int(post * sr), dtype=np.float32))
    sig = np.concatenate(parts) if parts else np.zeros(sr, dtype=np.float32)
    peak = float(np.max(np.abs(sig))) or 1.0
    if peak > 0.0:
        sig = sig / peak * 0.89          # ذروة موحّدة قبل الميكس
    write_wav(out_path, sig, sr)
    return len(sig) / sr


def scene_segments(sc):
    """لو المشهد فيه segments نرجّعها، وإلا نغلّف vo_file كمقطع واحد."""
    if sc.get("segments"):
        return sc["segments"]
    return [{"kind": "narration", "speaker": "ياسين", "audio": sc["vo_file"]}]


def main():
    spec_path = sys.argv[1]
    spec = json.load(open(spec_path, encoding="utf-8"))
    outdir = os.path.join(os.path.dirname(os.path.abspath(spec_path)), "..", "..",
                          "assets", "audio", os.path.basename(os.path.dirname(
                              os.path.abspath(spec_path))).split("-")[0].lower())
    os.makedirs(outdir, exist_ok=True)
    total = 0.0
    for sc in spec["scenes"]:
        segs = scene_segments(sc)
        out = os.path.join(ROOT, "assets", "audio", "ep02", f"scene-{sc['id']:02d}.wav")
        d = assemble(segs, out)
        total += d
        print(f"[✓] مشهد {sc['id']:02d}: {d:.2f}s ← {len(segs)} مقاطع")
    print(f"[i] إجمالي الكلام: {total/60:.2f} دقيقة")


if __name__ == "__main__":
    main()
