# دليل Google Flow — «ساعة الرمادي» الحلقة 3 «الاسم»

> دليل تشغيل على واجهة Flow الحالية (**Omni Flash 1.2** + **Veo 3.1 Lite**).
> كل رقم هنا مقاس على ملفات الحلقة الفعلية، مش تقدير.

---

## 0. فروق الحلقة 3 عن الحلقة 2 — اقرأ ده الأول

| | الحلقة 2 «الباب» | **الحلقة 3 «الاسم»** |
|---|---|---|
| عدد المشاهد | 10 | 10 |
| عدد مقاطع الصوت | 36 | **27** |
| مدة الكلام | 7:26 | **7:21** (441 ثانية) |
| عدد مقاطع Flow المطلوبة | ~50 | **59** |
| شخصيتان في الكادر | كتير | **قليل** — ياسين لوحده في 7 مشاهد |
| أصعب حاجة | الاستمرارية بين ياسين وفؤاد | **الرجل بلا وجه** |

### القيد الأساسي في الحلقة دي

المشهد 2 و9 و10 فيهم شخصية **وجهها مش بيتشاف** — الرجل في الرداء الفاتح.
ده مش اختيار جمالي، ده **قيد في البرومبت**: أي محاولة تطلع وش واضح هتبوّظ
المعنى (الناس مش عارفة توصفه، وعشرة أوصاف مختلفة). فلازم تكتب في كل
برومبت فيه: `face completely lost in glow, unreadable, no facial features`.

> ⚠️ **ما تحاولش** تحل ده بـ Ingredients أو بوصف تفصيلي للوجه. الحل هو
> **الغموض نفسه** — خلّي الضوء يغطي الوش في كل زاوية.

---

## 1. إعدادات الحساب والتكلفة

| البند | القيمة |
|---|---|
| الرابط | `flow.google.com` |
| الرصيد المجاني | **50 كريديت يوميًا** — ما بيترحّلش |
| ساعات الذروة | ~2م–5م UTC: التوليد مقفول لغير المشتركين |

### تكلفة الكريديت (الجدول الرسمي)

| الموديل | الدقة | التكلفة |
|---|---|---|
| **Omni Flash 1.2** | 360p | 1 كريديت / ثانية |
| **Omni Flash 1.2** | 720p | 3 كريديت / ثانية |
| **Veo 3.1 Lite** | 720p | 10 كريديت / فيديو |
| Nano Banana Pro | صورة | ضمن الاشتراك |

### حساب الحلقة 3 بالظبط

| السيناريو | الحساب | الإجمالي |
|---|---|---|
| كل حاجة 360p | 59 مقطع × 8s × 1 | **472 كريديت** |
| كل حاجة 720p | 59 مقطع × 8s × 3 | **1,416 كريديت** |
| **المختلط (المُوصى بيه)** | 37×24 + 22×8 | **1,064 كريديت** |

**الخطة المختلطة:** 720p للمشاهد 2 و5 و6 و8 و9 و10 (فيها وش ياسين أو جوهر
بصري)، و360p للباقي + **Upscale** لـ1080p في الآخر (مجاني لأول 10 فيديوهات).

> مع **Google AI Pro (1,000 كريديت/شهر)**: ابدأ بـ360p لكل حاجة (472)،
> وارفع للمشاهد المهمة بعد ما تشوف النتيجة.

---

## 2. إعدادات كل توليد (انسخها)

```
Model            : Omni Flash 1.2
Aspect ratio     : Landscape 16:9
Duration         : 8s
Resolution       : 720p  (أو 360p للتجارب)
Number of outputs: 1        ← ضعف الكريديت لو 2
```

**قاعدة:** 1080p و4K بيحتاجوا **8 ثواني بالظبط**. أي مدة تانية ترجع 720p.

---

## 3. الشخصيات

### ياسين — الملف الوحيد المطلوب

| البند | القيمة |
|---|---|
| الملف | `assets/images/ep03/char-yaseen.png` (1024×1024) |
| تاجات البرومبت | `yaseen_main, lean Arab man early thirties, long oval face, deep-set dark eyes, black beard with grey chin streak, thin scar on right temple, sand scarf, mud-brown coat` |
| يظهر في | المشاهد 1، 3، 4، 5، 6، 7، 8، 9، 10 |

