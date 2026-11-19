#!/usr/bin/env python3
"""
يقص شورتات عمودية 9:16 من الحلقة الكاملة + يعمل كوفر لكل واحد.

الطريقة: بنفس تعليمات الـ ASS المحروقة (عشان الترجمة تتحرق جوه الشورت)،
مع تحويل ذكي للإطار: الصورة الأصلية 16:9 بتتقصّ لنسبة 9:16 مع تعقّب
المنطقة المهمة (وسط أعلى)، وترجمة الشورت بتتحرك لفوق عشان تبان.

  python pipeline/shorts.py <ep.mp4> <subs.ass> --outdir output/dl/shorts
"""
import argparse
import json
import os
import subprocess
import sys

import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (اسم, بداية, نهاية, كابشن الكوفر, نص فوق الكوفر)
DEFAULT_SHORTS = [
    ("01-هوك",       7.20,  57.2,  "الملحمة بدأت", "سمع كلمة واحدة في الراديو",
     "assets/images/ep01/scene-01.png"),
    ("02-الملحمة",  539.0, 599.0,  "مئات وقفوا",   "وما حدش اتكلم",
     "assets/images/ep01/scene-07.png"),
    ("03-خط-ذهبي",  784.0, 844.0,  "السما تتشقّق", "أول مرة",
     "assets/images/ep01/scene-10.png"),
]


def ffprobe_dur(path):
    p = subprocess.run([FF, "-hide_banner", "-i", path], capture_output=True)
    for line in p.stderr.decode("utf-8", "replace").splitlines():
        if "Duration:" in line:
            h, m, s = line.split("Duration:")[1].split(",")[0].strip().split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise SystemExit("لا يمكن قراءة المدة")


def make_short(src, ass, start, dur, out, workdir):
    """قصّ عمودي 1080x1920 + حرق الترجمة (بتتحرك لفوق عشان متتقصّش)."""
    # ترجمة الشورت: نفس الأسطر لكن منطقة آمنة أعلى (1420 بدل 634)
    short_ass = os.path.join(workdir, os.path.basename(out) + ".ass")
    with open(ass, encoding="utf-8") as f:
        txt = f.read()
    # الترجمة محسوبة على 1280x720 (أفقي). للشورت العمودي 1080x1920:
    #   - نكبّر نظام الإحداثيات ونكبّر الخطوط معاه (عشان تبان على موبايل)
    #   - الترجمة تتنقل لفوق (y~1400) بعيد عن واجهة يوتيوب السفلية
    #   - نشيل كروت العنوان/النهاية: الشورت مش محتاجها، وبتزحم الشاشة
    keep = []
    for line in txt.splitlines():
        if not line.startswith("Dialogue:"):
            keep.append(line)
            continue
        is_card = ",Title," in line or ",Small," in line
        if is_card:
            continue
        keep.append(line)
    txt = "\n".join(keep)

    txt = (txt.replace("PlayResX: 1280", "PlayResX: 1080")
              .replace("PlayResY: 720", "PlayResY: 1920")
              .replace("\\pos(640,634)", "\\pos(540,1420)")
              .replace(",110,110,60,", ",50,50,200,")
              .replace("Noto Naskh Arabic,32,", "Noto Naskh Arabic,46,"))

    with open(short_ass, "w", encoding="utf-8") as f:
        f.write(txt)

    # نقصّ الشريط السفلي من المصدر (فيه الترجمة المحروقة الأصلية)
    # عشان منجيبش ترجمتين فوق بعض، وبعدها نحرق ترجمة الشورت في مكانها الصح.
    vf = (
        "crop=iw:trunc(ih*0.88/2)*2:0:0,"
        "scale=-2:1920:flags=lanczos,setsar=1,"
        "crop=1080:1920,setsar=1,"
        f"subtitles={short_ass}:fontsdir={os.path.join(ROOT, 'assets/fonts')},"
        "format=yuv420p"
    )
    cmd = [
        FF, "-hide_banner", "-loglevel", "error", "-y",
        "-ss", f"{start:.2f}", "-t", f"{dur:.2f}", "-i", src,
        "-vf", vf,
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-movflags", "+faststart", out,
    ]
    subprocess.run(cmd, check=True)
    return out


def make_cover(short_name, caption, kicker, src_image, out_jpg, workdir):
    """كوفر 1080x1920 من **صورة المشهد الأصلية** (نظيفة، بدون ترجمة محروقة)."""
    frame = src_image
    # نستخدم make_thumb.py لتوليد النص العربي بشكل صحيح
    subprocess.run([sys.executable, os.path.join(ROOT, "pipeline", "make_thumb.py"),
                    "--image", frame, "--title", caption, "--kicker", kicker,
                    "--size", "1080x1920", "--out", out_jpg], check=True)
    return out_jpg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("ass")
    ap.add_argument("--outdir", default=os.path.join(ROOT, "output/dl/shorts"))
    ap.add_argument("--workdir", default="/tmp/shorts_build")
    a = ap.parse_args()

    os.makedirs(a.outdir, exist_ok=True)
    os.makedirs(a.workdir, exist_ok=True)

    total = ffprobe_dur(a.video)
    made = []
    for name, s, e, cap, kick, image in DEFAULT_SHORTS:
        # اقصّر المدة لو النهاية تعدّي الفيديو
        dur = min(e, total - 0.5) - s
        if dur < 12:
            print(f"[!] تخطّي {name}: المدة قصيرة ({dur:.0f}s)")
            continue
        out = os.path.join(a.outdir, f"{name}.mp4")
        print(f"[i] شورت {name}: {s:.0f}s → {s+dur:.0f}s ({dur:.0f}s)")
        make_short(a.video, a.ass, s, dur, out, a.workdir)
        cover = os.path.join(a.outdir, f"{name}-كوفر.jpg")
        make_cover(name, cap, kick, os.path.join(ROOT, image), cover, a.workdir)
        made.append((name, out, cover, dur))

    print("\n[✓] خلص:")
    for name, out, cover, dur in made:
        print(f"  {os.path.basename(out)}  ({dur:.0f}s)  + {os.path.basename(cover)}")


if __name__ == "__main__":
    main()
