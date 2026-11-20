# دليل Google Flow — «ساعة الرمادي» الحلقة 2 «الباب»

> دليل تشغيل عملي، مكتوب على واجهة Flow الحالية (Omni Flash 1.2 + Veo 3.1 Lite).
> كل قيمة مكتوبة هنا هي **قيمة فعلية** موجودة في الواجهة، مش تقدير.

---

## 0. قبل ما تبدأ — إعدادات الحساب

| البند | القيمة |
|---|---|
| الرابط | `flow.google.com` (أو `labs.google/fx/tools/flow`) |
| المتصفح | Chrome أو Edge على ديسكتوب |
| السن | 18+ مع التحقق |
| الرصيد المجاني | **50 كريديت يوميًا** — يتجدد مع أول توليد في اليوم، والباقي **ما بيترحّلش** |
| ساعات الذروة | ~2م–5م UTC: التوليد **مقفول** لغير المشتركين (الصور بتفضل شغالة) |
| الرصيد المدفوع | Plus ‎+200/شهر · Pro ‎+1,000 · Ultra $100 ‎+10,000 · Ultra $200 ‎+25,000 |

### تكلفة الكريديت (من جدول Google الرسمي)

| الموديل | الدقة | التكلفة |
|---|---|---|
| **Omni Flash 1.2** | 360p | 1 كريديت / ثانية |
| **Omni Flash 1.2** | 720p | 3 كريديت / ثانية |
| **Veo 3.1 Lite** | 720p | 10 كريديت / فيديو (Ultra: 5) |
| Veo 3.1 Fast | 720p | 20 (متقاعد 5 ديسمبر 2026) |
| Veo 3.1 Quality | 720p | 100 (متقاعد 5 ديسمبر 2026) |
| Nano Banana Pro | صورة | مجاني/ضمن الاشتراك |

> ⚠️ **Veo Extend اتقفل في 5 نوفمبر 2026.** التمديد بقى **Omni Extend** وبيحتاج
> اشتراك Plus/Pro/Ultra. لو مش مشترك، كل مقطع لازم يبقى **≤ 10 ثواني**.

---

## 1. اختيار الموديل والإعدادات

في **مربع البرومبت** → أيقونة **Settings** (أعلى يمين) → تأكد من:

```
Model            : Omni Flash 1.2      ← الأفضل للاستمرارية والمدى الطويل
Aspect ratio     : Landscape 16:9      ← للفيديو الطويل
Duration         : 6s  أو 8s
Resolution       : 720p               ← 360p للتجارب بس (تلت التكلفة)
Number of outputs: 1                  ←  ضروري! 2 = ضعف الكريديت
```

**قاعدة الجودة:** 1080p و 4K محتاجين **8 ثواني بالظبط**. أي مدة تانية هترجع 720p.

### سير العمل الاقتصادي

| المرحلة | الموديل/الدقة | الغرض |
|---|---|---|
| تجربة | Veo 3.1 Lite 720p (10 كريديت) | تتأكد من الفكرة والكادر |
| إنتاج | Omni Flash 1.2 **360p** (1/ث) | كل المشاهد كاملة |
| تصدير | **Upscale → 1080p** (0 كريديت لأول 10 ث فيديو) | النسخة النهائية |

---

## 2. الشخصيات — Ingredients (مش Frames)

**القاعدة:** لو شخصية هتتكرر في أكتر من مشهد → **Ingredients**. لو لقطة واحدة → Text to Video عادي.

### الإعداد
```
Model  : Omni Flash 1.2   (Veo 3.1 Quality مش بيدعم Ingredients)
Mode   : Ingredients / References to Video
Images : 1–3 صور
Length : 8s  (Veo 3.1 Lite: 8s فقط)
```

### الملفات اللي ترفعها

| الشخصية | الملف | تاجات البرومبت |
|---|---|---|
| **ياسين** | `assets/images/ep02/char-yaseen.png` | `yaseen_main, long oval face, deep-set dark eyes, black beard with grey chin streak, thin scar on right temple, sand scarf, mud-brown coat` |
| **فؤاد** | `assets/images/ep02/char-fouad.png` | `fouad_main, stocky build, completely shaved head, deep forehead creases, milky-white blind left eye, sharp brown right eye, short grey beard, chin scar, brass compass necklace` |