```
Mode   : Ingredients / References to Video
Images : 1 (ياسين) — والخلفية اختيارية كصورة تانية
Length : 8s
```

### الرجل ذو الرداء الفاتح — **مش Ingredients**

ده **مقصود**. لو رفعتله صورة مرجعية، Flow هيحافظ على وشه في كل مشهد،
وده بيموّت الحكاية (الناس مش شايفين وشه أصلًا).

| البند | القيمة |
|---|---|
| الطريقة | Text to Video عادي، **بدون** Ingredients |
| تاجات ثابتة | `tall figure in long pale robe, face completely lost in soft glow, unreadable silhouette, no facial features visible` |
| يظهر في | 2، 9 (وذكره في 10) |

> **الاستمرارية بدون Ingredients:** استخدم **Frames to Video** — صدّر آخر
> فريم من مقطع ناجح واستخدمه كـ start frame. الرداء والطول هيفضلوا ثابتين
> والوش هيفضل مجهول.

---

## 4. مقاطع الحلقة (59 مقطع)

| # | المشهد | المدة | مقاطع | الموديل | حقن الشخصية |
|---|---|---|---|---|---|
| 1 | الاسم | 41s | **6** | Omni 720p | ياسين + زحام |
| 2 | الراجل اللي طلع في الشرق | 41s | **5** | Omni 720p | ياسين + الرجل (بعيد) |
| 3 | الإحصاء | 33s | **4** | Omni 360p | ياسين + كتّاب |
| 4 | أم سلمى | 43s | **6** | Omni 360p | ياسين + أم سلمى |
| 5 | البوصلة | 55s | **7** | Omni 720p | إيد ياسين فقط |
| 6 | الخيمة الفارغة | 35s | **5** | Omni 720p | ياسين (سايلويت) |
| 7 | التوزيع | 47s | **6** | Omni 360p | بدون ياسين |
| 8 | الصوت المسروق | 51s | **7** | Omni 720p | ياسين + مكبّرات |
| 9 | الصوت | 52s | **7** | Omni 720p | ياسين + الرجل |
| 10 | الاسم التاني | 44s | **6** | Omni 720p | ياسين لوحده |
| | **الإجمالي** | **441s** | **59** | | |

---

## 5. البرومبتات — مشهد بمشهد

> **القاعدة الذهبية:** سطر واحد = **حركة واحدة**. «الكاميرا تتقدم **و**الرجل
> يرفع إيده» = مقطع مفكوك. افصلهم.

كل برومبت بينتهي بـ:
```
no dialogue, no speech, no voices, no text, no logos
```

---

### مشهد 1 — الاسم (6 مقاطع)

**1-أ · الزحام (واسع)**
```
Cinematic 16:9, 8s, slow push in.
[YASEEN ingredient]
A lean bearded man in a sand scarf raises both hands in refusal while
dozens of strangers reach toward him, touching his coat, holding out
small radios and papers. Golden dawn light behind them, canvas tents of
a vast camp in the distance, dust suspended in the air.
Painterly realism, chiaroscuro, teal-grey with ember-orange, 35mm grain.
Motion: slow push in, no shake.
Audio: crowd murmur, footsteps.
no dialogue, no speech, no voices, no text, no logos
```

**1-ب · وش ياسين (كلوز)**
```
[YASEEN ingredient]
Extreme close-up on a lean bearded man's face, sweat and dust on his
skin, eyes moving across the crowd off-frame, jaw tight. No dialogue.
Shallow depth of field, golden rim light from behind.
Motion: almost still, breathing only.
no dialogue, no speech, no voices
```

**1-ج · إيدين بتتمدّ**
```
Many weathered hands reaching into frame from all sides, holding out
folded papers and small transistor radios, a young man's coat sleeve at
the edge. Dawn light, dust.
Motion: hands drifting slowly, no camera move.
no dialogue, no speech
```

**1-د · المخيم من بعيد**
```
A vast desert tent camp at dawn seen from a low ridge, hundreds of tents
in rows, thin smoke columns, tiny figures moving between them. One ember
slit at the horizon.
Motion: slow lateral pan right.
no dialogue, no speech
```

**1-هـ · خيمة ياسين من برّه**
```
The outside of a small canvas tent before sunrise, a queue of twenty
people standing patiently in the dark facing it, breath visible in cold
air, one lantern on the ground.
Motion: very slow drift forward.
no dialogue, no speech
```

