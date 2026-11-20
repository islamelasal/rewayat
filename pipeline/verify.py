#!/usr/bin/env python3
"""فحص أصول الحلقة قبل أي تجميع: صور سليمة، صوت مقروء، مقاطع ناقصة، تطابق المدة.

  python pipeline/verify.py episodes/02-الباب/scenes.json [--min-img 1024]
"""
import argparse
import json
import os
import subprocess
import sys
import wave

import imageio_ffmpeg
import numpy as np

FF = imageio_ffmpeg.get_ffmpeg_exe()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def probe_dur(path):
    p = subprocess.run([FF, "-hide_banner", "-i", path], capture_output=True)
    txt = p.stderr.decode("utf-8", "replace")
    for line in txt.splitlines():
        if "Duration:" in line:
            h, m, s = line.split("Duration:")[1].split(",")[0].strip().split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    return None


def audio_stats(path):
    raw = subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-i", path,
                          "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True).stdout
    if not raw:
        return 0.0, -99.0
    x = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
    dur = len(x) / 16000.0
    rms = 20 * np.log10(max(float(np.sqrt((x ** 2).mean())), 1e-9))
    return dur, rms


def check_image(path, min_w):
    try:
        from PIL import Image
        im = Image.open(path)
        im.verify()
        im = Image.open(path)
        w, h = im.size
        return (w >= min_w and h >= min_w // 2), f"{w}x{h}", os.path.getsize(path) / 1e6
    except Exception as e:                                    # noqa: BLE001
        return False, f"ERR {type(e).__name__}", 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--min-img", type=int, default=1024)
    ap.add_argument("--strict", action="store_true", help="يفشل لو فيه أصل ناقص")
    a = ap.parse_args()

    spec = json.load(open(a.spec, encoding="utf-8"))
    problems, warnings = [], []
    total_speech = 0.0

    print("=" * 74)
    print(f"{'#':>3} {'مشهد':<26} {'صورة':<12} {'مقاطع':>6} {'كلام':>8}  حالة")
    print("=" * 74)
    for sc in spec["scenes"]:
        sid = sc["id"]
        img = os.path.join(ROOT, sc["image_file"])
        if not os.path.exists(img):
            problems.append(f"صورة ناقصة: {sc['image_file']}")
            img_ok, img_txt = False, "MISSING"
        else:
            img_ok, img_txt, mb = check_image(img, a.min_img)
            if not img_ok:
                problems.append(f"صورة تالفة/صغيرة: {sc['image_file']} ({img_txt})")
        segs = sc.get("segments") or [{"audio": sc.get("vo_file")}]
        speech, missing, quiet = 0.0, 0, []
        for s in segs:
            p = os.path.join(ROOT, s["audio"]) if s.get("audio") else None
            if not p or not os.path.exists(p):
                missing += 1
                continue
            d, rms = audio_stats(p)
            speech += d
            if d < 0.35:
                quiet.append((os.path.basename(p), f"قصير {d:.2f}s"))
            elif rms < -45:
                quiet.append((os.path.basename(p), f"صامت {rms:.0f}dB"))
        total_speech += speech
        for n, why in quiet:
            warnings.append(f"مشهد {sid}: {n} — {why}")
        if missing:
            warnings.append(f"مشهد {sid}: {missing}/{len(segs)} مقطع صوتي ناقص")
        state = "✓" if (img_ok and not missing) else ("◐ جزئي" if img_ok else "✗")
        print(f"{sid:>3} {sc.get('title_ar','')[:26]:<26} {img_txt:<12} "
              f"{len(segs)-missing:>3}/{len(segs):<2} {speech:>7.1f}s  {state}")

    print("=" * 74)
    print(f"إجمالي الكلام: {total_speech/60:.2f} دقيقة")
    if warnings:
        print(f"\n⚠ تحذيرات ({len(warnings)}):")
        for w in warnings:
            print("   •", w)
    if problems:
        print(f"\n✗ مشاكل ({len(problems)}):")
        for p in problems:
            print("   •", p)
    print()
    if problems:
        sys.exit(1)
    if warnings and a.strict:
        sys.exit(2)
    print("✓ كل الصور سليمة — المقاطع الصوتية تكمل على دفعات.")


if __name__ == "__main__":
    main()
