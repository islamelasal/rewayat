#!/usr/bin/env python3
"""
مُحرّك إنتاج حلقات "رواية" — يبني فيديو 1080p كامل من:
  - scenes.json  (النص + وصف الصورة + نوع الحركة)
  - assets/images/epXX/scene-NN.png
  - assets/audio/epXX/scene-NN.mp3

كل حاجة بتتولد محلياً: حركة كاميرا (zoom/pan) + طبقة ضباب متحركة + فينييت
+ شريط صوتي (drone + رياح + نقرات) + ترجمة ASS عربية متزامنة + سبيكترم صوتي.

الاستخدام:
  python pipeline/render.py episodes/01-الرمادي/scenes.json --out output/rewayat-ep01.mp4
  python pipeline/render.py ... --preview 30   # أول 30 ثانية بس للاختبار
"""
import argparse
import json
import math
import os
import subprocess
import sys
import wave

import imageio_ffmpeg
import numpy as np
import arabic_reshaper
from bidi.algorithm import get_display

FF = imageio_ffmpeg.get_ffmpeg_exe()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, "assets", "fonts")
import dialogue as dialogue_engine   # noqa: E402  (تجميع مقاطع السرد/الحوار)
W, H = 1920, 1080
FPS = 24
SR = 48000

# ---------------------------------------------------------------- utils


def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        sys.stderr.write(" ".join(cmd)[:2000] + "\n")
        sys.stderr.write(p.stderr.decode("utf-8", "replace")[-4000:] + "\n")
        raise SystemExit(f"ffmpeg failed ({p.returncode})")
    return p.stdout


