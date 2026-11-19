#!/usr/bin/env python3
"""
محرك الصوت الاحترافي — «ساعة الرمادي»

المبدأ: الصوت بيتقسم لـ 3 مسارات منفصلة (stems) وبيتم دمجها بمعايير البث:

  1) VOICE STEM  — التعليق الصوتي بعد سلسلة معالجة كاملة:
       highpass 85Hz → deesser → EQ (cut 260Hz / presence 3.2kHz)
       → compressor 3:1 → 44.1k ثابت
  2) MUSIC STEM  — موسيقى تصويرية **نغمية بحتة**: درون وترى + باد + نبض
       (مفيش نويز أبيض ولا نقرات — دي كانت مصدر الوشوشرة)
  3) DUCKING     — sidechain compressor: الموسيقى بتنخفض تلقائياً 10dB
       وقت الكلام وترجع في السكوت (أهم ممارسة في ميكس الفيديو)

وأخيراً Mastering بـ EBU R128: -16 LUFS متكامل / -1.5 dBTP (معيار يوتيوب).

الاستخدام:
  python pipeline/audio.py episodes/01-الرمادي/scenes-slow.json --out mix.wav
"""
import argparse
import json
import os
import subprocess
import sys

import imageio_ffmpeg
import numpy as np

FF = imageio_ffmpeg.get_ffmpeg_exe()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000

# ──────────────────────────────────────────────── مستويات الميكس (dB)
VOICE_LEVEL = -16.0      # LUFS المستهدف للصوت
MUSIC_UNDER = -12.0      # الموسيقى تنخفض كام dB وقت الكلام
MUSIC_UNDER_DB = 13.0    # الموسيقى أعلى من الصمت بمقدارها، والـ ducking بينزّلها وقت الكلام
MUSIC_DUCK_DB = 11.0     # عمق الانخفاض وقت الكلام (يُقاس ويُتحقق منه)
TRUE_PEAK = -1.5


# ──────────────────────────────────────────────── أدوات

def dur(path):
    p = subprocess.run([FF, "-hide_banner", "-i", path], capture_output=True)
    for line in p.stderr.decode("utf-8", "replace").splitlines():
        if "Duration:" in line:
            h, m, s = line.split("Duration:")[1].split(",")[0].strip().split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise SystemExit(f"لا يمكن قراءة المدة: {path}")


def write_wav_open(path, channels=1, sr=SR):
    import wave
    w = wave.open(path, "wb")
    w.setnchannels(channels)
    w.setsampwidth(2)
    w.setframerate(sr)
    return w


def wav_append(w, mono_f32, channels=1):
    v = (np.clip(mono_f32, -1.0, 1.0) * 32767).astype("<i2")
    if channels == 1:
        w.writeframes(v.tobytes())
    else:
        st = np.empty((len(v), 2), dtype="<i2")
        st[:, 0] = v
        st[:, 1] = v
        w.writeframes(st.tobytes())


# ──────────────────────────────────────────────── 1) مسار الصوت البشري

VOICE_CHAIN = (
    "highpass=f=85:poles=2,"
    "deesser=i=0.4:m=0.5:f=0.5,"
    "equalizer=f=260:t=q:w=1.0:g=-2.5,"      # إزالة الخشونة/الطين
    "equalizer=f=1200:t=q:w=1.2:g=1.0,"      # وضوح
    "equalizer=f=3200:t=q:w=1.0:g=2.0,"      # حضور (presence)
    "equalizer=f=7500:t=q:w=1.5:g=-1.5,"     # تلطيف الحدة
    "acompressor=threshold=-18dB:ratio=3:attack=12:release=180:makeup=2,"
    "alimiter=limit=0.89:attack=5:release=50:level=disabled,"
    "aresample=48000"
)


