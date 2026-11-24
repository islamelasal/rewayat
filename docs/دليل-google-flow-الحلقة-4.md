# دليل Google Flow — «ساعة الرمادي» الحلقة 4 «الرمل اللي سمع»

> على واجهة Flow الحالية: **Omni Flash 1.2** + **Veo 3.1 Lite**.
> الأرقام مقاسة على ملفات الحلقة (41 مقطع صوتي · 481 ثانية كلام).

---

## 0. القيد اللي بيحكم الحلقة دي

الحلقة 2 كانت **وجهين**. الحلقة 3 كانت **وجه مجهول**. الحلقة 4 مش فيها وش
أصلًا — **كلها أثر**.

| | الحلقة 3 | **الحلقة 4** |
|---|---|---|
| الشخصية الأساسية | ياسين + رجل بلا وجه | **ياسين + الأرض** |
| المشاهد اللي فيها وش | 6 من 10 | **3 من 10** |
| العنصر البصري الحقيقي | الضوء | **الرمل، الأثر، المدى** |
| عدد المقاطع | 59 | **64** |

**النتيجة العملية:** الحلقة دي **أرخص** من التالتة بصريًا، لأن نصها مناظر
واسعة من غير وجوه. يعني تكدر تعملها كلها 360p وترفع بس 3 مشاهد.

### العنصر اللي لازم يتكرر بالظبط

**الأثر.** بيظهر في 5 مشاهد، ولازم يبقى **بصمة جزمة واحدة، بنفس العمق،
بنفس المسافة**. لو كل مشهد طلّع أثر مختلف، الحكاية بتفكك.

```
single boot print, hard-edged, deep into dry dust,
heel and sole tread clearly defined, no wind ripples around it
```

> **مش صورة جاهزة** — استخرج فريم من مشهد 2 واستخدمه كـ **Ingredients
> reference** في كل مشهد فيه أثر. ده أنضف من إعادة التوليد.

---

## 1. الإعدادات والتكلفة

```
Model            : Omni Flash 1.2
Aspect ratio     : Landscape 16:9
Duration         : 8s
Resolution       : 360p  (للأغلبية) · 720p للمشاهد 2 و6 و9
Number of outputs: 1
```

| السيناريو | الحساب | الإجمالي |
|---|---|---|
| كله 360p | 64 × 8 × 1 | **512 كريديت** |
| كله 720p | 64 × 8 × 3 | **1,536 كريديت** |
| **موصى بيه** | 22×24 + 42×8 | **864 كريديت** |

> 864 كريديت = أقل من **شهر Google AI Pro** (1,000). وفيها هامش للتجارب.

---

## 2. الشخصيات

| الشخصية | المرجع | ملاحظة |
|---|---|---|
| **ياسين** | `assets/images/ep03/char-yaseen.png` | نفس التاجات — هو هو من غير تغيير |
| **الرجل التاني** | ❗ **مش Ingredients** | نحيف، معطف داكن، عصا. عادي ومجهول — ده مقصود |
| **الفتاة** | ❗ **مش Ingredients** | 12 سنة، حجاب غبار، ورقة. مشهد واحد بس |

### الرجل التاني — ليه بدون مرجع

مش لأن وشه مجهول زي الحلقة 3، لكن لأنه **راجل عادي جدًا**. لو حطيت له
مرجع، هيبقى مميز بصريًا، وهيبان «مبعوت». هو بالعكس: راجل بيسجّل، زي أي
واحد. الوصف كفاية:

```
thin middle-aged man, worn dark coat, long wooden walking stick,
unremarkable face, tired
```

### الفتاة — مشهد واحد، بدون مرجع

لو حطيتها في أكتر من مشهد، هتحتاج مرجع. هي في مشهد 7 بس (+ تظهر من ضهر
في 9). **ضهر بس في 9، ما تحتاجش وش.**

---

## 3. الميزانية على المشاهد

