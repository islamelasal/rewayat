#!/usr/bin/env python3
"""
ثامبنيل/كوفر بنص عربي — مع قياس حقيقي لعرض النص عشان ميتقصّش.

  python pipeline/make_thumb.py --image scene.png --title "الملحمة بدأت" \
      --kicker "سمع كلمة واحدة" --size 1080x1920 --out cover.jpg

- العنوان بيتقسم لسطور عند \n أو تلقائياً لو طويل.
- حجم الخط بيتصغّر تلقائياً لحد ما يدخل في العرض المتاح (بقياس PIL الحقيقي).
- كل حاجة من اليمين (RTL) والخط Noto Kufi 900.
"""
import argparse
import os
import subprocess

import imageio_ffmpeg
from PIL import ImageFont

FF = imageio_ffmpeg.get_ffmpeg_exe()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, "assets", "fonts")

KUFI900 = os.path.join(FONT_DIR, "NotoKufiArabic-900.ttf")
KUFI700 = os.path.join(FONT_DIR, "NotoKufiArabic-700.ttf")


def esc(t):
    """تهريب الرموز اللي بتكسر فلتر drawtext."""
    for ch in ("\\", "'", ":", "%"):
        t = t.replace(ch, "\\" + ch)
    return t


def text_width(txt, font_path, size):
    """عرض النص الحقيقي بالبكسل (قياس PIL — مش تقدير)."""
    try:
        f = ImageFont.truetype(font_path, size)
        return float(f.getlength(txt))
    except Exception:
        return len(txt) * size * 0.55


def fit_size(lines, font_path, max_w, start):
    """يصغّر الخط لحد ما أطول سطر يدخل في max_w."""
    size = start
    while size > 20:
        if max(text_width(l, font_path, size) for l in lines) <= max_w:
            return size
        size -= 2
    return 20


def wrap(txt, max_chars=22):
    """يقسّم النص لسطور متوازنة لو مفيش \\n."""
    if "\n" in txt:
        return txt.split("\n")
    words = txt.split()
    if len(words) <= 2:
        return [txt]
    mid = (len(words) + 1) // 2
    return [" ".join(words[:mid]), " ".join(words[mid:])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--kicker", default="")
    ap.add_argument("--tag", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--size", default="1280x720")
    ap.add_argument("--max-width-pct", type=float, default=0.88,
                    help="أقصى عرض للنص كنسبة من عرض الكانفس")
    a = ap.parse_args()

    W, H = (int(x) for x in a.size.lower().split("x"))
    scale = W / 1280.0
    margin = int(W * (1 - a.max_width_pct) / 2)
    max_w = W - 2 * margin

    title_lines = wrap(a.title)
    title_size = fit_size(title_lines, KUFI900, max_w, int(88 * scale))
    kicker_lines = wrap(a.kicker) if a.kicker else []
    kicker_size = fit_size(kicker_lines, KUFI900, max_w, int(34 * scale)) if kicker_lines else 0
    tag_size = fit_size([a.tag], KUFI700, max_w, int(34 * scale)) if a.tag else 0

    line_h = int(title_size * 1.22)
    y = int(54 * scale)

    vf = [
        f"scale={W}:{H}:force_original_aspect_ratio=increase",
        f"crop={W}:{H}",
        "eq=contrast=1.16:brightness=-0.05:saturation=1.10",
    ]

    # تدرّج غامق ناعم فوق وتحت (شرائح رفيعة بألفا متزايدة — مفيش خط واضح)
    BANDS = 28
    top_h = int(H * 0.46)
    for i in range(BANDS):
        band_y = int(i * top_h / BANDS)
        band_h = max(1, int(top_h / BANDS) + 1)
        alpha = 0.62 * (1 - i / (BANDS - 1)) ** 1.4
        vf.append(f"drawbox=x=0:y={band_y}:w={W}:h={band_h}:"
                  f"color=black@{alpha:.3f}:t=fill")
    bot_h = int(H * 0.38)
    for i in range(BANDS):
        band_y = int(H - bot_h + i * bot_h / BANDS)
        band_h = max(1, int(bot_h / BANDS) + 1)
        alpha = 0.55 * (i / (BANDS - 1)) ** 1.2
        vf.append(f"drawbox=x=0:y={band_y}:w={W}:h={band_h}:"
                  f"color=black@{alpha:.3f}:t=fill")

    for i, line in enumerate(kicker_lines):
        vf.append(
            f"drawtext=fontfile={KUFI900}:text='{esc(line)}':fontsize={kicker_size}:"
            f"fontcolor=0xD8A24A:x=w-text_w-{margin}:"
            f"y={y + i * int(kicker_size * 1.3)}:"
            f"shadowx=0:shadowy=3:shadowcolor=0x000000@0.8"
        )
    if kicker_lines:
        y += len(kicker_lines) * int(kicker_size * 1.3) + int(8 * scale)

    # كل سطر عنوان لوحده (drawtext مش بيفهم \n) — وكلهم من اليمين
    for i, line in enumerate(title_lines):
        ly = y + i * line_h
        vf.append(
            f"drawtext=fontfile={KUFI900}:text='{esc(line)}':fontsize={title_size}:"
            f"fontcolor=0xF6F1E9:x=w-text_w-{margin}:y={ly}:"
            f"borderw=3:bordercolor=0x0A0A0C:shadowx=0:shadowy=5:shadowcolor=0x000000@0.55"
        )
    y += len(title_lines) * line_h + int(10 * scale)

    if a.tag:
        vf.append(
            f"drawtext=fontfile={KUFI700}:text='{esc(a.tag)}':fontsize={tag_size}:"
            f"fontcolor=0xE9DFD2:x=w-text_w-{margin}:y={y}:"
            f"shadowx=0:shadowy=3:shadowcolor=0x000000@0.85"
        )

    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-i", a.image,
                    "-vf", ",".join(vf), "-frames:v", "1", "-q:v", "2", a.out], check=True)
    print(f"ثامبنيل: {a.out}  ({W}x{H}, عنوان {title_size}px, {len(title_lines)} سطر)")


if __name__ == "__main__":
    main()