**1-و · ياسين قاعد لوحده**
```
[YASEEN ingredient]
A lean bearded man sits alone on the ground inside a dim tent, radio in
his lap, both hands over his face, one weak lamp above. Dust in the air.
Motion: static, breathing.
no dialogue, no speech
```

---

### مشهد 2 — الراجل اللي طلع في الشرق (5 مقاطع)

**2-أ · الحد الشرقي (واسع جدًا)**
```
Cinematic 16:9, 8s, static wide shot.
A single tall figure in a long pale robe stands motionless at the eastern
edge of a huge tent camp, seen from very far away as a dark silhouette
against a rising sun. The sand around him is completely smooth — no
footprints at all, approaching or leaving. Cold blue mist on the ground.
face completely lost in glow, unreadable, no facial features visible.
Motion: completely static camera, faint heat shimmer.
no dialogue, no speech, no voices
```

**2-ب · الناس بتوقف**
```
A crowd of camp dwellers stops walking and turns to look toward
something off-frame right, all frozen mid-step, some lowering their
heads. Grey dawn light, dust.
Motion: crowd settles into stillness, no camera move.
no dialogue, no speech
```

**2-ج · الرمل بلا أثر**
```
Extreme close-up of smooth untouched desert sand at dawn, cold blue
shadow, a faint warm line of sunrise at the top of frame. Absolutely no
footprints, no marks.
Motion: extremely slow tilt up.
no dialogue, no speech
```

**2-د · ياسين بيبص**
```
[YASEEN ingredient]
A lean bearded man in a sand scarf stands among a crowd, looking off
frame right, his expression unreadable, wind moving his scarf slightly.
Grey dawn, cold light.
Motion: hold, subtle breathing, scarf flutter only.
no dialogue, no speech
```

**2-هـ · الظل الطويل**
```
A very long single shadow stretched across flat sand toward the viewer,
cast by an unseen figure off-frame. Cold blue light, no footprints
anywhere.
Motion: slow tilt down the length of the shadow.
no dialogue, no speech
```

---

### مشهد 3 — الإحصاء (4 مقاطع)

**3-أ · طاولة الكتّاب**
```
Cinematic 16:9, 8s, slow push.
Three clerks in clean pale grey robes sit at a long wooden table in the
open air, thick ledgers and ink pots before them, writing steadily.
Families queue in front, ground swept clean, canvas tents behind.
Grey overcast light. Orderly and deeply wrong.
Motion: slow push in, pens moving only.
no dialogue, no speech, no voices
```

**3-ب · صف الأولاد**
```
A separate short queue of children held back by a rope line, ten or so
kids standing quietly, an adult's hand on one child's shoulder. Grey
flat light, dust.
Motion: static, cloth moving in wind.
no dialogue, no speech
```

**3-ج · القلم على الورق**
```
Extreme close-up of a reed pen writing Arabic-style ledger entries on
aged paper, ink pot at the edge, a hand holding the pen steady.
Warm lantern light against grey daylight.
Motion: pen strokes only, no camera move.
no text, no dialogue
```
> ⚠️ ده المقطع الوحيد اللي فيه كتابة. لو طلعت حروف مش مقروءة، **اقطعها**
> أو استبدلها بلقطة اليد من غير ورق.

**3-د · ياسين بيسأل**
```
[YASEEN ingredient]
A lean bearded man stands at the edge of a writing table, leaning
slightly forward, one hand on the table edge, questioning expression.
Grey daylight, clerks blurred in the background.
Motion: slight lean in, no camera move.
no dialogue, no speech
```

---

### مشهد 4 — أم سلمى (6 مقاطع)

> **ملاحظة إخراجية:** المشهد ده كل قوته في **الهدوء**. ما تحطّش حركة
> كاميرا كتير — الثبات هو اللي بيوحّش.

**4-أ · أم سلمى قاعد**
```
Cinematic 16:9, 8s, static.
An older woman in her fifties wearing a black headscarf sits perfectly
still on a wooden stool outside a canvas tent, hands folded in her lap,
her face completely calm and empty — no grief in it at all.
Grey flat light, laundry line behind, dust.
Motion: absolutely static, only fabric moving.
no dialogue, no speech, no voices
```

