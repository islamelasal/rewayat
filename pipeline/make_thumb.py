#!/usr/bin/env python3
"""مولّد الثامبنيل: قصّ 16:9 + تدرّج + نص عربي عبر drawtext (Noto Kufi).

الاستخدام:
  python pipeline/make_thumb.py --image assets/images/ep01/scene-01.png \
      --title "ساعة الرمادي" --kicker "الملحمة بدأت" --tag "الحلقة الأولى" \
      --out assets/images/ep01/thumb-01.jpg
"""
import argparse
import os
import subprocess
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = lambda n: os.path.join(ROOT, "assets", "fonts", n)


def esc(t):
    """تهريب الرموز اللي بتكسر فلتر drawtext."""
    for ch in ("\\", "'", ":", "%"):
        t = t.replace(ch, "\\" + ch)
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--kicker", default="")
    ap.add_argument("--tag", default="")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    vf = [
        "scale=1280:720:force_original_aspect_ratio=increase",
        "crop=1280:720",
        "eq=contrast=1.16:brightness=-0.05:saturation=1.10",
        f"drawtext=fontfile={F('NotoKufiArabic-900.ttf')}:text='{esc(a.kicker)}':fontsize=34:"
        f"fontcolor=0xD8A24A:x=w-text_w-58:y=54:shadowx=0:shadowy=3:shadowcolor=0x000000@0.75",
        f"drawtext=fontfile={F('NotoKufiArabic-900.ttf')}:text='{esc(a.title)}':fontsize=88:"
        f"fontcolor=0xF6F1E9:x=w-text_w-52:y=100:borderw=3:bordercolor=0x0A0A0C:"
        f"shadowx=0:shadowy=5:shadowcolor=0x000000@0.55",
        f"drawtext=fontfile={F('NotoKufiArabic-700.ttf')}:text='{esc(a.tag)}':fontsize=34:"
        f"fontcolor=0xE9DFD2:x=w-text_w-62:y=214:shadowx=0:shadowy=3:shadowcolor=0x000000@0.8",
    ]
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-i", a.image,
                    "-vf", ",".join(vf), "-frames:v", "1", "-q:v", "2", a.out], check=True)
    print("ثامبنيل:", a.out)


if __name__ == "__main__":
    main()
