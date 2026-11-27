"""Rahhal (رحّال): an Arabic travel-logistics agent; first trip template: Umrah. Episode 1: tools on a free key.

Read this file top to bottom: 1. the model → 2. the instruction → 3. the agent.
The tools live in tools/, the fiqh guardrail in guardrail.py.
"""

from __future__ import annotations

import os

import httpx
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.models.llm_response import LlmResponse
from google.genai import types

from .guardrail import fiqh_guardrail
from .tools import convert_currency, get_prayer_times, search_hotels

# ── 1. The model ─────────────────────────────────────────────────────────────────────────────────
# 🔗 Docs: https://google.github.io/adk-docs/agents/models/
# Free tier: Gemini 3.5 Flash-Lite allows 15 requests/minute and 500/day on a no-billing AI Studio key.
MODEL_NAME = os.getenv("RAHHAL_MODEL", "gemini-3.5-flash-lite")
REQUEST_TIMEOUT_S = 30

# ⚠️ Pitfall: `adk run` and `adk web` don't retry a 429 (free-tier quota) by default, so one burst of
#    tool calls ends the turn with a stack trace. A Gemini object (instead of a plain model name) lets us
#    add retries for 429/503 and a timeout, because a request can also hang with no answer at all.
model = Gemini(
    model=MODEL_NAME,
    retry_options=types.HttpRetryOptions(
        attempts=5, initial_delay=2, max_delay=60, http_status_codes=[429, 503]
    ),
    client_kwargs={"http_options": types.HttpOptions(timeout=REQUEST_TIMEOUT_S * 1000)},  # in ms
)

# Shown only after every retry fails: 429 = free-tier quota used up, 503 or timeout = model busy.
QUOTA_DAILY_MSG = "وصلنا للحد اليومي المجاني للطلبات. جرّب تاني بكرة."
QUOTA_MINUTE_MSG = "الطلبات كتير في الدقيقة دي. استنى دقيقة وجرّب تاني."
BUSY_MSG = "الخدمة عليها ضغط دلوقتي. جرّب تاني بعد شوية."


def quota_message(callback_context, llm_request, error: Exception) -> LlmResponse | None:
    """on_model_error_callback: turn a final 429/503/timeout into a short Arabic reply.

    Returning None lets any other error surface unchanged.
    """
    code = getattr(error, "code", None)
    if isinstance(error, (TimeoutError, httpx.TimeoutException)) or code == 503:
        text = BUSY_MSG
    elif code == 429:
        text = QUOTA_DAILY_MSG if "PerDay" in str(error) else QUOTA_MINUTE_MSG
    else:
        return None
    return LlmResponse(content=types.Content(role="model", parts=[types.Part(text=text)]))


# ── 2. The instruction ───────────────────────────────────────────────────────────────────────────
# The agent's job description and rules, in the language it answers in. Each rule fixes something we
# saw go wrong. A small model follows them most of the time, not always: the golden cases measure it.
INSTRUCTION = """\
أنت "رحّال"، مساعد لتخطيط الجانب اللوجستي لرحلات العمرة فقط: الميزانية، والعملة،
والسكن، وترتيب الأيام، وظروف المسافرين (كبار السن والأطفال).

القواعد:
1. لا تفتِ أبدًا: أي سؤال عن حكم شرعي (حلال/حرام، يجوز ولا لأ، صحة العبادة، الكفارة أو الفدية،
   الأفضل شرعًا) قل بلطف إنه خارج اختصاصك ووجّه المستخدم لسؤال أهل العلم.
   لكن الأسئلة العملية عن المناسك مش فتوى: المواعيد والزحمة، المواصلات للميقات أو الحرم، تأجير
   الكراسي المتحركة، ترتيب الأيام. جاوب عليها باختصار من غير ما تقول إنها سؤال شرعي، ولو المعلومة
   محتاجة تحديث مباشر (زحمة، تصاريح) وجّه لـ"نسك" كمصدر للمعلومة.
   لو السؤال فيه جزء عملي وجزء شرعي، جاوب العملي بس، وقول إن الجزء الشرعي (زي تحديد الميقات
   أو الحكم) يرجع لأهل العلم.
2. لا تحجز ولا تصدر تصاريح. للتصاريح وقطار الحرمين والحجوزات الرسمية: وجّه المستخدم إلى "نسك".
3. لأي تحويل عملات استخدم الأداة convert_currency، ولا تحسب من عندك. ووضّح أن الأسعار تجريبية.
4. لاقتراح فنادق استخدم الأداة search_hotels فقط، ووضّح أنها بيانات تجريبية. لو المسافر كبير في
   السن أو عنده صعوبة في المشي، استخدم elderly_friendly_only=true.
5. رد بنفس لهجة المستخدم (عامية مصرية أو فصحى)، وباختصار ووضوح. متذكرش أسماء الأدوات أو
   إعداداتها في ردك؛ اشرح بكلام عادي (مثلًا: "فنادق مناسبة لكبار السن").
6. اكتب أسماء العملات بالعربي (ريال سعودي، جنيه مصري، دولار أمريكي) وليس برموزها مثل SAR،
   واكتب الأرقام بالأرقام الغربية مثل 3000.
7. لو المستخدم ذكر ميزانية: حوّلها للريال بالأداة، واعتبر إن نصها تقريبًا للسكن. حد سعر الليلة =
   نص الميزانية بالريال ÷ عدد الليالي، ومرّره في max_price_sar_per_night. لو مفيش نتائج في مدينة،
   قول كده بوضوح، وابحث مرة واحدة من غير الحد واعرض أرخص الاختيارات، وقول إنها أعلى من الميزانية.
8. اكتب أسماء الفنادق زي ما رجعت من الأداة بالظبط، بما فيها كلمة (وهمي).
9. لمواعيد الصلاة في مكة أو المدينة استخدم الأداة get_prayer_times، ومتخمّنش المواعيد. اكتبها بنظام
   12 ساعة (ص/م)، واذكر التاريخ، ووضّح إنها مواعيد محسوبة والإعلان الرسمي في الحرم هو المعتمد.
"""

# ── 3. The agent ─────────────────────────────────────────────────────────────────────────────────
# 📘 Concept: Agent = Model + Instruction + Tools. The model is the brain, the instruction is the job
#    description, the tools are the hands. One user message ≈ 2 model requests when a tool is used.
# 🔗 Docs: https://google.github.io/adk-docs/agents/llm-agents/
root_agent = Agent(
    name="rahhal",
    model=model,
    description="Arabic travel-logistics assistant, Umrah template (budget, currency, hotels, prayer times). No religious rulings.",
    instruction=INSTRUCTION,
    # 🔗 Docs: https://google.github.io/adk-docs/tools-custom/function-tools/
    tools=[convert_currency, search_hotels, get_prayer_times],
    # Layer 1 of the fiqh guardrail (guardrail.py); rule 1 above is layer 2.
    # 🔗 Docs: https://google.github.io/adk-docs/callbacks/types-of-callbacks/
    before_agent_callback=fiqh_guardrail,
    on_model_error_callback=quota_message,
)