| # | المشهد | المدة | مقاطع | الأولوية |
|---|---|---|---|---|
| 1 | بعد أسبوع | 54s | 7 | 360p |
| 2 | **الرمل اللي سمع** | 38s | 5 | **720p** |
| 3 | الصوت في الحجر | 56s | 7 | 360p |
| 4 | الرجل التاني | 44s | 6 | 360p |
| 5 | خريطة الأسماء | 44s | 6 | 360p |
| 6 | **الثمن** | 67s | 9 | **720p** |
| 7 | الفتاة | 41s | 5 | 360p |
| 8 | الورقة | 52s | 7 | 360p |
| 9 | **الاختيار التاني** | 52s | 7 | **720p** |
| 10 | ما كتبته | 34s | 5 | 360p |
| | **الإجمالي** | **481s** | **64** | |

---

## 4. البرومبتات

اختصار: كل برومبت بينتهي بـ `no dialogue, no speech, no voices, no text, no logos`.

### مشهد 1 — بعد أسبوع (7)

**1-أ · ياسين على الحجر**
```
Cinematic 16:9, 8s, static wide.
[YASEEN ingredient]
A lone bearded man in a mud-brown coat and sand scarf sits on a flat grey
stone in an immense empty desert at dawn, a small shortwave radio beside
him, a leather satchel at his feet. Nothing else to the horizon.
Cold blue pre-dawn, one ember line at the horizon.
Motion: absolutely static, only his scarf moves.
no dialogue, no speech, no voices, no text, no logos
```

**1-ب · المدى (مافيش حد)**
```
Endless flat grey desert to a hard horizon line, completely empty, no
tracks, no plants, no structures. Cold blue light, heavy haze.
Motion: extremely slow pan right. Nothing enters frame.
no dialogue, no speech
```

**1-ج · الراديو في الإيد**
```
Close-up of a worn shortwave radio held in weathered hands, dial dark
and unlit, dust in the creases of the plastic.
Motion: a thumb turns the dial, no response.
no dialogue, no speech
```

**1-د · الظل**
```
A man's long shadow alone on flat grey dust at dawn, cast toward the
camera, the man himself out of frame above.
Motion: the shadow is still. Slow tilt.
no dialogue, no speech
```

**1-هـ · الحقيبة**
```
A worn leather satchel lying open on desert ground, a folded map that is
blank, a tin cup, a spare battery.
Motion: static, dust moving.
no dialogue, no speech
```

**1-و · ياسين من ضهر**
```
[YASEEN ingredient]
A bearded man seen from behind walking slowly away across flat empty
desert, his coat moving in the wind, no destination visible.
Motion: he walks away, camera fixed.
no dialogue, no speech
```

**1-ز · السما**
```
An overcast white-grey sky with no visible sun, thin high cloud, one
faint warm band low on the horizon. Bleak, flat light.
Motion: slow drift of cloud.
no dialogue, no speech
```

---

### مشهد 2 — الرمل اللي سمع (5) · **أقوى صورة في الحلقة**

**2-أ · الأثر الأول**
```
Cinematic 16:9, 8s, extreme low angle at ground level.
A single boot print in flat grey desert dust in the foreground,
hard-edged, deep, heel and sole tread clearly defined, no wind ripples
around it. Beyond it, identical prints continue in a perfectly straight
line to the far horizon. No other marks anywhere.
Cold blue dawn with one ember slit at the sky line.
Motion: extremely slow push forward along the line of prints.
no dialogue, no speech, no voices, no text, no logos
```

**2-ب · الخط للأفق**
```
Same boot prints seen from a higher angle, the line receding to a point
at the horizon, perfectly even spacing, no drift left or right.
Motion: slow crane up.
no dialogue, no speech
```

**2-ج · ياسين بيبص تحت**
```
[YASEEN ingredient]
A bearded man standing still, head tilted down, looking at the ground at
his own feet, his shadow crossing the dust.
Motion: he does not move. Only breath.
no dialogue, no speech
```

**2-د · قياس الأثر**
```
A man's boot beside a print in the dust, the print exactly the same size
and shape. Dust, cold light.
Motion: static.
no dialogue, no speech
```