**4-ب · الكرسي الفاضي**
```
An empty wooden stool beside a canvas tent, dust on its seat, the tent
flap moving slightly. Grey light.
Motion: static.
no dialogue, no speech
```

**4-ج · ياسين بيقعد قصادها**
```
[YASEEN ingredient]
A lean bearded man in a mud-brown coat kneels on the ground in front of
an older woman seated on a stool, speaking quietly, his brow furrowed.
She looks past him, calm. Grey light.
Motion: still, subtle head movement.
no dialogue, no speech
```

**4-د · إيدينها**
```
Close-up of an older woman's folded hands in her lap, worn skin, a thin
silver ring. Perfectly still. Grey light.
Motion: none.
no dialogue, no speech
```

**4-هـ · وشها**
```
Close-up of an older woman's face in a black headscarf, utterly calm,
eyes open but not focused on anything, no tears, no expression.
Grey flat light.
Motion: static, blink only.
no dialogue, no speech
```

**4-و · الخيمة من بعيد**
```
A small tent at the edge of camp, a woman seated outside it, a man
kneeling before her, both tiny in the frame. Grey sky, wide sand.
Motion: very slow pull back.
no dialogue, no speech
```

---

### مشهد 5 — البوصلة (7 مقاطع) · **أهم مشهد بصري**

**5-أ · البوصلة في الإيد**
```
Cinematic 16:9, 8s, macro.
A worn brass compass held open in scarred weathered hands, its needle
pointing right, away from north. Brass scratched and dented, golden hour
light, dust motes.
Motion: extremely subtle hand tremor.
no dialogue, no speech, no voices
```

**5-ب · العقرب بيلف**
```
Macro shot inside an open brass compass, the needle swinging slowly
across the dial and settling. Warm light on the glass.
Motion: needle rotation only, camera locked.
no dialogue, no speech
```

**5-ج · الخدش على النحاس**
```
Extreme macro of a small hand-carved scratch on tarnished brass inside a
compass lid, catching warm light, the rest of the surface blurred.
Motion: slow rack focus across the scratch.
no text, no dialogue
```

**5-د · ياسين بيلف**
```
[YASEEN ingredient]
A lean bearded man stands in the middle of a camp square holding a
compass at chest height, turning slowly on the spot, sand scarf lifting.
Midday grey light, tents all around.
Motion: he rotates in place, camera locked.
no dialogue, no speech
```

**5-هـ · الرجل في اتجاه العقرب**
```
A tall figure in a long pale robe stands far away across open ground,
small in frame, facing the viewer. face completely lost in glow,
silhouette only, no facial features.
Motion: complete stillness, faint heat shimmer.
no dialogue, no speech
```

**5-و · العين على البوصلة**
```
[YASEEN ingredient]
Close-up of a bearded man's eyes looking down at something in his hands
off-frame, deep-set dark eyes, dust on his lashes.
Motion: eyes track slowly left to right.
no dialogue, no speech
```

**5-ز · الميدان من فوق**
```
High angle over a desert camp square, a single man standing alone in the
centre holding something small, people moving around the edges.
Long shadows, grey light.
Motion: slow rise of the camera.
no dialogue, no speech
```

---

### مشهد 6 — الخيمة الفارغة (5 مقاطع) · **أقوى مشهد**

> إحنا **بنستخدم الصورة اللي عندنا كمرجع**: `scene-06.png` طلعت ممتازة.
> استخدمها كـ Frames to Video (First) واطلب حركة بس.

**6-أ · الدخول**
```
Frames to Video (First): assets/images/ep03/scene-06.png
The canvas entrance of a huge empty tent at dawn, a silhouette standing
in the opening, one oil lamp burning on the packed earth at the centre.
Motion: the tent flap moves in a light wind, camera drifts forward
two metres. Nothing else moves.
no dialogue, no speech
```

**6-ب · المصباح**
```
Macro of a single oil lamp burning on packed earth, its flame steady,
warm light pooling on the ground, absolute darkness beyond.
Motion: flame flicker only.
no dialogue, no speech
```

**6-ج · القماش بيتنفّس**
```
Interior wall of a vast empty canvas tent, the fabric breathing slowly
in and out with the wind outside, dust suspended in a shaft of daylight.
Motion: fabric movement, camera static.
no dialogue, no speech
```

