#!/usr/bin/env python3
"""
محرك المؤثرات السينمائية -- نغمي بحت (مفيش نويز ابيض).

مسموح: موجات جيبية، هارمونيات، غلاف اسي، رنة مصنعة.
ممنوع: نويز مسموع، نقرات، تشويش، هيس.

  python pipeline/sfx.py episodes/01-الرمادي/scenes-slow.json --out /tmp/sfx.wav
"""
import argparse
import json
import os
import sys
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
SR = 48000


def env_adsr(n, attack, decay, sustain_level, release, sr=SR):
    a = max(1, int(attack * sr))
    d = max(1, int(decay * sr))
    r = max(1, int(release * sr))
    s = max(0, n - a - d - r)
    out = np.concatenate([
        np.linspace(0, 1, a, endpoint=False),
        np.linspace(1, sustain_level, d, endpoint=False),
        np.full(s, sustain_level),
        np.linspace(sustain_level, 0, r),
    ])
    return out[:n] if len(out) >= n else np.pad(out, (0, n - len(out)))


def exp_env(n, tau, sr=SR):
    t = np.arange(n) / sr
    return np.exp(-t / max(tau, 1e-4))


def reverb(x, sr=SR, decay=1.8, mix=0.35):
    """رنة مصنعة: خطوط تاخير + ترشيح الذيل. نغمي بالكامل."""
    out = np.zeros_like(x)
    for delay_ms, gain in ((37, 0.42), (53, 0.34), (71, 0.26), (97, 0.20)):
        d = int(delay_ms / 1000 * sr)
        if d >= len(x):
            continue
        tail = x[:-d] * gain
        ker = np.hanning(9)
        ker /= ker.sum()
        tail = np.convolve(tail, ker, mode="same")
        out[d:] += tail * exp_env(len(tail), decay, sr)
    return x + mix * out


def lowpass_tonal(x, sr=SR, cutoff=900):
    k = max(3, int(sr / max(cutoff, 20)))
    if k % 2 == 0:
        k += 1
    ker = np.hanning(k)
    ker /= ker.sum()
    return np.convolve(x, ker, mode="same")


def sfx_thunder(dur=3.2, sr=SR):
    """رعد: هدير منخفض 28-75Hz بهبوط تدريجي + كراكل نغمي."""
    n = int(dur * sr)
    t = np.arange(n) / sr
    out = np.zeros(n)
    f = 62 - 30 * (t / dur) ** 0.6
    phase = 2 * np.pi * np.cumsum(f) / sr
    out += 1.00 * np.sin(phase) * exp_env(n, 0.55, sr)
    out += 0.55 * np.sin(2 * phase) * exp_env(n, 0.35, sr)
    out += 0.30 * np.sin(3 * phase + 1.1) * exp_env(n, 0.22, sr)
    out += 0.45 * np.sin(2 * np.pi * 34.5 * t) * exp_env(n, 1.5, sr)
    rng = np.random.default_rng(11)
    for s in rng.uniform(0.02, 1.1, 12):
        i0 = int(s * sr)
        ln = min(int(0.12 * sr), n - i0)
        if ln <= 0:
            continue
        tt = np.arange(ln) / sr
        fq = rng.uniform(190, 620)
        out[i0:i0 + ln] += rng.uniform(0.10, 0.28) * np.sin(2 * np.pi * fq * tt) * exp_env(ln, 0.035, sr)
    out = lowpass_tonal(out, sr, 420)
    out = reverb(out, sr, decay=1.6, mix=0.30)
    return out / (np.max(np.abs(out)) or 1.0)


def sfx_wind(dur=10.0, sr=SR):
    """رياح نغمية: ثالوث منخفض بمستوى بيتغير ببطء + انزلاق ترددي."""
    n = int(dur * sr)
    t = np.arange(n) / sr
    breath = (0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t - 1.4)) ** 1.8
    drift = 1 + 0.006 * np.sin(2 * np.pi * 0.031 * t)
    out = np.zeros(n)
    for f0, g in ((55, 0.55), (82.5, 0.34), (110, 0.26), (137.5, 0.12)):
        out += g * np.sin(2 * np.pi * f0 * drift * t + f0 % 3)
    out *= breath
    out *= env_adsr(n, 1.4, 0.6, 0.85, 1.8, sr)
    out = lowpass_tonal(out, sr, 260)
    out = reverb(out, sr, decay=2.2, mix=0.25)
    return out / (np.max(np.abs(out)) or 1.0)


def sfx_drone_hit(dur=2.4, sr=SR):
    """ضربة درون (لحظة مفصلية): 41/55Hz بهجوم سريع وذيل طويل."""
    n = int(dur * sr)
    t = np.arange(n) / sr
    out = np.zeros(n)
    for f0, g, tau in ((41.2, 1.0, 0.85), (55.0, 0.62, 0.55),
                       (82.5, 0.32, 0.32), (123.5, 0.16, 0.20)):
        out += g * np.sin(2 * np.pi * f0 * t) * exp_env(n, tau, sr)
    out *= np.clip(t / 0.05, 0, 1)
    out = reverb(out, sr, decay=1.5, mix=0.28)
    return out / (np.max(np.abs(out)) or 1.0)


