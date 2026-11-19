# rewayat — «ساعة الرمادي»

مسلسل روايات صوتية ومصورة باللهجة المصرية، مبني بالكامل داخل الريبو:
سكربت لكل مشهد → لقطات مولّدة → تعليق صوتي → محرك مونتاج محلي (ffmpeg) →
فيديو 1080p بترجمة عربية محروقة وميكس صوتي.

## المحتوى

```
docs/خطة-قناة-رواية-2026.md     خطة القناة: شروط الربح، الحماية، طول الفيديو، الإعلانات، سياسة AI
episodes/01-الرمادي/
  scenes.json                    سكربت الحلقة (الإيقاع الأصلي)
  scenes-slow.json               نفس الحلقة بإيقاع راوٍ (85 كلمة/دقيقة) — المستخدم في النشر
  publish.md                     العنوان/الوصف/الفصول/الشورتات (جاهز للنسخ في يوتيوب)
assets/images/ep01/              لقطات 16:9 + الثامبنيل
assets/audio/ep01/               تعليق صوتي لكل مشهد
assets/fonts/                    Noto Naskh / Noto Kufi / Cairo (SIL OFL)
pipeline/render.py               محرك الإنتاج
pipeline/retime.py               ضبط الإيقاع (إبطاء + وقفات تنفّس)
pipeline/make_thumb.py           توليد الثامبنيل
output/                          الفيديو النهائي + ملف الفصول
```

## إعادة الإنتاج

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r pipeline/requirements.txt
python3 pipeline/render.py episodes/01-الرمادي/scenes.json --out output/ep01.mp4
```

التفاصيل في [`pipeline/README.md`](pipeline/README.md).