**2-هـ · الأفق الفاضي**
```
The horizon line where the trail of prints vanishes into haze, nothing
beyond it, no structures, no figures.
Motion: extremely slow push toward the vanishing point.
no dialogue, no speech
```

---

### مشهد 3 — الصوت في الحجر (7)

> **المشهد كله على حجر واحد.** استخدم `assets/images/ep04/scene-03.png`
> كـ First frame في أول مقطع، وكمّل من آخر فريم.

**3-أ · الكف على الحجر**
```
First frame: assets/images/ep04/scene-03.png
A man's weathered hand pressed flat on a featureless grey stone slab
lying on empty desert floor. Deep shadow around it, one warm highlight
on the stone's edge.
Motion: the hand presses slightly harder. Nothing else moves.
no dialogue, no speech
```

**3-ب · الحجر (ماكرو)**
```
Extreme macro of grey stone surface, grain and tiny fractures visible,
no markings, no carvings.
Motion: slow rack focus across the surface.
no dialogue, no speech
```

**3-ج · الراديو صامت**
```
A shortwave radio lying on dust, speaker grille close to camera, nothing
coming out of it, dial unlit.
Motion: static.
no dialogue, no speech
```

**3-د · ياسين نايم**
```
[YASEEN ingredient]
A bearded man asleep on his side on hard desert ground, coat pulled
around him, the stone slab behind him, cold blue pre-dawn.
Motion: chest rising and falling only.
no dialogue, no speech
```

**3-هـ · الحجر بالليل**
```
The same stone slab at night, moonlight cold and hard, long shadow
stretching from it, absolutely nothing else in frame.
Motion: static, faint heat shimmer.
no dialogue, no speech
```

**3-و · أذن على الحجر**
```
[YASEEN ingredient]
A bearded man lying with his ear pressed against the flat stone, eyes
closed, listening. Night.
Motion: absolutely still.
no dialogue, no speech
```

**3-ز · الصحراء بالليل**
```
Vast empty desert at night under a cold blue sky with no stars, one low
horizon line, nothing in frame.
Motion: extremely slow push.
no dialogue, no speech
```

---

### مشهد 4 — الرجل التاني (6)

**4-أ · الظهور**
```
Cinematic 16:9, 8s, very wide.
A thin middle-aged man in a worn dark coat stands far away on flat empty
desert holding a long wooden walking stick, watching. A second figure
sits in the foreground. Both tiny in the landscape.
Motion: the standing man does not move at all.
no dialogue, no speech, no voices
```

**4-ب · المشي البطيء**
```
The same thin man walking slowly toward camera across flat desert, stick
tapping the ground, coat moving in wind. Dust at his feet.
Motion: steady walking pace, camera fixed.
no dialogue, no speech
```

**4-ج · العصا**
```
Close-up of a long wooden walking stick's tip touching dry dust, the
wood worn smooth and dark at the grip.
Motion: the stick lifts and plants again.
no dialogue, no speech
```

**4-د · الوش (عادي جدًا)**
```
Close-up of a thin middle-aged man's face, unremarkable, weathered,
tired, no distinguishing features, looking slightly past camera.
Grey flat light, dust on his skin.
Motion: static, he blinks once.
no dialogue, no speech
```

**4-هـ · المسافة بينهم**
```
Two men standing thirty paces apart on flat desert, facing each other,
neither moving. Wide, cold, empty.
Motion: absolutely static.
no dialogue, no speech
```

**4-و · الرمل بينهم**
```
Ground-level shot of flat desert dust between two pairs of boots, one
pair still, one approaching. The single line of boot prints runs through
the frame.
Motion: static.
no dialogue, no speech
```

---

### مشهد 5 — خريطة الأسماء (6)

> ⚠️ الحروف هتطلع مقلوبة. **استخدم خطوط مجردة بدل حروف** — الشكل بيوصل
> المعنى، والحروف مش مقروءة أصلًا في الحكاية.

**5-أ · الرسم في الرمل**
```
Cinematic 16:9, 8s, high angle.
A man kneels on flat desert sand dragging a long stick, carving a wide
spiral of abstract flowing script-like lines into the dust. A lantern on
the sand lights the grooves from below, making them deep and black. The
spiral is enormous and unfinished.
Motion: the stick moves, the spiral grows.
no readable letters, no dialogue, no speech, no voices
```