def sfx_bell(dur=2.8, sr=SR):
    """جرس بعيد: 196/294/392/588/784Hz بنسب تخميد مختلفة."""
    n = int(dur * sr)
    t = np.arange(n) / sr
    out = np.zeros(n)
    for f0, g, tau in ((196.0, 1.00, 1.5), (294.0, 0.55, 1.0),
                       (392.0, 0.34, 0.7), (588.0, 0.17, 0.45), (784.0, 0.09, 0.3)):
        out += g * np.sin(2 * np.pi * f0 * t) * exp_env(n, tau, sr)
    out *= np.clip(t / 0.01, 0, 1)
    out = lowpass_tonal(out, sr, 2600)
    out = reverb(out, sr, decay=2.6, mix=0.45)
    return out / (np.max(np.abs(out)) or 1.0)


def sfx_radio(dur=1.8, sr=SR):
    """تشويش راديو نغمي: حاملات بتقطيع وانزلاق -- مش نويز."""
    n = int(dur * sr)
    t = np.arange(n) / sr
    out = np.zeros(n)
    rr = np.random.default_rng(5)
    for f0, g in ((420, 0.30), (630, 0.22), (840, 0.16), (1180, 0.10)):
        glide = f0 * (1 + 0.004 * np.sin(2 * np.pi * rr.uniform(0.5, 2.0) * t))
        out += g * np.sin(2 * np.pi * np.cumsum(glide) / sr)
    gate = 0.55 + 0.45 * np.sin(2 * np.pi * 7.3 * t) * np.sin(2 * np.pi * 1.7 * t + 0.6)
    out *= np.abs(gate)
    out *= env_adsr(n, 0.12, 0.2, 0.7, 0.5, sr)
    out = lowpass_tonal(out, sr, 1800)
    return out / (np.max(np.abs(out)) or 1.0)


SFX = {
    "thunder": sfx_thunder,
    "wind": sfx_wind,
    "drone": sfx_drone_hit,
    "bell": sfx_bell,
    "radio": sfx_radio,
}

# (مؤثر, رقم المشهد, إزاحة بالثواني, مستوى dB)
DEFAULT_PLAN = [
    ("wind",    1, 0.0,  -30),
    ("radio",   1, 12.0, -34),
    ("thunder", 2, 1.0,  -26),
    ("radio",   3, 6.0,  -32),
    ("wind",    4, 0.0,  -32),
    ("drone",   7, 0.5,  -27),
    ("thunder", 7, 8.0,  -25),
    ("bell",    9, 1.0,  -30),
    ("thunder", 10, 2.0, -27),
    ("bell",    10, 20.0, -28),
]


# خطة الحلقة الثانية — موضوعة على mood كل مشهد، مش تخمين:
#   مشهد 1 راديو/ليل    2 فؤاد يصلح جهاز    3 صحراء/قافلة
#   4 نار البئر         5 وادي/ليلة          6 مخيم/ضوء
#   7 مطر رمادي         8 خيمة/سكوت          9 باب/ضوء ساطع   10 شروق/خط ذهبي
DEFAULT_PLAN_EP02 = [
    ("radio",   1,  0.0, -36),   # مؤشر الراديو وهو بيتكلم
    ("wind",    1,  0.0, -34),   # رياح برّه الشباك
    ("bell",    2,  1.2, -35),   # رنّة معدن خفيفة (مفك على راديو)
    ("wind",    3,  0.0, -33),   # صحراء مفتوحة
    ("drone",   3,  0.0, -32),   # اتساع الطريق
    ("thunder", 4,  1.0, -31),   # بعيد، مع كلام فؤاد
    ("wind",    5,  0.0, -35),   # وادي بالليل
    ("drone",   6,  0.0, -33),   # خيمة/رهبة
    ("bell",    6,  2.0, -36),
    ("wind",    7,  0.0, -32),   # المطر الرمادي (نغمي، مش نويز)
    ("drone",   8,  0.0, -34),   # سكوت الاختيار
    ("thunder", 9,  2.0, -29),   # الباب
    ("bell",    9,  6.0, -33),
    ("thunder", 10, 1.0, -28),   # الشروق
    ("bell",    10, 8.0, -30),
    ("bell",    10, 26.0, -32),
]


