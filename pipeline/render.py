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
Style: Sub,Noto Naskh Arabic,32,&H00F2EDE4,&H00FFFFFF,&H00120F0C,&H99000000,0,0,0,0,100,100,0,0,1,1.5,0.9,8,110,110,60,1
Style: Title,Noto Kufi Arabic,54,&H00F6F1E9,&H00FFFFFF,&H00000000,&H99000000,0,0,0,0,100,100,0,0,1,2,2,8,40,40,0,1
Style: Small,Noto Naskh Arabic,24,&H00C9B7AC,&H00FFFFFF,&H00000000,&H99000000,0,0,0,0,100,100,0,0,1,0.8,0,8,40,40,30,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def build_ass(scenes, total, out_path):
    lines = [ASS_HEAD.format(w=SUB_W, h=SUB_H)]
    for sc in scenes:
        # (تم إلغاء عنوان الفصل أعلى الشاشة: تشويش بصري وتقليل تركيز)
        for a, b, txt in chunk_vo(sc["vo"], sc["start"] + 0.25, sc["end"] - 0.25):
            if b - a < 0.6:
                continue
            lines.append(
                f"Dialogue: 0,{fmt_ts(a)},{fmt_ts(b)},Sub,,0,0,0,,{rtl(txt)}{{\\fad(200,200)\\pos({SUB_W//2},634)}}"
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
    lines.append(
        f"Dialogue: 1,{fmt_ts(total-9.4)},{fmt_ts(total-1.5)},Small,,0,0,0,,{rtl('«اللي قال: أنا جيت أريّحكم»')}{{\\fad(800,900)\\pos({SUB_W//2},276)}}"
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


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

    # ---- مدد الصوت
    t = 0.0
    scenes = []
    for i, sc in enumerate(items, 1):
        vo_path = os.path.join(ROOT, sc["vo_file"])
        d = dur(vo_path)
        lead = sc.get("lead", 0.55)
        tail = sc.get("tail", 1.25)
        sc = dict(sc)
        sc["audio"] = vo_path
        sc["image"] = os.path.join(ROOT, sc["image_file"])
        sc["start"] = t
        sc["end"] = t + lead + d + tail
        t = sc["end"]
        scenes.append(sc)

    total = t
    if args.preview:
        total = min(total, args.preview)
    print(f"[i] عدد المشاهد: {len(scenes)} | المدة الإجمالية: {total/60:.2f} دقيقة")

    # ---- ترجمة
    ass = os.path.join(work, "subs.ass")
    build_ass(scenes, total, ass)

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