**6-د · الأرض**
```
Extreme low angle across packed earth floor of an empty tent, one lamp
glow at the top of frame, dust drifting through it.
Motion: extremely slow tilt.
no dialogue, no speech
```

**6-هـ · ياسين في الباب**
```
[YASEEN ingredient]
A lean bearded man stands in the entrance of an empty tent, silhouetted
against daylight from outside, one hand still holding the canvas.
Motion: he does not move; only the fabric and dust move.
no dialogue, no speech
```

---

### مشهد 7 — التوزيع (6 مقاطع)

**7-أ · التوزيع**
```
Cinematic 16:9, 8s, slow pan.
An open-air distribution line in a desert camp, people receiving sacks
of bread and boxes of medicine with genuine smiles, men in pale grey
robes handing them out. Grey sky, warm lanterns, dust.
Motion: slow pan right along the line.
no dialogue, no speech, no voices
```

**7-ب · طفل بياخد كيس**
```
A small child's hands taking a paper sack from an adult's hands, the
child looking up, a worn sleeve visible. Warm lamp light.
Motion: hands close around the sack.
no dialogue, no speech
```

**7-ج · العجوز بيبوس الإيد**
```
An old man with white stubble bends and kisses the hand of a distributor
in a pale robe, the distributor smiling. Grey light, dust.
Motion: the bend and the kiss, camera static.
no dialogue, no speech
```

**7-د · الدفتر**
```
A thick ledger open on a table, a hand writing names with a reed pen,
a red cord tying the pages together at the spine.
Motion: pen strokes only.
no text, no dialogue
```

**7-هـ · الخيط الأحمر**
```
Macro of red cord knotted around the spine of an old ledger, the fibres
catching warm light, pages compressed beneath it.
Motion: static, slight focus shift.
no dialogue, no speech
```

**7-و · الساحة من فوق**
```
High wide shot of a big open-air distribution in a desert camp, hundreds
of people, tables, sacks, tents around the perimeter. Grey overcast.
Motion: slow drone rise.
no dialogue, no speech
```

---

### مشهد 8 — الصوت المسروق (7 مقاطع)

**8-أ · ياسين في الراديو**
```
Cinematic 16:9, 8s, slow push.
[YASEEN ingredient]
A lean bearded man speaks into a small shortwave radio at night, his
face lit hard from below by the radio's dial, expression urgent.
Cold blue night, canvas behind him.
Motion: slow push in on his face.
no dialogue, no speech, no voices
```

**8-ب · المكبّرات**
```
Enormous loudspeakers mounted on tall wooden poles across a vast tent
camp at night, dozens of them receding into darkness, lantern-lit tents
below. Cold blue with hard white highlights.
Motion: slow crane up the nearest pole.
no dialogue, no speech
```

**8-ج · الناس بتسمع**
```
A crowd seen from behind at night, faces lifted toward loudspeakers
above, warm lantern light on their shoulders, cold blue sky.
Motion: static, slight crowd sway.
no dialogue, no speech
```

**8-د · الصوت بيرجع**
```
Visual metaphor: a single man's mouth at the edge of frame, and across
the frame the same wave shape repeating a hundred times in the air
above a camp, drawn as faint light. Cold blue.
Motion: the wave shapes ripple outward.
no dialogue, no speech, no text
```

**8-هـ · ياسين بيسدّ ودنه**
```
[YASEEN ingredient]
A lean bearded man presses both palms over his ears, eyes shut, jaw
clenched, standing under a loudspeaker pole at night.
Motion: he slowly lowers his hands.
no dialogue, no speech
```

**8-و · الظل على القماش**
```
A man's shadow thrown large onto a canvas tent wall by speaker light,
the shadow's mouth moving but the body still.
Motion: shadow mouth moving, body static.
no dialogue, no speech
```

**8-ز · المخيم بالليل (واسع)**
```
Vast desert tent camp at night from a distance, hundreds of small
lantern lights, tall speaker poles, cold blue sky with no stars.
Motion: very slow pull back.
no dialogue, no speech
```

---

### مشهد 9 — الصوت (7 مقاطع) · **أخطر مشهد دراميًا**