def build(scenes, total, out_path, plan=None, sr=SR):
    """يبني شريط المؤثرات كامل الطول (ستيريو) على التايم لاين."""
    if plan is None:
        ids = {str(s["id"]) for s in scenes}
        has_segs = any(s.get("segments") for s in scenes)
        ep = scenes[0].get("episode", 1) if scenes else 1
        if not has_segs:
            plan = DEFAULT_PLAN
        elif ep == 4:
            plan = DEFAULT_PLAN_EP04
        elif ep == 3:
            plan = DEFAULT_PLAN_EP03
        elif ep == 2:
            plan = DEFAULT_PLAN_EP02
        else:
            plan = DEFAULT_PLAN
    n_total = int(total * sr)
    acc = np.zeros(n_total)
    by_id = {str(s["id"]): s for s in scenes}
    cache = {}
    for name, sid, off, level_db in plan:
        sc = by_id.get(str(sid))
        if sc is None:
            continue
        if name not in cache:
            cache[name] = SFX[name]()
        sig = cache[name]
        start = int((sc["start"] + off) * sr)
        if start >= n_total:
            continue
        end = min(start + len(sig), n_total)
        acc[start:end] += sig[: end - start] * (10 ** (level_db / 20.0))

    d = int(0.011 * sr)
    st = np.zeros((n_total, 2))
    st[:, 0] = acc
    st[d:, 1] = acc[: n_total - d]
    st[:, 1] *= 0.9

    pcm = (np.clip(st, -1, 1) * 32767).astype("<i2")
    w = wave.open(out_path, "wb")
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(sr)
    w.writeframes(pcm.tobytes())
    w.close()
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scenes")
    ap.add_argument("--out", default="/tmp/sfx.wav")
    a = ap.parse_args()
    spec = json.load(open(a.scenes, encoding="utf-8"))
    from audio import dur
    t, scenes = 0.0, []
    for sc in spec["scenes"]:
        sc = dict(sc)
        sc["audio"] = os.path.join(ROOT, sc["vo_file"])
        d = dur(sc["audio"])
        sc["start"] = t
        sc["end"] = t + sc.get("lead", 0.55) + d + sc.get("tail", 1.25)
        t = sc["end"]
        scenes.append(sc)
    build(scenes, t, a.out)
    print(f"[OK] {a.out} | {t/60:.2f} min | {len(DEFAULT_PLAN)} tonal sfx")


if __name__ == "__main__":
    main()

# الحلقة 3 — «الاسم». المؤثرات على mood كل مشهد:
#   1 زحام/جرس    2 فراغ شرقي/رياح    3 أقلام وورق    4 سكوت/قماش
#   5 معدن البوصلة  6 خيمة فارغة      7 توزيع/دافئ    8 مكبّرات صوت
#   9 رياح ساكنة/طنين   10 خطوات/رياح
DEFAULT_PLAN_EP03 = [
    ("bell",    1,  0.8, -35),   # جرس بعيد وسط الزحام
    ("wind",    2,  0.0, -34),   # فراغ الحد الشرقي
    ("drone",   2,  0.0, -35),
    ("bell",    3,  1.5, -36),   # قلم/طاولة الكتّاب
    ("wind",    4,  0.0, -36),   # سكوت أم سلمى
    ("bell",    5,  0.5, -33),   # معدن البوصلة
    ("drone",   6,  0.0, -38),   # الخيمة الفارغة — أهدأ نقطة في الحلقة
    ("bell",    7,  2.0, -34),   # دافئ
    ("wind",    7,  0.0, -36),
    ("thunder", 8,  3.0, -32),   # مكبّرات الصوت
    ("drone",   9,  0.0, -34),
    ("bell",    9,  8.0, -31),
    ("wind",    10, 0.0, -33),
    ("bell",    10, 12.0, -32),
]

# خطة الحلقة الرابعة — «الرمل اللي سمع»
#   المشهد 2 و3 فيهم حجر، فمفيش رياح في 3 (الصوت هو الحجر نفسه)
#   6 سكوت حواري → أقل مستوى ممكن
#   9 العاصفة → أعلى مستوى في الحلقة
DEFAULT_PLAN_EP04 = [
    ("wind",    1,  0.0, -34),   # صحراء مفتوحة
    ("drone",   1,  0.0, -36),
    ("bell",    2,  0.0, -31),   # الأثر الأول
    ("wind",    2,  6.0, -33),
    ("drone",   3,  0.0, -37),   # الحجر — أهدأ نقطة
    ("bell",    3,  9.0, -29),   # الحجر "بيتكلم"
    ("wind",    4,  0.0, -35),   # الرجل التاني يظهر
    ("drone",   4,  0.0, -33),
    ("bell",    5,  2.0, -30),   # العصا على الرمل
    ("wind",    5,  0.0, -36),
    ("drone",   6,  0.0, -38),   # سكوت حواري تام
    ("bell",    7,  1.0, -30),   # ظهور الفتاة
    ("wind",    7,  0.0, -33),
    ("drone",   8,  0.0, -34),   # الورقة
    ("bell",    8,  7.0, -32),
    ("thunder", 9,  0.0, -25),   # العاصفة تتجمع
    ("wind",    9,  0.0, -28),   # أعلى رياح في الحلقة
    ("bell",    9, 14.0, -29),
    ("drone",   10, 0.0, -31),   # الكتابة
    ("bell",    10, 10.0, -28),
    ("wind",    10, 0.0, -33),
]
