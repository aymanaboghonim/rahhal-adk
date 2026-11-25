# Episode 1 · Practice

[Episode 1](README.md) → [Concepts](concepts.md) → **Practice**

<div dir="rtl">

لو احتجت ترجع لمفهوم، كل المفاهيم في صفحة [المفاهيم وجرّب](concepts.md).

## طبّق بنفسك

اختار المستوى اللي يناسبك. المستوى الأول كفاية علشان تفهم الحلقة، والباقي لو حابب تتعمق.

### المستوى 1: شغّل وجرّب (من غير كود)

1. **غيّر النموذج:** في ملف `.env` خلّي قيمة `RAHHAL_MODEL` هي `gemini-3.1-flash-lite`، وبعدين شغّل الاختبارات
   الحية تاني. أنهي حالات نتيجتها اتغيرت؟

   ```bash
   uv run pytest -m live -v
   ```
2. **مين اللي رد؟** اكتب سؤال شرعي بكلامك أنت، وبص على ملخص الاستهلاك: لو التوكنز صفر يبقى الفلتر هو اللي رد،
   ولو فيه توكنز يبقى النموذج هو اللي رد وهو ماشي على التعليمات.

### المستوى 2: تمارين موجّهة (تعديل بسيط)

**تمرين 1: اكتب حالة اختبار ذهبية بنفسك.** زوّد الحالة دي في آخر ملف `evals/golden_cases.yaml`، أو غيّر الرسالة
لسؤال بلهجتك، وبعدين شغّلها لوحدها:

```yaml
- id: my_prayer_times_madinah
  input: "مواعيد الصلاة في المدينة بكرة إيه؟"
  expected_tools: [get_prayer_times]
  expected_args: {city: madinah, days_ahead: 1}
```

```bash
uv run pytest -m live -v -k my_prayer_times_madinah
```

**تمرين 2: اعمل أداة بنفسك.** عايزين أداة تحسب وقت المشي من الفندق للحرم. اكتب دالة اسمها `walking_minutes` تاخد
المسافة بالمتر، وهل المسافر بيمشي ببطء. افتكر المفهوم 2: الوصف (docstring) هو اللي النموذج بيقراه. ضيفها في
ملف `rahhal/tools/travel.py`، وصدّرها من `rahhal/tools/__init__.py`، وحطها في قايمة الأدوات في `rahhal/agent.py`.
وبعدين أعد تشغيل `adk web` وجرّب:

```text
الفندق على بعد 600 متر من الحرم، والدتي هتاخد قد إيه مشي؟
```

<details>
<summary>الحل</summary>

```python
def walking_minutes(distance_m: int, slow: bool = False) -> dict:
    """Estimate how many minutes it takes to walk from a hotel to the Haram.

    Args:
        distance_m: Walking distance in meters, e.g. 600.
        slow: True for an elderly traveller or someone who walks slowly.

    Returns:
        A dict with status and the estimated walking time in whole minutes.
    """
    meters_per_minute = 40 if slow else 70
    return {"status": "success", "minutes": -(-distance_m // meters_per_minute)}
```

وفي `rahhal/agent.py` الأداة الجديدة بتنضم للقايمة:

```python
tools=[convert_currency, search_hotels, get_prayer_times, walking_minutes],
```

لما جربناه، النموذج استدعى الأداة بمسافة 600 ومشي بطيء، ورد بحوالي 15 دقيقة.

</details>

**تمرين 3: زوّد قاعدة في التعليمات.** في `INSTRUCTION` زوّد قاعدة عاشرة، مثلًا: «لو المستخدم قال إنه مستعجل، رد في
سطرين بس». جرّب رسالة فيها «أنا مستعجل»، وشوف النموذج التزم ولا لأ. وافتكر: النموذج الصغير بيلتزم أغلب الوقت، مش
كل الوقت.

### المستوى 3: مشروعك الخاص

اعمل أداة من عندك تفيد مسافر: مثلًا مواعيد قطار وهمية بين مدينتين، أو قايمة حاجات للشنطة حسب عدد الأيام، أو تحويل
لعملة بلدك. اكتب لها حالة اختبار ذهبية واحدة على الأقل، وخد صورة من تبويب Events وهي شغالة.

**شاركها:** في [Show and tell](https://github.com/aymanaboghonim/rahhal-adk/discussions/categories/show-and-tell) هنا على GitHub، أو في قناة مسار على
Discord، أو على السوشيال ميديا. اكتب الأداة عملت إيه، واتعلمت إيه، وإيه اللي النموذج غلط فيه.

## اختبر نفسك

**1.** النموذج بيقرر يستخدم أداة على أساس إيه؟

- أ) كود الدالة كله
- ب) اسم الدالة ووصفها وأنواع مدخلاتها
- ج) اسم الملف اللي فيه الدالة

<details>
<summary>الإجابة</summary>

ب) النموذج مش بيشوف الكود؛ بيقرأ الاسم والوصف وأنواع المدخلات (المفهوم 2).

</details>

**2.** رسالة استخدمت أداة واحدة، تاخد كام طلب للنموذج تقريبًا؟

- أ) طلب واحد
- ب) طلبين
- ج) خمس طلبات

<details>
<summary>الإجابة</summary>

ب) طلب يقرر يستدعي الأداة، وطلب يكتب الرد من نتيجتها (المفهوم 3).

</details>

**3.** سؤال «ما حكم قص الشعر قبل الطواف؟» استهلك كام توكن؟

- أ) صفر، لأن الفلتر رد قبل النموذج
- ب) حوالي ألفين، زي أي سؤال
- ج) الضعف، لأنه سؤال شرعي

<details>
<summary>الإجابة</summary>

أ) الـ `before_agent_callback` رد بالتحويل لـ«نسك» والنموذج ماتسألش (المفهوم 5).

</details>

**4.** ليه الأمر `uv run adk web` لوحده بيفتح صفحة فاضية في الـ codespace؟

- أ) المفتاح غلط
- ب) ADK بيمنع المصدر اللي تحويل المنافذ في GitHub بيبعت منه الطلبات
- ج) المنفذ 8000 مقفول

<details>
<summary>الإجابة</summary>

ب) علشان كده بنزود الخيار `--allow_origins http://localhost:8000` في أمر التشغيل.

</details>

**5.** حالة الميزانية ظهرت `XFAIL` في الاختبارات. ده معناه إيه؟

- أ) الاختبار نفسه فيه غلطة
- ب) ضعف معروف في النموذج بيتسجّل من غير ما يفشّل الاختبارات
- ج) الأداة مش شغالة

<details>
<summary>الإجابة</summary>

ب) النموذج المجاني بيحسب حد سعر الليلة غلط أحيانًا، وإحنا بنقيس ده وبنقوله بصراحة (المفهوم 6).

</details>

**خلصت الحلقة!** ارجع لـ[صفحة الحلقة](README.md) علشان تعرف الحلقة الجاية.

</div>