**5-ب · الخريطة كاملة**
```
High wide shot of a huge spiral of carved lines in flat desert dust,
lantern light raking across it, the pattern extending beyond the light
into darkness.
Motion: slow crane up.
no readable letters, no dialogue
```

**5-ج · الأسماء (تجريدي)**
```
Extreme close of carved grooves in dust, abstract marks that read as
groups of symbols, light raking low across them.
Motion: slow pan along the grooves.
no readable letters, no dialogue
```

**5-د · ياسين بيقرا**
```
[YASEEN ingredient]
A bearded man kneeling, looking down at carved lines in the dust, his
face lit from below by a lantern, expression tightening.
Motion: static.
no dialogue, no speech
```

**5-هـ · العصا بتمسح**
```
A boot dragging across carved dust, erasing a section of the spiral,
dust rising in a small cloud.
Motion: the boot moves left to right.
no dialogue, no speech
```

**5-و · الاتنين قاعدين**
```
Two men sitting on flat ground on either side of a lantern, the carved
spiral visible around them, night, cold blue beyond the light.
Motion: static.
no dialogue, no speech
```

---

### مشهد 6 — الثمن (9) · **أطول مشهد**

> **ملاحظة:** ده مشهد حوار كامل، والكاميرا لازم تفضل **ساكنة**. الحركة
> كلها في الإيدين والوش. لو حرّكت الكاميرا هتشتت الكلام.

**6-أ · الدفتر**
```
Cinematic 16:9, 8s, close.
A small worn notebook open in a man's hands, dense abstract handwritten
marks filling the page, a stub of pencil in the gutter.
Motion: a page turns.
no readable letters, no dialogue, no speech, no voices
```

**6-ب · الإيد بتكتب**
```
Close-up of a hand writing with a stub pencil in a small notebook, the
marks abstract and dense, lantern light from the left.
Motion: handwriting only.
no readable letters, no dialogue
```

**6-ج · وش الرجل**
```
Close-up of a thin middle-aged man's face lit from below by a lantern,
calm, watchful, unreadable.
Motion: static, one blink.
no dialogue, no speech
```

**6-د · وش ياسين**
```
[YASEEN ingredient]
Close-up of a bearded man's face, lantern light from below, jaw tight,
listening hard.
Motion: static.
no dialogue, no speech
```

**6-هـ · الفانوس**
```
A small oil lantern on flat desert sand at night, flame steady, warm
light pooling in a circle, absolute darkness beyond.
Motion: flame flicker only.
no dialogue, no speech
```

**6-و · المسافة بينهم**
```
Two men seated facing each other across a lantern, wide enough to see
both, night, cold blue beyond the pool of light.
Motion: static.
no dialogue, no speech
```

**6-ز · الدفتر بيتقفل**
```
A hand closing a small worn notebook, thumb pressing the cover flat,
lantern light.
Motion: the cover closes.
no dialogue, no speech
```

**6-ح · النجوم (مفيش)**
```
Cold blue night sky over flat desert, heavy cloud, no stars visible, one
faint glow at the horizon.
Motion: cloud drift only.
no dialogue, no speech
```

**6-ط · الرمل تحتهم**
```
Ground shot of flat sand between two seated figures, two pairs of boots,
a lantern base, dust.
Motion: static.
no dialogue, no speech
```

---

### مشهد 7 — الفتاة (5)

**7-أ · الفتاة وحدها**
```
Cinematic 16:9, 8s, wide.
A girl of about twelve in a dusty dark headscarf stands alone in the
middle of empty flat desert holding a folded paper against her chest.
Wind pulls at her clothes. No adults anywhere, no tents, no vehicles.
Cold blue dawn, one warm ember line at the horizon.
Motion: she stands perfectly still. Only her clothes move.
no dialogue, no speech, no voices
```

**7-ب · الوش**
```
Close-up of a twelve-year-old girl's face, dusty, calm, not afraid, eyes
steady on camera. Wind moving a strand of hair.
Motion: static, she does not blink.
no dialogue, no speech
```