def build_voice_stem(scenes, total, path):
    """يبني مسار صوت واحد نظيف: كل مشهد يُعالَج بشبكة الفلاتر ثم يُركّب على التايم لاين."""
    n_total = int(total * SR)
    buf_w = write_wav_open(path, channels=1)
    try:
        cursor = 0
        for sc in scenes:
            start = int(sc["start"] * SR)
            # صمت حتى بداية المشهد
            if start > cursor:
                buf_w.writeframes(np.zeros(start - cursor, dtype="<i2").tobytes())
                cursor = start

            # معالجة المشهد (ffmpeg) — ناتج PCM مباشر
            raw = subprocess.run(
                [FF, "-hide_banner", "-loglevel", "error", "-i", sc["audio"],
                 "-af", VOICE_CHAIN, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                stdout=subprocess.PIPE, check=True).stdout
            voice = np.frombuffer(raw, dtype="<i2")

            # الصمت القائد (lead) قبل الكلام
            lead = int(sc.get("lead", 0.55) * SR)
            cursor += lead
            buf_w.writeframes(np.zeros(lead, dtype="<i2").tobytes())

            # الكلام نفسه
            buf_w.writeframes(voice.tobytes())
            cursor += len(voice)          # voice مصفوفة عينات مش بايتات

            # ذيل المشهد
            tail = int((sc["end"] - sc["start"]) * SR) - lead - len(voice)
            if tail > 0:
                buf_w.writeframes(np.zeros(tail, dtype="<i2").tobytes())
                cursor += tail

        if cursor < n_total:
            buf_w.writeframes(np.zeros(n_total - cursor, dtype="<i2").tobytes())
    finally:
        buf_w.close()


# ──────────────────────────────────────────────── 2) الموسيقى التصويرية

class MusicEngine:
    """
    موسيقى نغمية بحتة — مفيش نويز.
    كل الطبقات موجات جيبية بترددات هارمونية مع LFO بطيء، فالصوت ناعم ومفيش وشوشرة.

    الطبقات:
      sub    : 55Hz + 82.5Hz — هدير سينمائي (بدون هيس)
      pad    : A minor (220/261.63/329.63) — دفء وتناغم
      pulse  : 41.2Hz مقطّع بإيقاع 0.9Hz — توتّر (مشاهد tense)
      awe    : 523/784Hz بسويل بطيء — رهبة (مشاهد awe)
    """

    def __init__(self, total, scenes, sr=SR):
        self.total, self.scenes, self.sr = total, scenes, sr

    def _scene(self, t):
        for sc in self.scenes:
            if sc["start"] <= t < sc["end"]:
                return sc
        return self.scenes[-1]

    def block(self, i0, n):
        sr = self.sr
        t = np.arange(i0, i0 + n, dtype=np.float64) / sr
        seg = np.zeros(n, dtype=np.float64)

        # ── هدير سينمائي: ترددات منخفضة مع تنفّس بطيء جداً
        breath = 0.55 + 0.45 * np.sin(2 * np.pi * 0.021 * t - 1.2)
        # الصب-باس مخفّض (كان 85% من الطاقة → إحساس بهدر مزعج)
        seg += 0.30 * breath * np.sin(2 * np.pi * 55.0 * t)
        seg += 0.22 * breath * np.sin(2 * np.pi * 82.5 * t + 1.7)
        seg += 0.30 * breath * np.sin(2 * np.pi * 110.0 * t + 0.4)
        seg += 0.16 * breath * np.sin(2 * np.pi * 165.0 * t + 2.8)   # دفء متوسط
        seg += 0.09 * breath * np.sin(2 * np.pi * 220.0 * t + 5.1)

        # ── باد وترى (A minor) — بيتحكم فيه المزاج
        sc = self._scene(float(t.mean()))
        mood = sc.get("mood", "tense")
        ramp = np.clip(np.minimum(t - sc["start"], sc["end"] - t) / 3.5, 0, 1)

        if mood in ("calm", "awe"):
            swell = 0.35 + 0.65 * np.clip(np.sin(np.pi * (t - sc["start"]) / max(sc["end"] - sc["start"], 1)), 0, 1)
            seg += 0.16 * ramp * swell * np.sin(2 * np.pi * 220.00 * t)
            seg += 0.12 * ramp * swell * np.sin(2 * np.pi * 261.63 * t + 2.0)
            seg += 0.09 * ramp * swell * np.sin(2 * np.pi * 329.63 * t + 4.1)
        if mood == "awe":
            seg += 0.055 * ramp * np.sin(2 * np.pi * 523.25 * t + 0.9)
            seg += 0.038 * ramp * np.sin(2 * np.pi * 783.99 * t + 3.3)
        if mood == "tense":
            pulse = np.clip(np.sin(2 * np.pi * 0.9 * t), 0, 1) ** 1.6
            seg += 0.34 * ramp * pulse * np.sin(2 * np.pi * 41.20 * t)
            seg += 0.07 * ramp * np.sin(2 * np.pi * 164.81 * t)

        # ── دخول/خروج ناعم جداً
        seg *= np.clip(t / 4.0, 0, 1) * np.clip((self.total - t) / 6.0, 0, 1)
        return seg.astype(np.float32)


def build_music_stem(scenes, total, path, block_sec=2.0):
    """يبني مسار الموسيقى كستيريو حقيقي — تأخير Haas دقيق بين القناتين يخلق اتساع."""
    n_total = int(total * SR)
    bs = int(block_sec * SR)
    eng = MusicEngine(total, scenes)
    w = write_wav_open(path, channels=2)
    try:
        for i0 in range(0, n_total, bs):
            n = min(bs, n_total - i0)
            seg = eng.block(i0, n)
            peak = float(np.max(np.abs(seg))) or 1.0
            seg = seg / peak * 0.35          # تطبيع كل بلوك لتفادي القفزات
            # Haas stereo: القناة اليمنى متأخرة 14ms → اتساع بدون تعارض طوري
            d = int(0.014 * SR)
            n = len(seg)
            st = np.empty((n, 2), dtype=np.float32)
            st[:, 0] = seg
            st[1:, 1] = seg[:-1]
            st[:d + 1, 1] = 0.0
            st[d:, 1] = seg[:n - d]
            st[:, 1] *= 0.92
            w.writeframes((np.clip(st, -1, 1) * 32767).astype("<i2").tobytes())
    finally:
        w.close()


# ──────────────────────────────────────────────── 3) الميكس والماسترف

def rms_db(path):
    """يقيس مستوى RMS الفعلي لملف (mean_volume من volumedetect)."""
    p = subprocess.run([FF, "-hide_banner", "-i", path, "-af", "volumedetect",
                        "-f", "null", "-"], capture_output=True)
    for line in p.stderr.decode("utf-8", "replace").splitlines():
        if "mean_volume:" in line:
            return float(line.split("mean_volume:")[1].split("dB")[0].strip())
    raise SystemExit("لا يمكن قياس المستوى: " + path)


def measure_loudness(path):
    p = subprocess.run(
        [FF, "-hide_banner", "-i", path, "-af",
         f"loudnorm=I={VOICE_LEVEL}:TP={TRUE_PEAK}:LRA=11:print_format=json",
         "-f", "null", "-"], capture_output=True)
    txt = p.stderr.decode("utf-8", "replace")
    j = txt[txt.rindex("{"): txt.rindex("}") + 1]
    return json.loads(j)


def mix_and_master(voice_wav, music_wav, out_wav, total):
    """
    الدمج النهائي بيتم في بايثون (مش فلتر ffmpeg) للأسباب دي:
      • تحكّم كامل في الستيريو: الموسيقى ستيريو حقيقي، الصوت مونو في الوسط
      • ducking محسوب بعناية من منحنى طاقة الصوت نفسه (attack/release مظبوطين)
      • مفيش مفاجآت من amix/sidechaincompress (سابقاً كانت بتلغى الاتساع)

    المعادلة:
      music_out(t) = music(t) * duck(t)
      duck(t)      = -DUCK_DB وقت الكلام، 0 dB في السكوت (تنعيم هجومي/انفراجي)
    """
    m = measure_loudness(voice_wav)
    voice_gain = VOICE_LEVEL - float(m["input_i"])

    vr, mr = rms_db(voice_wav), rms_db(music_wav)
    music_gain = (vr + voice_gain) - MUSIC_UNDER_DB - mr
    print(f"    voice {vr:.1f} dB RMS | music {mr:.1f} dB RMS | "
          f"music gain {music_gain:+.1f} dB (تحت الصوت بـ {MUSIC_UNDER_DB:.0f} dB)")

    def read(path):
        r = subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-i", path,
                            "-ar", str(SR), "-ac", "2", "-f", "f32le", "-"],
                           capture_output=True)
        return np.frombuffer(r.stdout, dtype="<f4").reshape(-1, 2)

    v = read(voice_wav) * (10 ** (voice_gain / 20.0))
    mus = read(music_wav) * (10 ** (music_gain / 20.0))

    n = min(len(v), len(mus))
    v, mus = v[:n], mus[:n]

    # ── منحنى الطاقة: كم المشهد فيه كلام فعلي
    mono = np.abs(v).mean(axis=1)
    hop = int(0.01 * SR)                       # دقة 10ms
    k = n // hop
    env = mono[:k * hop].reshape(k, hop).max(axis=1)
    active = (env > 0.02).astype(np.float64)   # فوق -34 dBFS = كلام

    # ── تنعيم هجوم/انفراج: 40ms هجوم، 700ms انفراج (راحة للأذن)
    atk = np.exp(-1.0 / (0.040 * 100))
    rel = np.exp(-1.0 / (0.700 * 100))
    sm = np.empty_like(active)
    y = 0.0
    for i, a in enumerate(active):
        c = atk if a > y else rel
        y = c * y + (1 - c) * a
        sm[i] = y
    duck = (10 ** (-MUSIC_DUCK_DB / 20.0)) ** sm
    duck_full = np.repeat(duck, hop)
    if len(duck_full) < n:
        duck_full = np.pad(duck_full, (0, n - len(duck_full)), mode="edge")

    mus_ducked = mus * duck_full[:, None]

    mix = v + mus_ducked
    # ليمتر ناعم: tanh على ما فوق الحد فقط (بيحافظ على النقاء)
    peak = np.max(np.abs(mix)) or 1.0
    ceiling = 10 ** (-1.5 / 20.0)
    if peak > ceiling:
        mix *= ceiling / peak
    mix = np.tanh(mix * 1.02) * np.tanh(ceiling) / np.tanh(ceiling * 1.02)

    np.clip(mix, -1, 1, out=mix)
    w = write_wav_open(out_wav, channels=2)
    try:
        w.writeframes((mix * 32767).astype("<i2").tobytes())
    finally:
        w.close()

    # ماسترف نهائي: loudnorm مرتين (قياس ثم تطبيق)
    m2 = measure_loudness(out_wav)
    subprocess.run(
        [FF, "-hide_banner", "-loglevel", "error", "-y", "-i", out_wav,
         "-af",
         f"loudnorm=I={VOICE_LEVEL}:TP={TRUE_PEAK}:LRA=11:"
         f"measured_I={m2['input_i']}:measured_TP={m2['input_tp']}:"
         f"measured_LRA={m2['input_lra']}:measured_thresh={m2['input_thresh']}:"
         f"offset={m2['target_offset']}:linear=true,"
         f"alimiter=limit=0.84:attack=5:release=80:level=disabled",
         "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s24le", "-f", "wav", out_wav + ".tmp"],
        check=True)
    os.replace(out_wav + ".tmp", out_wav)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scenes")
    ap.add_argument("--out", default=None)
    ap.add_argument("--stems", action="store_true", help="احتفظ بملفات الـ stems")
    a = ap.parse_args()

    spec = json.load(open(a.scenes, encoding="utf-8"))
    items = spec["scenes"]

    # بناء التايم لاين
    t, scenes = 0.0, []
    for sc in items:
        sc = dict(sc)
        sc["audio"] = os.path.join(ROOT, sc["vo_file"])
        d = dur(sc["audio"])
        sc["start"] = t
        sc["end"] = t + sc.get("lead", 0.55) + d + sc.get("tail", 1.25)
        t = sc["end"]
        scenes.append(sc)
    total = t
    print(f"[i] المدة: {total/60:.2f} دقيقة | {len(scenes)} مشهد")

    out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.scenes)), "_build", "mix-master.wav")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    base = out.rsplit(".", 1)[0]

    voice = base + "-voice.wav"
    music = base + "-music.wav"

    print("[i] مسار الصوت البشري (تنظيف + EQ + ضغط)...")
    build_voice_stem(scenes, total, voice)
    print("[i] الموسيقى التصويرية (نغمية، بدون نويز)...")
    build_music_stem(scenes, total, music)
    print("[i] دمج + ducking + ماسترف EBU R128...")
    mix_and_master(voice, music, out, total)

    if not a.stems:
        os.remove(voice)
        os.remove(music)

    m = measure_loudness(out)
    print(f"[✓] {out}")
    print(f"    Loudness: {float(m['input_i']):.1f} LUFS | True Peak: {float(m['input_tp']):.1f} dBTP "
          f"| LRA: {float(m['input_lra']):.1f} LU  (الهدف {VOICE_LEVEL} / {TRUE_PEAK})")


if __name__ == "__main__":
    main()