> **القيد:** الرجل لازم يتكلم **بصوت زي فؤاد**. الصوت في ملفاتنا، بس
> **الكادر** لازم يوحّي بفؤاد من غير ما يبان. الطريقة: لقطة من ضهر ياسين
> وهو بيسيب راديوه، والرجل ممدّ إيده — والوش مش باين.

**9-أ · الرجل بيقرب**
```
Cinematic 16:9, 8s, static.
A tall figure in a long pale robe stands a few metres from a lean bearded
man at the edge of a camp at night. face completely lost in soft glow,
unreadable, no facial features. One lantern on the ground between them.
Motion: the tall figure does not move; dust drifts.
no dialogue, no speech, no voices
```

**9-ب · الإيد المرفوعة**
```
Close-up of a pale hand raised gently in the air, palm open, soft glow
behind it, no other detail visible.
Motion: the hand lifts slightly and holds.
no dialogue, no speech
```

**9-ج · ياسين بيتجمّد**
```
[YASEEN ingredient]
Extreme close-up of a bearded man's face, eyes wide, breath caught,
a muscle moving in his jaw. Night, one warm lamp light from the side.
Motion: almost imperceptible, a single blink.
no dialogue, no speech
```

**9-د · الراديوه بينهم**
```
A small shortwave radio held out in two hands toward the centre of
frame, a pale sleeve at the edge of frame opposite, cold night behind.
Motion: the radio is lifted slowly.
no dialogue, no speech
```

**9-هـ · ياسين بيغمض عينه**
```
[YASEEN ingredient]
Close-up of a bearded man's eyes closing slowly, lashes against dust-lit
skin, night light. 
Motion: eyes close over three seconds.
no dialogue, no speech
```

**9-و · المسافة بينهم**
```
Wide static shot at night of two figures facing each other across a
short distance on open sand, one tall and pale, one in a dark coat, one
lantern between them. Cold blue, one warm pool of light.
Motion: absolutely static.
no dialogue, no speech
```

**9-ز · الخيمة من بعيد بالليل**
```
A single small tent far off at night with one lamp inside it, throwing
a warm square of light on the sand, cold dark desert all around.
Motion: extreme slow push toward the tent.
no dialogue, no speech
```

---

### مشهد 10 — الاسم التاني (6 مقاطع) · **الخاتمة**

**10-أ · الفحم على القماش**
```
Cinematic 16:9, 8s, macro.
A piece of charcoal writing large Arabic letters on canvas tent fabric,
the fabric taut, dawn light low and grey.
Motion: the hand moves across the canvas writing strokes.
no dialogue, no speech
```
> ⚠️ الحروف اللي هتطلع **مش هتكون اسم ياسين الحقيقي** — ومعظم المولّد
> بيكتب حروف مقلوبة. لو مش نظيفة، استخدم **لقطة الإيد من غير حروف**:
> `a hand holding charcoal against canvas fabric, motion only, no visible letters`

**10-ب · ياسين بيمشي بعيد**
```
[YASEEN ingredient]
Cinematic wide: a lean bearded man walks away from a vast tent camp
across empty grey desert, a small radio in one hand, a leather satchel
on his shoulder, long shadow ahead of him.
Motion: he walks away from camera at a steady pace.
no dialogue, no speech, no voices
```

**10-ج · الخيام بتصغر**
```
A vast desert tent camp seen from far away at dawn, tiny in frame, one
small figure walking away from it leaving a single line of footprints.
Cold grey, one ember slit at the horizon.
Motion: extreme slow pull back.
no dialogue, no speech
```

**10-د · الراديوه في الإيد**
```
Close-up of a worn shortwave radio carried low in a man's hand, swinging
slightly with his walking pace, sand under his boots.
Motion: rhythmic swing matching footsteps.
no dialogue, no speech
```

**10-هـ · باب الخيمة والاسم**
```
A canvas tent door at dawn with dark charcoal marks on it, the camp
behind silent, one lamp still burning inside.
Motion: the tent flap moves slightly in the wind.
no dialogue, no speech
```

**10-و · الصحراء الفاضية**
```
A completely empty grey desert at dawn, endless flat sand, one distant
horizon line, no figures, no tents, no footprints.
Motion: absolutely static, slow heat shimmer only.
no dialogue, no speech, no voices
```

---

## 6. الاستمرارية

### Frames to Video — لما تحتاجها