**الترتيب في الـ Ingredients panel:** ياسين أولًا، فؤاد ثانيًا، والخلفية تالتة (اختياري).
الصورة الأولى هي الأقوى تأثيرًا.

---

## 3. مقاطع الحلقة (10 مشاهد × 2–3 مقاطع)

كل مشهد ≤ 10 ثواني (حد غير المشتركين). المدة الإجمالية **≈ 8 دقائق** = ~50 مقطع.

| # | المشهد | المدة | الموديل | حقن الشخصية |
|---|---|---|---|---|
| 1 | النداء | 8s × 3 | Omni 720p | ياسين + فؤاد |
| 2 | الرجل الذي علّمني أن أسمع | 8s × 3 | Omni 720p | فؤاد |
| 3 | الطريق من الشرق | 8s × 2 | Omni 360p | ياسين + فؤاد |
| 4 | أخطر جملة | 8s × 3 | Omni 720p | فؤاد (كلوز) |
| 5 | الوادي في الليل | 8s × 2 | Omni 360p | فؤاد |
| 6 | الخيمة | 8s × 3 | Omni 720p | ياسين |
| 7 | المطر الرمادي | 8s × 2 | Omni 360p | ياسين + فؤاد |
| 8 | الاختيار | 8s × 3 | Omni 720p | ياسين + فؤاد |
| 9 | الباب | 8s × 3 | Omni 720p | ياسين |
| 10 | خط ذهبي | 8s × 3 | Omni 720p | ياسين |

### الميزانية
- **720p (3 ك/ث × 8s = 24 كريديت)** × 20 مقطع = **480**
- **360p (1 ك/ث × 8s = 8 كريديت)** × 10 مقطع = **80**
- **الإجمالي ≈ 560 كريديت** — يعني **شهر Google AI Pro (1,000)** كافي + هامش للتجارب.

---

## 4. قوالب البرومبت (انسخ كما هو)

### أ) لقطة الراوي (ياسين في الكادر)
```
Cinematic 16:9 film still, 8 seconds, slow dolly-in.
[YASEEN IMAGE as ingredient]
A lean Arab man in his early thirties, black beard with a grey streak,
thin scar on right temple, sand scarf, mud-brown coat, sits before an
old shortwave transmitter in a dark radio shack at night. One weak
orange lamp. Dust in the air. His hand turns a dial slowly.
Painterly realism, chiaroscuro, teal-grey palette with ember accents,
35mm grain, shallow depth of field.
Motion: slow push in, handheld breathing, no camera shake.
Audio: low room hum, distant wind outside.
```

### ب) لقطة فؤاد (ملفوف)
```
Cinematic 16:9 film still, 8 seconds, static with subtle push.
[FOUAD IMAGE as ingredient]
A stocky older man in his late fifties, completely shaved head, deep
forehead creases, milky-white blind left eye, short grey beard, chin
scar, brass compass hanging at his chest, sits on a wooden crate
repairing a small radio with a screwdriver. Warm lamplight from the
right. Sand dust. Blurred tents behind.
Painterly realism, chiaroscuro, teal-grey with warm amber, 35mm grain.
Motion: almost still, breathing, fingers working.
Audio: metal tick, slow breath.
```

### ج) لقطة بدون شخصية (establishing)
```
Cinematic 16:9 film still, 8 seconds, slow lateral pan.
A small caravan of three overloaded vintage trucks and forty walking
people crossing a vast grey desert at first light. Long thin shadows,
plumes of pale dust, broken power pylons in the distance. One ember
orange slit at the horizon. Tiny figures, epic scale.
Painterly realism, heavy atmospheric haze, 35mm grain.
Motion: slow pan right, no zoom.
Audio: distant engine, desert wind.
```

> **قاعدة ذهبية:** سطر واحد = **حركة واحدة**. «الكاميرا تتقدم **و**الشخصية تلتفت»
> = مقطع مفكوك. افصلهم لمقطعين.

---

## 5. الاستمرارية بين المقاطع — Frames to Video

بعد أول مقطع ناجح، **صدّر آخر فريم** واستخدمه كـ start frame للمقطع اللي بعده.

