# pipeline — محرك إنتاج «ساعة الرمادي»

يبني فيديو 1080p كامل (حركة كاميرا + تدرّج لوني + جْرين + ترجمة عربية محروقة + ميكس صوتي)
من ملف مشاهد JSON. مفيش أي خدمة خارجية — كله محلي.

## التشغيل

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r pipeline/requirements.txt

python3 pipeline/render.py episodes/01-الرمادي/scenes.json \
  --out output/rewayat-ep01.mp4

# نسخة سريعة للاختبار (أول 15 ثانية)
python3 pipeline/render.py episodes/01-الرمادي/scenes.json \
  --out output/preview.mp4 --preview 15
```

### ضبط سرعة الإيقاع (مهم)

التعليق الصوتي المولَّد بيطلع سريع (~115 كلمة/دقيقة). الإيقاع الدرامي المطلوب **85–95**.
لتصحيحه:

```bash
python3 pipeline/retime.py episodes/01-الرمادي/scenes.json --tempo 0.86
# → ينشئ assets/audio/ep01/retimed/ و episodes/01-الرمادي/scenes-slow.json
```

`retime.py` بيعمل حاجتين:
1. **إبطاء مع الحفاظ على طبقة الصوت** (`atempo` — مش بيخنق الصوت).
2. **إطالة الصمت** عند نهايات الجمل (0.35–0.60s) والجمل الفرعية (0.18–0.26s) — ده اللي بيدّي إحساس الراوي.

بعدين ارندر بـ `scenes-slow.json`.

> ⚠️ استخدم `--tempo 0.85–0.88`. أقل من 0.80 بيبقى بطيء بشكل غير طبيعي.

## شكل `scenes.json`

```json
{
  "series": "ساعة الرمادي",
  "scenes": [
    {
      "id": 1,
      "vo": "النص اللي بيتقرأ (للعرض/الترجمة)",
      "vo_file": "assets/audio/ep01/scene-01.mp3",
      "image_file": "assets/images/ep01/scene-01.png",
      "motion": "slow_zoom_in",
      "mood": "tense",
      "chapter": "الافتتاحية"
    }
  ]
}
```

- `motion`: `slow_zoom_in | slow_zoom_out | pan_right | pan_left | push_up`
- `mood`: `tense | calm | awe` (بيتحكم في طبقة الموسيقى/النبض)
- `lead` / `tail`: ثواني صمت قبل/بعد التعليق (افتراضي 0.55 / 1.25)

## اللي المحرك بيعمله

1. يحسب مدة كل تعليق صوتي ويبني تايم لاين.
2. يبني **شريط صوتي** رياضياً: درون + رياح مُرشّحة + نبض قلب + نقرات، بمزاج مختلف لكل مشهد.
3. يرندر كل مشهد بـ zoompan (حركة بطيئة جداً) + vignette + تدرّج لوني + جْرين فيلم + نبض إضاءة.
4. يدمج المشاهد مع fade in/out بينها.
5. يحرق ترجمة ASS عربية (Noto Naskh) — سطرين كحد أقصى، أسفل الشاشة.
6. يضيف كارت المقدمة/النهاية ويكتب `ep01-chapters.txt` (فصول يوتيوب).

## ملاحظات تقنية مهمة

- **الترجمة**: استخدم خط **Noto Naskh Arabic** أو **Noto Kufi Arabic** (موجودين في `assets/fonts`) مع **Spacing = 0**.
  خطوط Cairo/Google Sans بتطلع الحروف المركّبة (لا/لأ) مربّعات في libass لأن shaping بتاعها مختلف.
- **العربية**: اكتب النص خام في الـ ASS؛ libass بيعمل التشكيل والترتيب بنفسه. متعملش reshaper/bidi مسبقاً
  (ده بيعمل عكس مزدوج).
- قابلية التوسّع: زوّد مشاهد في `scenes.json` وملفاتها في `assets/` — مفيش تغيير في الكود.