| الحالة | الطريقة |
|---|---|
| مشهد 6 كله | ابدأ من `scene-06.png` واستخدم آخر فريم لكل مقطع بعده |
| الرجل (2، 9) | آخر فريم من 2-أ → start frame لـ9-أ |
| ياسين بيمشي (10) | آخر فريم من 10-ب → start frame لـ10-ج |

```
1. المقطع الناجح → ⋮ → Download frame
2. New generation → Frames to Video: First
3. ارفع الفريم في + Add start frame
4. اكتب الحركة الجديدة بس (مش وصف الشخصية تاني)
5. Duration 8s · 16:9 · Outputs 1
```

**علامة التدهور:** بعد 4–5 تمديدات الجودة بتنزل. ساعتها **ابدأ من فريم
محفوظ**، ما تمدّدش أكتر.

---

## 7. الصوت في Flow

| البند | القيمة |
|---|---|
| الصوت الأصلي | **شغّل** — بييدي رياح و جو حقيقي |
| الحوار | **اقفله** + `no dialogue, no speech, no voices` في كل برومبت |

> **السبب:** الحوار بتاعنا متسجّل بملفات منفصلة (ياسين/فؤاد). لو Flow ولّد
> كلام عربي هيبقى بلكنة عشوائية ومش متزامن. والمشهد 9 بالتحديد بيعتمد على
> إن الصوت **زي فؤاد** — وده إحنا اللي عاملينه، مش Flow.

---

## 8. التصدير والاستيراد

| البند | القيمة |
|---|---|
| التنزيل | ⋮ → **Download** (MP4, 24fps) |
| الاسم | `ep03-s01-a.mp4` |
| المكان | `assets/video/ep03/` |
| الترقية | Upscale → 1080p قبل التنزيل النهائي |

```bash
# الصور الحالية (المستخدمة في الرندر المحلي)
assets/images/ep03/scene-01.png … scene-10.png

# لو استبدلت بمقاطع Flow:
assets/video/ep03/ep03-s01-a.mp4 …
# render.py بيقبل صورة أو فيديو في image_file
```

---

## 9. قائمة الفحص قبل كل توليد

```
□ Number of outputs = 1              ← أهم بند للكريديت
□ Aspect ratio = 16:9
□ Duration = 8s
□ Model = Omni Flash 1.2
□ Ingredients مرفوع (لو ياسين في الكادر)
□ الرجل: NO Ingredients — الوش لازم يفضل مجهول
□ آخر سطر: no dialogue, no speech, no voices, no text, no logos
□ حركة واحدة بس
```

---

## 10. أعطال شائعة → الحل

| العرض | السبب | الحل |
|---|---|---|
| وش الرجل بان واضح | مفيش قيد ضوء كفاية | زوّد `face lost in glow, backlit, no features` وقلّل الإضاءة الأمامية |
| ياسين بيتغير بين المقاطع | مفيش Ingredients | ارفع `char-yaseen.png` |
| الكريديت خلص بسرعة | Outputs = 2 | خليه 1 |
| 1080p رجع 720p | المدة مش 8s | خليها 8s بالظبط |
| حروف عربية مقلوبة | مشكلة معروفة في المولّد | استخدم لقطة من غير حروف |
| «Image generation failed» | برومبت طويل | اختصر لـ3 أسطر وأعد |
| Ingredients مش متاح | الموديل غلط | بدّل لـOmni Flash 1.2 |
| التوليد مقفول | ذروة 2–5م UTC | جرّب بره الوقت |
| مفيش Extend | حساب مجاني | كل مقطع ≤10s |

---

## 11. الميزانية والجدول

| اليوم | الشغل | كريديت |
|---|---|---|
| 1 | مشاهد 6 + 9 (الأقوى بصريًا) 720p | 288 |
| 2 | مشاهد 2 + 5 + 8 720p | 456 |
| 3 | مشاهد 1 + 10 720p | 288 |
| 4 | مشاهد 3 + 4 + 7 360p | 176 |
| | **الإجمالي** | **1,208** |

> **لو على الخطة المجانية (50/يوم):** 59 مقطع × 8 كريديت (360p) = 472
> كريديت = **~10 أيام**. ابدأ بالمشاهد 6 و9 (أقوى بصريًا) عشان تشوف
> النتيجة النهائية بسرعة.