```
1. اضغط على المقطع الناجح → ⋮ → Download frame
2. New generation → Frames to Video: First
3. ارفع الفريم في + Add start frame
4. اكتب برومبت الحركة الجديدة فقط (مش وصف الشخصية تاني)
5. Duration 8s, 16:9, Number of outputs 1
```

**Frames to Video: First and last** — استخدمها في اللقطات اللي لازم تنتهي بشكل
محدد (زي مشهد 9: ياسين واقف قدام الباب → الضوء بيزيد → يقف ساكن).

| المحاولة | المدة | ملاحظة |
|---|---|---|
| الأولى | 8s | جودة كاملة |
| بعد 4–5 تمديدات | — | الجودة بتبدأ تنزل |
| عند التدهور | — | **أعد البدء** من فريم محفوظ بدل ما تمدد أكتر |

---

## 6. إعدادات الصوت في Flow

| البند | القيمة |
|---|---|
| الصوت الأصلي | **شغّل** (Sound native) — بيدي جو ورياح حقيقية |
| الحوار | **اقفله** أو اكتب `no dialogue, no speech` في البرومبت |
| السبب | الحوار بتاعنا متسجّل بملفات صوت منفصلة (ياسين/فؤاد) — صوت Flow هيتعارض |

> ⚠️ **مهم جدًا:** لو Flow ولّد كلام عربي، هيبقى بلكنة عشوائية ومش متزامن مع
> السرد. **دايمًا** ضيف في آخر البرومبت: `no dialogue, no speech, no voices`،
> واستخدم الصوت الأصلي للمؤثرات بس (رياح/معدن/خطوات).
>
> لو حبيت تستخدمه كمرجع: `Custom voice` متاح في Omni Flash — اختار voice واكتب
> وصف. بس الأفضل تسيب الحوار لملفاتنا.

---

## 7. التصدير والاستيراد في المونتاج

| البند | القيمة |
|---|---|
| التنزيل | ⋮ على المقطع → **Download** (MP4, 24fps) |
| الاسم | `ep02-s01-a.mp4` (مشهد-حرف) |
| المكان | `assets/video/ep02/` |
| الترقية | Upscale → 1080p قبل التنزيل النهائي |
| الترتيب | `s01-a` → `s01-b` → `s01-c` … |

### التجميع مع ملفاتنا
```bash
# الصور (المستخدمة حاليًا في الرندر المحلي)
assets/images/ep02/scene-01.png … scene-10.png

# لو استبدلت بمقاطع Flow:
assets/video/ep02/ep02-s01-a.mp4 …
# render.py يقبل صورة أو فيديو في image_file — لو فيديو، التحويل تلقائي
```

---

## 8. قائمة الفحص قبل التوليد

```
□ Number of outputs = 1        (أهم بند لتوفير الكريديت)
□ Aspect ratio = 16:9
□ Duration = 8s  (لو 1080p)
□ Model = Omni Flash 1.2  (لو محتاج Ingredients)
□ Ingredients: ياسين/فؤاد مرفوعين قبل الكتابة
□ آخر سطر في البرومبت: no dialogue, no speech, no voices
□ حركة واحدة بس في الوصف
```

## 9. أعطال شائعة → الحل

| العرض | السبب | الحل |
|---|---|---|
| «Image generation failed» متكرر | ازدحام أو برومبت طويل | **اختصر لـ 3 أسطر وأعد المحاولة** |
| مفيش خيار Video | الموديل على صورة | اضغط اسم الموديل → Video → Omni/Veo |
| الكريديت خلص بسرعة | Number of outputs = 2 | خليه 1 |
| Ingredients مش متاح | الموديل Quality/Fast | بدّل لـ **Omni Flash 1.2** |
| مش قادر أمدد | Extend اتقفل للمجاني | اشترك Plus+ أو خلي كل مقطع ≤10s |
| الوش بيتغير بين المقاطع | مفيش Ingredients | ارفع `char-*.png` كمرجع |
| 1080p بيرجع 720p | المدة مش 8s | خليها 8s بالظبط |
| التوليد مقفول | ساعة الذروة 2–5م UTC | جرّب بره الوقت ده |