**7-ج · الورقة في إيدها**
```
Close-up of a folded paper held against a girl's chest by small dusty
hands, the paper old and creased.
Motion: static, wind at the edge of the paper.
no readable letters, no dialogue
```

**7-د · ياسين بيقرب**
```
[YASEEN ingredient]
A bearded man walking slowly toward the girl across flat desert, she
stays still, distance closing.
Motion: he approaches, camera fixed.
no dialogue, no speech
```

**7-هـ · الاتنين في الكادر**
```
A bearded man and a small girl standing facing each other on empty
desert, twenty paces apart, both small in the frame.
Motion: static.
no dialogue, no speech
```

---

### مشهد 8 — الورقة (7)

**8-أ · الورقة بتتفتح**
```
Cinematic 16:9, 8s, macro.
A folded paper opened flat in weathered hands, covered edge to edge in
dense abstract handwritten marks with no margins. Old and creased, a
lantern flame reflected in its fibres.
Motion: the paper unfolds.
no readable letters, no dialogue, no speech, no voices
```

**8-ب · الوش بيتغير**
```
Close-up of a thin middle-aged man's face as he reads, lantern light
from below, his expression shifting from calm to something else.
Motion: static, subtle.
no dialogue, no speech
```

**8-ج · السطر الأخير**
```
Extreme macro of the bottom edge of a handwritten page, one lone line of
abstract marks separated from the dense block above it, lantern light
raking the paper.
Motion: slow rack focus.
no readable letters, no dialogue
```

**8-د · الورقة بتترجع**
```
A paper being folded again by weathered hands, creases pressed flat.
Motion: the folding.
no dialogue, no speech
```

**8-هـ · إيد الفتاة**
```
Close-up of a girl's small dusty hand taking a folded paper back,
perfectly steady, no tremor.
Motion: the hand closes on the paper.
no dialogue, no speech
```

**8-و · ياسين بيقرا**
```
[YASEEN ingredient]
A bearded man reading a paper held close to his face by lantern light,
eyes moving across it, jaw tightening.
Motion: static.
no dialogue, no speech
```

**8-هـ · الرمل حواليهم**
```
Ground shot: a folded paper lying on flat dust at night, lantern light
on it, three pairs of boots at the edges of frame.
Motion: static.
no dialogue, no speech
```

---

### مشهد 9 — الاختيار التاني (7) · **أقوى مشهد بصريًا**

**9-أ · الجدار (واسع)**
```
Cinematic 16:9, 8s, very wide.
An immense dark wall of dust storm rises across the entire horizon,
walking slowly forward, swallowing the light. One ember-orange slit
glows beneath it. Flat empty desert in the foreground.
Motion: the wall advances imperceptibly. Camera fixed.
no dialogue, no speech, no voices
```

**9-ب · التلاتة من ضهر**
```
Three figures seen from behind standing on flat desert facing a vast
dark dust wall on the horizon: a bearded man, a thin man with a stick,
a small girl. All small in frame.
Motion: absolutely static.
no dialogue, no speech
```

**9-ج · العاصفة بتقرب**
```
The dust wall much closer now, texture of churning dust visible, light
dying, sand streaming low across the ground.
Motion: the wall advances, sand streams.
no dialogue, no speech
```

**9-د · وش ياسين**
```
[YASEEN ingredient]
Close-up of a bearded man's face, wind tearing at his scarf, dust on his
skin, eyes fixed on something off-frame, lit by dying amber light.
Motion: static.
no dialogue, no speech
```

**9-هـ · وش الرجل**
```
Close-up of a thin middle-aged man's face, wind and dust, calm, almost
relieved, looking at the storm.
Motion: static.
no dialogue, no speech
```

**9-و · إيد الفتاة**
```
A small dusty hand reaching up and holding a man's coat sleeve, wind
pulling at both.
Motion: the hand closes.
no dialogue, no speech
```

