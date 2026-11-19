#!/usr/bin/env python3
"""
إبطاء الإيقاع: يبطّئ التعليق الصوتي مع الحفاظ على طبقة الصوت (pitch)،
ويطوّل الوقفات الطبيعية عند نهايات الجمل، ويضيف صمت تنفّس بين المشاهد.

النتيجة: نفس النص، لكن بإيقاع راوٍ درامي (~90 كلمة/دقيقة) بدل القراءة السريعة.

الاستخدام:
  python pipeline/retime.py episodes/01-الرمادي/scenes.json --tempo 0.85
"""
import argparse
import json
import os
import re
import subprocess

import imageio_ffmpeg
import numpy as np

FF = imageio_ffmpeg.get_ffmpeg_exe()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000


def decode(path):
    raw = subprocess.run(
        [FF, "-hide_banner", "-loglevel", "error", "-i", path,
         "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0


def encode(path, x):
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2").tobytes()
    subprocess.run(
        [FF, "-hide_banner", "-loglevel", "error", "-y", "-f", "s16le",
         "-ar", str(SR), "-ac", "1", "-i", "-",
         "-c:a", "libmp3lame", "-b:a", "192k", path],
        input=pcm, check=True)


def atempo(path_in, tempo, path_out):
    """إبطاء مع الحفاظ على طبقة الصوت، عبر سلسلة atempo لو tempo خارج المدى."""
    chain, t = [], tempo
    while t < 0.5:
        chain.append("atempo=0.5")
        t /= 0.5
    while t > 2.0:
        chain.append("atempo=2.0")
        t /= 2.0
    chain.append(f"atempo={t:.6f}")
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-i", path_in,
                    "-af", ",".join(chain), "-c:a", "libmp3lame", "-b:a", "192k", path_out],
                   check=True)


def insert_pauses(x, sr=SR, cfg=None):
    """يطوّل الصمت عند حدود الجمل/الجمل الفرعية. بيرجّع (الصوت الجديد, عدد الوقفات)."""
    cfg = cfg or {"sentence": (0.35, 0.60), "clause": (0.18, 0.26), "micro": (0.10, 0.10)}
    win = int(0.02 * sr)
    n = len(x) // win
    rms = np.sqrt((x[: n * win].reshape(n, win) ** 2).mean(1))

    # عتبة متكيّفة: أهدأ 15% من الإطارات
    thr = max(0.004, float(np.percentile(rms, 15)) * 0.9)

    runs, start = [], None
    for i, silent in enumerate(rms < thr):
        if silent and start is None:
            start = i
        elif not silent and start is not None:
            runs.append((start, i))
            start = None
    if start is not None:
        runs.append((start, n))

    pieces, prev, added, count = [], 0, 0, 0
    for a, b in runs:
        g = (b - a) * 0.02
        for lo, extra in cfg.values():
            if g >= lo:
                # نُطيل الصمت بإضافة فراغ في منتصفه
                mid = (a + b) // 2
                pieces.append(x[prev * win: mid * win])
                pieces.append(np.zeros(int(extra * sr), dtype=np.float32))
                prev = mid
                added += extra
                count += 1
                break
    pieces.append(x[prev * win:])
    return np.concatenate(pieces), count, added


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scenes")
    ap.add_argument("--tempo", type=float, default=0.85, help="1.0 = بدون تغيير")
    ap.add_argument("--lead", type=float, default=1.15)
    ap.add_argument("--tail", type=float, default=2.10)
    ap.add_argument("--out-spec", default=None)
    a = ap.parse_args()

    spec = json.load(open(a.scenes, encoding="utf-8"))
    outdir = os.path.join(ROOT, "assets", "audio", "ep01", "retimed")
    os.makedirs(outdir, exist_ok=True)
    tmp = os.path.join(outdir, "_tmp.mp3")

    total_before = total_after = 0.0
    for sc in spec["scenes"]:
        src = os.path.join(ROOT, sc["vo_file"])
        dst = os.path.join(outdir, f"scene-{sc['id']:02d}.mp3")

        atempo(src, a.tempo, tmp)
        x = decode(tmp)
        y, n_pause, added = insert_pauses(x)
        encode(dst, y)

        before, after = len(x) / SR, len(y) / SR
        total_before += before
        total_after += after
        w = len(sc["vo"].split())
        print(f"مشهد {sc['id']:2d}: {w} كلمة | {before:5.1f}s → {after:5.1f}s "
              f"| {w/after*60:5.1f} كلمة/دقيقة | +{n_pause} وقفة")

        sc["vo_file"] = os.path.relpath(dst, ROOT)
        sc["lead"] = a.lead
        sc["tail"] = a.tail

    if os.path.exists(tmp):
        os.remove(tmp)

    out_spec = a.out_spec or a.scenes.replace(".json", "-slow.json")
    with open(out_spec, "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)

    print(f"\nالإجمالي: {total_before/60:.2f} → {total_after/60:.2f} دقيقة (تعليق صوتي)")
    print(f"ملف المشاهد الجديد: {out_spec}")


if __name__ == "__main__":
    main()
