#!/usr/bin/env python3
"""يجمع مقاطع مشهد واحد (سرد + حوار) في WAV واحد، ويرجّع توقيت كل مقطع
عشان الترجمة تتزامن مع المتكلم الصح — من غير أي تخمين توزيع النص.

المبدأ: كل مقطع صوتي معروف مدته بالظبط، فبدل ما نوزّع نص المشهد على الزمن
بالتساوي (اللي بيعمل ترجمة سايبة)، بنحط كل سطر في مكانه الحقيقي.

  assemble_scene(sc, out_wav) -> (duration, timings)
  timings = [(t0, t1, segment_dict), ...]  نسبية لبداية المشهد
"""
import os
import subprocess

import imageio_ffmpeg
import numpy as np

FF = imageio_ffmpeg.get_ffmpeg_exe()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000


def decode(path, sr=SR):
    raw = subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-i", path,
                          "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0


def trim(x, thresh=0.004, pad=0.06, sr=SR):
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


def fade(x, ms=15, sr=SR):
    k = max(int(sr * ms / 1000), 1)
    if len(x) < 2 * k:
        return x
    x = x.copy()
    x[:k] *= np.linspace(0, 1, k)
    x[-k:] *= np.linspace(1, 0, k)
    return x


def write_wav(path, x, sr=SR):
    x = np.clip(x, -1, 1)
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y",
                    "-f", "s16le", "-ar", str(sr), "-ac", "1", "-i", "-",
                    "-c:a", "pcm_s16le", path],
                   input=(x * 32767).astype("<i2").tobytes(), check=True)


def scene_segments(sc):
    """segments إن وُجدت، وإلا vo_file كمقطع سرد واحد (توافق مع الحلقة 1)."""
    if sc.get("segments"):
        return sc["segments"]
    return [{"kind": "narration", "speaker": "ياسين", "audio": sc["vo_file"]}]


def assemble_scene(sc, out_wav, sr=SR, default_pre=0.12, default_post=0.40):
    """يبني WAV المشهد + توقيتاته. لو مقطع ناقص يتخطاه ويكمل."""
    segs = scene_segments(sc)
    parts, timings, t = [], [], 0.0
    missing = []
    for i, seg in enumerate(segs):
        ap = seg.get("audio")
        full = os.path.join(ROOT, ap) if ap else None
        pre = seg.get("pre", 0.0 if i == 0 else default_pre)
        post = seg.get("post", 0.0 if i == len(segs) - 1 else default_post)
        if pre:
            parts.append(np.zeros(int(pre * sr), dtype=np.float32))
            t += pre
        if not full or not os.path.exists(full):
            missing.append(ap)
            continue
        x = fade(trim(decode(full, sr)), sr=sr)
        # تطبيع لكل مقطع على حدة — بدون كده مقطع هادي في مشهد صاخب يفضل مدفون
        # (حصل فعلًا: s04-3 في ح4 و s06-4 في ح2 كانوا أهدى بـ19 dB)
        seg_rms = float(np.sqrt(np.mean(x.astype(np.float64) ** 2))) or 1e-9
        target_rms = 10 ** (-20.0 / 20.0)      # ≈ −20 dBFS RMS
        x = x * (target_rms / seg_rms)
        pk = float(np.max(np.abs(x))) or 1.0
        if pk > 0.92:                           # امنع القص
            x = x * (0.92 / pk)
        parts.append(x)
        timings.append((t, t + len(x) / sr, seg))
        t += len(x) / sr
        if post:
            parts.append(np.zeros(int(post * sr), dtype=np.float32))
            t += post

    sig = np.concatenate(parts) if parts else np.zeros(int(1.0 * sr), dtype=np.float32)
    peak = float(np.max(np.abs(sig))) or 1.0
    sig = sig / peak * 0.89
    os.makedirs(os.path.dirname(out_wav) or ".", exist_ok=True)
    write_wav(out_wav, sig, sr)
    if missing:
        print(f"   ⚠ مقاطع ناقصة في مشهد {sc['id']}: {len(missing)}")
    return len(sig) / sr, timings