**9-ز · الرمل بيتحرك**
```
Ground level: dry dust streaming across flat sand in long low sheets,
the boot prints beginning to fill and disappear.
Motion: dust streams left to right.
no dialogue, no speech
```

---

### مشهد 10 — ما كتبته (5) · **الخاتمة**

**10-أ · الكتابة**
```
Cinematic 16:9, 8s, high angle.
A bearded man kneels on flat grey desert dragging a long stick through
the dust, writing large sweeping abstract marks. A shortwave radio and
leather satchel beside him. A dark dust wall far on the horizon.
Motion: the stick moves, marks appear.
no readable letters, no dialogue, no speech, no voices
```

**10-ب · الكتابة كاملة**
```
Wide high shot of a long line of swept marks in desert dust, wide and
deliberate, unfinished at the far end. Dust wall on the horizon.
Motion: slow crane up.
no readable letters, no dialogue
```

**10-ج · ياسين بيقف**
```
[YASEEN ingredient]
A bearded man stands up from kneeling, stick still in hand, looking
toward the storm, back straight.
Motion: he rises.
no dialogue, no speech
```

**10-د · بيمشي في اتجاه العاصفة**
```
[YASEEN ingredient]
A bearded man walking away from camera toward an immense dark dust wall
on the horizon, small in the frame, not looking back.
Motion: he walks, camera fixed.
no dialogue, no speech
```

**10-هـ · الأثر في الرمل**
```
Ground shot: a line of swept marks in dust with a single pair of boot
prints beside it, dust beginning to drift over both.
Motion: dust drifts.
no dialogue, no speech
```

---

## 5. تقنية الأثر — الأهم في الدليل

عشان الأثر يفضل واحد في 5 مشاهد:

```
1. ولّد مشهد 2-أ لحد ما يطلع صح
2. ⋮ → Download frame  (فريم فيه الأثر واضح)
3. ارفعه كـ Ingredients reference في أي مشهد فيه أثر
4. في البرومبت اكتب:
   "same boot print as the reference image, identical size, identical depth"
```

**بديل أسرع:** لو Flow مش بيحافظ على التفاصيل، **استخدم نفس الصورة**
`scene-02.png` كـ First frame، وحرّك الكاميرا بس.

---

## 6. الأصوات في الحلقة

| الشخصية | f0 المقاس | ملاحظة |
|---|---|---|
| ياسين | 109–183 هرتز | الراوي |
| الرجل التاني | 94–110 هرتز | أعمق وأهدأ |
| الفتاة | 182 هرتز | ⚠️ **قريبة من مدى ياسين** |

> ⚠️ **تحذير مهم:** فصل الفتاة عن ياسين **مش في التردد** — الاتنين على نفس
> المدى. الفصل في **الطابع**: طفلة 12 سنة مقابل راجل في التلاتينات. في
> المكس النهائي، بينهم دايمًا سطر ليساسين بيفصل. لو عملت نسخة إنجليزية،
> انتبه للنقطة دي.

في Flow: **اقفل الحوار** (`no dialogue, no speech, no voices`) — الأصوات
كلها من ملفاتنا.

---

## 7. قائمة الفحص

```
□ Number of outputs = 1
□ Aspect ratio = 16:9
□ Duration = 8s
□ Ingredients: ياسين بس (الرجل والفتاة بدون مرجع)
□ الأثر: مصدر واحد في كل المشاهد
□ الحروف: abstract marks مش حروف
□ آخر سطر: no dialogue, no speech, no voices, no text, no logos
□ حركة واحدة بس
```

---

## 8. الجدول

| اليوم | الشغل | كريديت |
|---|---|---|
| 1 | مشاهد 2 + 9 (أقوى بصريًا) 720p | 288 |
| 2 | مشهد 6 (أطول) 720p | 216 |
| 3 | مشاهد 1 + 3 + 8 360p | 168 |
| 4 | مشاهد 4 + 5 + 7 + 10 360p | 192 |
| | **الإجمالي** | **864** |

> **على الخطة المجانية (50/يوم):** 512 كريديت (كله 360p) = **11 يوم**.
> ابدأ بمشهد 2 — هو اللي بيبيع الحلقة.
