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


def clean(t):
    """تنظيف الرموز حسب ما هو **متاح فعلًا** في خط Noto Kufi.

    اتقاس بـ fontTools: الخط مفيهوش شرطة (-) ولا — ولا • ولا /  (كلهم بيطلعوا
    مربع فاضي). الموجود: الفاصلة العربية ٬ والنقطة ٫ والمسافة.
    """
    # الشرطة بقت مسافة (مش فاصلة): الفاصلة العربية ٬ شكلها شرطة مائلة فوق
    # السطر، وده بيبان كأنه خطأ إملائي في العنوان. المسافة أنضف بصريًا.
    for bad, good in (("—", " "), ("–", " "), ("\u2013", " "), ("-", " "),
                      ("«", ""), ("»", ""), ("\u200f", ""), ("\u200e", ""),
                      ("•", ""), ("\u00b7", ""), ("/", " "), ("\u204f", "")):
        t = t.replace(bad, good)
    return " ".join(t.split())


def esc(t):
    """تهريب الرموز اللي بتكسر فلتر drawtext."""
    for ch in ("\\", "'", ":", "%"):
        t = t.replace(ch, "\\" + ch)
    return t


def make_gradient(w, h, top_strength=0.66, top_h=0.50,
                  bot_strength=0.58, bot_h=0.42):
    """طبقة سوداء بقناة ألفا متدرجة بسلاسة (منحنى ناعم، مش خطي) — للـ overlay."""
    from PIL import Image
    import numpy as _np
    yy = _np.arange(h, dtype=_np.float32) / max(h - 1, 1)
    t_h = max(int(h * top_h), 1)
    b_h = max(int(h * bot_h), 1)
    ay = _np.zeros(h, dtype=_np.float32)
    # فوق: من 1 عند الحد العلوي إلى 0 عند نهاية المنطقة (منحنى تكعيبي ناعم)
    top = _np.arange(t_h, dtype=_np.float32) / max(t_h - 1, 1)
    ay[:t_h] = _np.maximum(ay[:t_h], (1.0 - top) ** 1.6 * top_strength)
    # تحت
    bot = _np.arange(b_h, dtype=_np.float32) / max(b_h - 1, 1)
    ay[h - b_h:] = _np.maximum(ay[h - b_h:], (bot ** 2.0) * bot_strength)
    alpha = (yy * 0)[:, None] + ay[:, None]
    rgba = _np.zeros((h, w, 4), dtype=_np.uint8)
    rgba[..., 3] = _np.clip(alpha * 255, 0, 255).astype(_np.uint8)
    return Image.fromarray(rgba, "RGBA")


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


GRAD = [None]


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

    title_lines = wrap(clean(a.title))
    title_size = fit_size(title_lines, KUFI900, max_w, int(88 * scale))
    kicker_lines = wrap(clean(a.kicker)) if a.kicker else []
    kicker_size = fit_size(kicker_lines, KUFI900, max_w, int(34 * scale)) if kicker_lines else 0
    tag_size = fit_size([a.tag], KUFI700, max_w, int(34 * scale)) if a.tag else 0

    line_h = int(title_size * 1.22)
    y = int(54 * scale)

    vf = [
        f"scale={W}:{H}:force_original_aspect_ratio=increase",
        f"crop={W}:{H}",
        "eq=contrast=1.16:brightness=-0.05:saturation=1.10",
    ]

    # تدرّج غامق ناعم فوق وتحت.
    # ملاحظة: شرائح drawbox كانت بتعمل خطوط أفقية على السما الفاتحة (كل شريحة
    # بتحط حافة صلبة فوق اللي قبلها). الحل: تدرّج واحد متصل على صورة رمادية
    # بـ PIL، ونستخدمه كـ overlay — ناعم ١٠٠٪ ومفيهوش أي حدود.
    grad_top = make_gradient(W, H, top_strength=0.66, top_h=0.50,
                             bot_strength=0.58, bot_h=0.42)
    grad_path = os.path.join(os.path.dirname(os.path.abspath(a.out)), ".grad.png")
    grad_top.save(grad_path)
    GRAD[0] = grad_path

    for i, line in enumerate(kicker_lines):
        vf.append(
            f"drawtext=fontfile={KUFI900}:text='{esc(clean(line))}':fontsize={kicker_size}:"
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
            f"drawtext=fontfile={KUFI900}:text='{esc(clean(line))}':fontsize={title_size}:"
            f"fontcolor=0xF6F1E9:x=w-text_w-{margin}:y={ly}:"
            f"borderw=3:bordercolor=0x0A0A0C:shadowx=0:shadowy=5:shadowcolor=0x000000@0.55"
        )
    y += len(title_lines) * line_h + int(10 * scale)

    if a.tag:
        vf.append(
            f"drawtext=fontfile={KUFI700}:text='{esc(clean(a.tag))}':fontsize={tag_size}:"
            f"fontcolor=0xE9DFD2:x=w-text_w-{margin}:y={y}:"
            f"shadowx=0:shadowy=3:shadowcolor=0x000000@0.85"
        )

    if GRAD[0]:
        # سلسلة الفلاتر الأساسية + طبقة التدرّج كمدخل تاني (بلا movie=)
        chain = ",".join(x for x in vf)
        cmd = [FF, "-hide_banner", "-loglevel", "error", "-y",
               "-i", a.image, "-loop", "1", "-i", GRAD[0],
               "-filter_complex",
               f"[0:v]{chain}[base];[base][1:v]overlay=0:0:format=auto[v]",
               "-map", "[v]", "-frames:v", "1", "-q:v", "2", a.out]
    else:
        cmd = [FF, "-hide_banner", "-loglevel", "error", "-y", "-i", a.image,
               "-vf", ",".join(vf), "-frames:v", "1", "-q:v", "2", a.out]
    subprocess.run(cmd, check=True)
    print(f"ثامبنيل: {a.out}  ({W}x{H}, عنوان {title_size}px, {len(title_lines)} سطر)")


if __name__ == "__main__":
    main()