def dur(path):
    out = run([FF, "-hide_banner", "-i", path]).decode("utf-8", "replace") if False else None
    p = subprocess.run([FF, "-hide_banner", "-i", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    txt = p.stderr.decode("utf-8", "replace")
    for line in txt.splitlines():
        if "Duration:" in line:
            h, m, s = line.split("Duration:")[1].split(",")[0].strip().split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise SystemExit(f"no duration for {path}")


def rtl(s):
    """نص عربي خام. libass/ffmpeg هو اللي بيعمل التشكيل والترتيب البصري
    (شغال صح مع Cairo)، فأي preprocessing بيعمل عكس مزدوج."""
    return s


# ---------------------------------------------------------------- audio bed


def wind(n, sr=SR, seed=7):
    """رياح: نويز منخفض الترددات بمعدل تغيّر بطيء."""
    rng = np.random.default_rng(seed)
    white = rng.standard_normal(n)
    # مرشّح تمرير منخفض بسيط (متوسط متحرك) لصنع هدير
    k = 400
    ker = np.hanning(k)
    ker /= ker.sum()
    low = np.convolve(white, ker, mode="same")
    # تعديل السعة بموجة بطيئة (هبّات رياح)
    t = np.arange(n) / sr
    env = 0.55 + 0.45 * np.sin(2 * np.pi * 0.055 * t + 1.1) * np.sin(2 * np.pi * 0.021 * t)
    return low * env


def drone(n, sr=SR, freqs=(55.0, 82.5, 110.0, 164.8)):
    """درون وترى منخفض للتوتّر."""
    t = np.arange(n) / sr
    sig = np.zeros(n)
    for i, f in enumerate(freqs):
        det = 1 + 0.0016 * np.sin(2 * np.pi * (0.03 + 0.011 * i) * t)
        sig += (0.9 / (i + 1.4)) * np.sin(2 * np.pi * f * det * t + i)
    swell = 0.5 + 0.5 * np.sin(2 * np.pi * 0.017 * t - 0.6)
    return sig * (0.45 + 0.55 * swell)


def heartbeat(n, sr=SR, bpm=54.0):
    """نبض قلب: نقرتين + سكتة."""
    t = np.arange(n) / sr
    period = 60.0 / bpm
    out = np.zeros(n)
    for start in np.arange(0, n / sr, period):
        for k, amp in ((0.0, 1.0), (0.32, 0.65)):
            s0 = int((start + k) * sr)
            ln = int(0.16 * sr)
            if s0 + ln >= n:
                continue
            tt = np.arange(ln) / sr
            env = np.exp(-tt * 26)
            beat = np.sin(2 * np.pi * 48 * tt) * env * amp
            out[s0:s0 + ln] += beat
    return out


def tick(n, sr=SR, every=2.6, seed=3):
    """نقرات راديو/ساعة خفيفة جداً."""
    rng = np.random.default_rng(seed)
    out = np.zeros(n)
    for s in np.arange(1.5, n / sr, every):
        s0 = int(s * sr)
        ln = int(0.05 * sr)
        if s0 + ln >= n:
            continue
        tt = np.arange(ln) / sr
        out[s0:s0 + ln] += np.sin(2 * np.pi * 1750 * tt) * np.exp(-tt * 90) * 0.5
        out[s0:s0 + ln] += rng.standard_normal(ln) * np.exp(-tt * 140) * 0.2
    return out


def crossfade_norm(x):
    m = np.max(np.abs(x)) or 1.0
    return x / m


# ---------------------------------------------------------------- subtitles


def fmt_ts(x):
    h = int(x // 3600)
    m = int((x % 3600) // 60)
    s = x % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def chunk_vo(text, start, end, max_chars=62):
    """تقسيم النص لفقرات ترجمة حسب طول الجملزمنياً."""
    parts, cur = [], ""
    for tok in text.split():
        if len(cur) + len(tok) + 1 <= max_chars:
            cur = (cur + " " + tok).strip()
        else:
            if cur:
                parts.append(cur)
            cur = tok
    if cur:
        parts.append(cur)
    total_chars = sum(len(p) for p in parts) or 1
    out, t = [], start
    for p in parts:
        share = (end - start) * len(p) / total_chars
        out.append((t, min(t + share, end), p))
        t += share
    return out


SUB_W, SUB_H = 1280, 720

ASS_HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Noto Naskh Arabic,39,&H00F2EDE4,&H00FFFFFF,&H00120F0C,&H99000000,0,0,0,0,100,100,0,0,1,1.5,0.9,8,110,110,60,1
Style: Fouad,Noto Naskh Arabic,39,&H00A8D8F0,&H00FFFFFF,&H00120F0C,&H99000000,0,0,0,0,100,100,0,0,1,1.6,1.0,8,110,110,60,1
Style: FouadName,Noto Kufi Arabic,25,&H0090C4DC,&H00FFFFFF,&H00120F0C,&H66000000,0,0,0,0,100,100,0,0,1,1.0,0,8,110,110,96,1
Style: Title,Noto Kufi Arabic,54,&H00F6F1E9,&H00FFFFFF,&H00000000,&H99000000,0,0,0,0,100,100,0,0,1,2,2,8,40,40,0,1
Style: Small,Noto Naskh Arabic,24,&H00C9B7AC,&H00FFFFFF,&H00000000,&H99000000,0,0,0,0,100,100,0,0,1,0.8,0,8,40,40,30,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


NEXT_LINE = {
    1: "«اللي قال: أنا جيت أريّحكم»",
    2: "«الراجل اللي طلع في الشرق»",
    3: "«اللي هييجي بعد كده… فيه حاجة غلط»",
}


def next_line(scenes):
    ep = scenes[0].get("episode", 1) if scenes else 1
    return NEXT_LINE.get(ep, "الحلقة القادمة")


def build_ass(scenes, total, out_path):
    lines = [ASS_HEAD.format(w=SUB_W, h=SUB_H)]
    for sc in scenes:
        # (تم إلغاء عنوان الفصل أعلى الشاشة: تشويش بصري وتقليل تركيز)
        segs = sc.get("_timings")            # توقيتات مقاطع السرد/الحوار (إن وُجدت)
        if segs:
            for t0, t1, seg in segs:
                a = sc["start"] + t0 + 0.10
                b = sc["start"] + t1 - 0.06
                if b - a < 0.5:
                    continue
                is_f = (seg.get("speaker") == "فؤاد")
                style = "Fouad" if is_f else "Sub"
                for ca, cb, txt in chunk_vo(seg["text"], a, b, max_chars=58):
                    if cb - ca < 0.55:
                        continue
                    lines.append(
                        f"Dialogue: 0,{fmt_ts(ca)},{fmt_ts(cb)},{style},,0,0,0,,"
                        f"{rtl(txt)}{{\\fad(180,180)\\pos({SUB_W//2},642)}}"
                    )
                # اسم المتكلم فوق السطر لما يكون حوار
                if seg.get("kind") == "dialogue" and is_f:
                    lines.append(
                        f"Dialogue: 0,{fmt_ts(a)},{fmt_ts(min(a+1.8, b))},FouadName,,0,0,0,,"
                        f"{rtl(seg['speaker'])}{{\\fad(200,300)\\pos({SUB_W//2},578)}}"
                    )
            continue
        for a, b, txt in chunk_vo(sc["vo"], sc["start"] + 0.25, sc["end"] - 0.25):
            if b - a < 0.6:
                continue
            lines.append(
                f"Dialogue: 0,{fmt_ts(a)},{fmt_ts(b)},Sub,,0,0,0,,{rtl(txt)}{{\\fad(200,200)\\pos({SUB_W//2},642)}}"
            )
    # كارت البداية
    lines.append(
        f"Dialogue: 1,{fmt_ts(0.8)},{fmt_ts(6.5)},Title,,0,0,0,,{rtl('ساعة الرمادي')}{{\\fad(900,900)\\pos({SUB_W//2},196)}}"
    )
    lines.append(
        f"Dialogue: 1,{fmt_ts(1.8)},{fmt_ts(6.5)},Small,,0,0,0,,{rtl('الحلقة الأولى — الملحمة بدأت')}{{\\fad(900,900)\\pos({SUB_W//2},272)}}"
    )
    # كارت النهاية
    lines.append(
        f"Dialogue: 1,{fmt_ts(total-10)},{fmt_ts(total-1.5)},Title,,0,0,0,,{rtl('الحلقة القادمة')}{{\\fad(800,900)\\pos({SUB_W//2},200)\\fs44}}"
    )
    nxt = next_line(scenes)
    lines.append(
        f"Dialogue: 1,{fmt_ts(total-9.4)},{fmt_ts(total-1.5)},Small,,0,0,0,,{rtl(nxt)}{{\\fad(800,900)\\pos({SUB_W//2},276)}}"
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")



# ---------------------------------------------------------------- intro

# ملاحظة: خط Noto مفيهوش علامات تنصيص ولا أقواس (بتطلع مربع فاضي) —
# فالكلام مكتوب من غيرها، والفواصل العربية بتعمل الشغل.
INTRO_LINES = [
    ("الحلقة السابقة", "الملحمة بدأت، راجل عجوز في الراديو، وشارع كله بيبص لفوق"),
    ("الحلقة دي", "ياسين خرج يدوّر على إجابة، ولقى فؤاد"),
    ("وخد بالك", "فيه جملة واحدة في الحلقة دي، لو سمعتها هتفهم كل حاجة"),
]


def _dt(t):
    """تهريب نص drawtext + تنظيف الرموز اللي الخط مش فيه (بتطلع مربع فاضي).

    اتأكدنا بـ fontTools إن خطوط Noto هنا مفيهاش ولا علامة ترقيم لاتينية،
    فالوقف بيبقى بالنقطة العربية ٫ (موجودة ومقروءة).
    """
    t = t.replace("…", "٫").replace(".", "٫")
    for bad in ("«", "»", '"', "(", ")", "[", "]", "—", "–", "-", "•", ":", "،"):
        t = t.replace(bad, "٬" if bad in ":،-—–" else "")
    t = " ".join(t.split())
    for ch in ("\\", "'", ":", "%"):
        t = t.replace(ch, "\\" + ch)
    return t


def build_intro_card(out_path, seconds, w=W, h=H, fps=FPS):
    """كارت تمهيدي (بلا صوت) — النص بيتحط بـ ffmpeg drawtext مش PIL.

    PIL بيرسم الحروف العربية منفصلة ومقلوبة (مش بيعمل shaping)، فكل النص
    العربي لازم يعدّي على libass/drawtext. هنا بنجهّز الخلفية PIL ونكتب
    الكلام بـ drawtext + text_shaping=1.
    """
    from PIL import Image
    import numpy as _np

    img = Image.open(os.path.join(ROOT, "assets", "images", "ep02", "scene-02.png")).convert("RGB")
    base = img.resize((w, h), Image.LANCZOS)
    arr = _np.asarray(base).astype(_np.float32)
    arr = arr * 0.16 + (_np.array([12, 13, 16], dtype=_np.float32) * 0.84)
    Image.fromarray(arr.clip(0, 255).astype(_np.uint8)).save(out_path)

    kufi = os.path.join(FONT_DIR, "NotoKufiArabic-900.ttf")
    naskh = os.path.join(FONT_DIR, "NotoNaskhArabic-400.ttf")
    y = int(h * 0.26)
    vf = []
    for head, body in INTRO_LINES:
        vf.append(
            f"drawtext=fontfile={kufi}:text='{_dt(head)}':fontsize=38:"
            f"fontcolor=0xD8A24A:x=(w-text_w)/2:y={y}:text_shaping=1"
        )
        vf.append(
            f"drawtext=fontfile={naskh}:text='{_dt(body)}':fontsize=42:"
            f"fontcolor=0xE9E2D6:x=(w-text_w)/2:y={y+56}:text_shaping=1"
        )
        y += int(h * 0.185)

    vf += [
        f"zoompan=z='1.0+0.00030*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d=1:s={w}x{h}:fps={fps}",
        "setsar=1", "format=yuv420p",
        f"fade=t=in:st=0:d=0.8", f"fade=t=out:st={max(seconds-0.8,0):.2f}:d=0.8",
    ]
    mp4 = out_path.replace(".png", ".mp4")
    r = subprocess.run(
        [FF, "-hide_banner", "-loglevel", "error", "-y", "-loop", "1", "-i", out_path,
         "-t", f"{seconds:.2f}", "-r", str(fps), "-vf", ",".join(vf),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
         "-pix_fmt", "yuv420p", mp4],
        capture_output=True)
    if r.returncode != 0:
        print(r.stderr.decode("utf-8", "replace")[-800:])
    return r.returncode == 0


# ---------------------------------------------------------------- video


def scene_clip(sc, out_path, preview=None):
    """رندر مشهد واحد: صورة + حركة كاميرا + غبار متحرك + جْرين خفيف + فينييت."""

    d = sc["end"] - sc["start"]
    if preview is not None:
        d = min(d, preview)
    if sc.get("_pad"):
        d += sc["_pad"]
    frames = max(int(round(d * FPS)), 2)
    img = sc["image"]
    kind = sc.get("motion", "slow_zoom_in")

    if kind == "slow_zoom_in":
        z, x, y = "1.03+0.0012*on", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif kind == "slow_zoom_out":
        z, x, y = "1.14-0.0012*on", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif kind == "pan_right":
        z = "1.11"
        x, y = "iw/2-iw/zoom/2+(iw*0.016)*on/%d" % frames, "ih/2-(ih/zoom/2)"
    elif kind == "pan_left":
        z = "1.11"
        x, y = "iw/2-iw/zoom/2-(iw*0.016)*on/%d" % frames, "ih/2-(ih/zoom/2)"
    elif kind == "push_up":
        z = "1.07"
        x, y = "iw/2-(iw/zoom/2)", "ih/2-ih/zoom/2-(ih*0.010)*on/%d" % frames
    else:
        z, x, y = "1.05", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"

    # ملاحظة: blend/eq/vignette ممكن تعمل إزاحة لونية حسب ترتيب التحويل،
    # فبنسيب الشغل اللوني في مساحة gbrp وبعدها نحول لـ yuv420p مرة واحدة.
    vf = (
        "scale=2400:-2:flags=lanczos,crop=2400:1350,"
        f"zoompan=z='{z}':x='{x}':y='{y}':d=1:s={W}x{H}:fps={FPS},setsar=1,"
        "format=gbrp,"
        "unsharp=5:5:0.6:5:5:0.0,"
        "vignette=PI/5.0,"
        "eq=contrast=1.12:brightness='-0.004+0.010*sin(2*PI*t*0.09)':saturation=1.06:gamma=0.98,"
        "colorbalance=rs=-.020:bs=.028:rm=-.012:bm=.016,"
        "noise=alls=5:allf=t,"
        "fade=t=in:st=0:d=0.45:color=black,"
        f"fade=t=out:st={max(d-0.55,0):.2f}:d=0.55:color=black,"
        "format=yuv420p"
    )

    cmd = [
        FF, "-hide_banner", "-loglevel", "error", "-y",
        "-loop", "1", "-i", img,
        "-vf", vf, "-t", f"{d:.3f}",
        "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
        "-pix_fmt", "yuv420p", "-g", str(FPS * 2), out_path,
    ]
    run(cmd)
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scenes")
    ap.add_argument("--out", required=True)
    ap.add_argument("--preview", type=float, default=None, help="ثواني فقط للاختبار")
    ap.add_argument("--workdir", default=None)
    args = ap.parse_args()

    spec_path = args.scenes
    epdir = os.path.dirname(spec_path)
    spec = json.load(open(spec_path, encoding="utf-8"))
    items = spec["scenes"]
    work = args.workdir or os.path.join(epdir, "_build")
    os.makedirs(work, exist_ok=True)

    # ---- مدد الصوت: تجميع مقاطع السرد/الحوار لكل مشهد (مع توقيتات)
    os.makedirs(os.path.join(ROOT, "assets", "audio", "build"), exist_ok=True)
    t = 0.0
    scenes = []
    for i, sc in enumerate(items, 1):
        sc = dict(sc)
        lead = sc.get("lead", 0.55)
        tail = sc.get("tail", 1.25)
        if sc.get("segments"):
            vo_path = os.path.join(work, f"vo-{sc['id']:02d}.wav")
            d, tim = dialogue_engine.assemble_scene(sc, vo_path)
            sc["_timings"] = tim
            # نص المشهد كامل (للـ chunk/timecode فقط)
            sc["vo"] = " ".join(s["text"] for s in sc["segments"])
        else:
            vo_path = os.path.join(ROOT, sc["vo_file"])
            d = dur(vo_path)
        sc["audio"] = vo_path
        sc["image"] = os.path.join(ROOT, sc["image_file"])
        sc["start"] = t
        sc["end"] = t + lead + d + tail
        sc["episode"] = spec.get("episode", 1)
        t = sc["end"]
        scenes.append(sc)

    total = t
    if args.preview:
        total = min(total, args.preview)
    print(f"[i] عدد المشاهد: {len(scenes)} | المدة الإجمالية: {total/60:.2f} دقيقة")

    # ---- ترجمة
    ass = os.path.join(work, "subs.ass")
    build_ass(scenes, total, ass)

    # ---- مقدمة تمهيدية (لو محددة في السكربت) — بتوسّع الفيلم فوق 8 دقايق
    intro = float(spec.get("intro_seconds", 0) or 0)
    if intro > 0 and not args.preview:
        for sc in scenes:
            sc["start"] += intro
            sc["end"] += intro
        total += intro

    # ---- الصوت: محرك احترافي (stems + ducking + EBU R128 mastering)
    print("[i] معالجة الصوت (voice stem → music stem → ducking → mastering)...")
    wav = os.path.join(work, "mix.wav")
    import audio as audio_engine  # pipeline/audio.py
    import sfx as sfx_engine      # pipeline/sfx.py
    audio_engine.build_voice_stem(scenes, total, wav + ".voice.wav")
    audio_engine.build_music_stem(scenes, total, wav + ".music.wav")
    sfx_path = os.path.join(work, "sfx.wav")
    sfx_engine.build(scenes, total, sfx_path)
    audio_engine.mix_and_master(wav + ".voice.wav", wav + ".music.wav", wav, total,
                                sfx_wav=sfx_path)
    os.remove(wav + ".voice.wav")
    os.remove(wav + ".music.wav")
    m = audio_engine.measure_loudness(wav)
    print(f"[i] الميكس: {float(m['input_i']):.1f} LUFS / {float(m['input_tp']):.1f} dBTP")

    # ---- رندر المشاهد
    XF = 0.65          # مدة الانتقال بين المشاهد
    clips, rendered = [], []
    for i, sc in enumerate(scenes, 1):
        if sc["start"] >= total:
            break
        local = dict(sc)
        if not args.preview:
            local["_pad"] = XF      # هيتشال من الأخير بعد الحلقة
        if intro > 0 and i == 1:
            local["_pad"] = 0.0     # المقدمة بتوصل بقطع مش xfade
        if args.preview:
            local["_timings"] = [tt for tt in sc.get("_timings", []) if tt[0] < args.preview]
        if args.preview:
            local["end"] = min(local["end"], args.preview)
            if local["end"] - local["start"] < 0.4:
                break
        out = os.path.join(work, f"clip-{i:02d}.mp4")
        if not (os.path.exists(out) and os.path.getmtime(out) > os.path.getmtime(sc["image"])):
            print(f"[i] رندر مشهد {i}/{len(scenes)} ({local['end']-local['start']:.1f}s)")
            scene_clip(local, out, preview=args.preview)
        clips.append(out)
        rendered.append(local)

    if intro > 0 and not args.preview:
        card_png = os.path.join(work, "intro.png")
        ok = build_intro_card(card_png, intro)
        if ok:
            card_mp4 = card_png.replace(".png", ".mp4")
            real = dur(card_mp4)          # المدة الفعلية بعد الرندر
            clips.insert(0, card_mp4)
            rendered.insert(0, {"start": 0.0, "end": real, "_pad": 0.0, "image": card_png})
            print(f"[i] مقدمة {intro:.1f}s")
        else:
            print("[!] المقدمة فشلت — الفيلم هيكمل من غيرها")

    if len(rendered) > 1:
        rendered[-1]["_pad"] = 0.0      # الأخير مش محتاج مساحة انتقال

    # ---- دمج بانتقالات ناعمة (xfade) بدل القطع الفاصل
    print("[i] دمج المشاهد بانتقالات ناعمة...")
    concat = os.path.join(work, "video.mp4")
    if len(clips) == 1:
        run([FF, "-hide_banner", "-loglevel", "error", "-y", "-i", clips[0],
             "-c", "copy", concat])
    else:
        cmd = [FF, "-hide_banner", "-loglevel", "error", "-y"]
        for c in clips:
            cmd += ["-i", c]
        # مدة كل مقطع بعد fades — نستخدم مدد المشاهد المحسوبة
        durs = [min(sc["end"], total) - sc["start"] + sc.get("_pad", 0.0) for sc in rendered]
        parts, prev = [], "0:v"
        acc = durs[0]
        for i in range(1, len(clips)):
            out = f"vx{i}" if i < len(clips) - 1 else "vout"
            parts.append(f"[{prev}][{i}:v]xfade=transition=fade:duration={XF}:"
                         f"offset={max(acc - XF, 0):.3f}[{out}]")
            prev = out
            acc += durs[i] - XF
        run(cmd + ["-filter_complex", ";".join(parts), "-map", f"[{prev}]",
                   "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
                   "-pix_fmt", "yuv420p", concat])

    # ---- المدة النهائية = مجموع المقاطع الفعلية (بعد xfade) مش الحساب النظري
    real_total = sum(sc["end"] - sc["start"] + sc.get("_pad", 0.0) for sc in rendered)
    if len(rendered) > 1:
        real_total -= XF * (len(rendered) - 1)
    if abs(real_total - total) > 0.05:
        print(f"[i] ضبط المدة: {total:.2f}s → {real_total:.2f}s")
        total = real_total

    # ---- burn subs + audio
    print("[i] حرق الترجمة والتجميع النهائي...")
    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    vf = f"subtitles={ass}:fontsdir={FONT_DIR},format=yuv420p"
    run([
        FF, "-hide_banner", "-loglevel", "error", "-y",
        "-i", concat, "-i", wav,
        "-vf", vf,
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-profile:v", "high", "-level", "4.1", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
        "-shortest", "-movflags", "+faststart", args.out,
    ])
    # ---- فصول يوتيوب (تايم كود دقيق)
    chap_path = os.path.join(os.path.dirname(os.path.abspath(args.out)),
                              os.path.basename(args.out).replace(".mp4", "-chapters.txt"))
    with open(chap_path, "w", encoding="utf-8") as f:
        f.write("00:00 المقدمة\n")
        for sc in scenes:
            mm, ss = int(sc["start"] // 60), int(sc["start"] % 60)
            f.write(f"{mm:02d}:{ss:02d} {sc.get('chapter', sc.get('title_ar', ''))}\n")
    print(f"[✓] فصول يوتيوب: {chap_path}")
    print(f"[✓] تم: {args.out}")


if __name__ == "__main__":
    main()
