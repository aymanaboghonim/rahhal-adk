"""Fiqh guardrail: Rahhal never gives religious rulings (فتوى); it refers them to Nusuk (نسك).

Two layers:
1. This file: a keyword filter for clear *ruling* questions. It runs before the model as a
   `before_agent_callback`; on a match it returns a fixed referral and the model is never called.
2. The instruction in agent.py (rule 1): everything the filter can't safely catch, e.g.
   "ينفع أعمل العمرة عن أبويا؟".

The filter looks for ruling words (حكم، يجوز، حرام، كفارة...), not ritual topics (الطواف، الميقات),
so practical questions about rituals (crowds, transport, wheelchairs) still reach the agent.
"""

from __future__ import annotations

import re

from google.genai import types

REFERRAL_MSG = (
    "هذا سؤال شرعي خارج اختصاصي؛ أنا أساعد في الجانب اللوجستي فقط (الميزانية والسكن وترتيب الأيام).\n"
    "للفتوى، يُرجى الرجوع إلى تطبيق «نسك» الرسمي أو إلى أهل العلم."
)

_DIACRITICS = re.compile(r"[ً-ْٰـ]")  # tashkeel, superscript alef, tatweel
_LETTERS = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ة": "ه", "ى": "ي"})


def normalize_ar(text: str) -> str:
    """Remove diacritics and unify common letter variants, so dialect spellings match."""
    return _DIACRITICS.sub("", text).translate(_LETTERS)


# A word starts at the beginning or after a space or punctuation, optionally with و / ف attached.
_START = r"(?:^|[\s،,.؟?!(])(?:و|ف)?"
_END = r"(?=$|[\s،,.؟?!)])"

# Ruling words that are enough on their own.
_RULING = re.compile(
    _START
    + r"(?:"
    + r"حكم"                          # ما حكم ...
    + r"|[يت]جوز\w*|جا[يئ]ز\w*"       # يجوز، تجوز، يجوزلي، جايز
    + r"|حلال|حرام"                    # "حرام" only as its own word: "الحرام" (the Haram) doesn't match
    + r"|ا?فت(?:وي|اوي|وني|يني)"       # فتوى، فتاوى، افتوني
    + r"|كفار\w*|فدي\w*"              # كفارة، فدية
    + r")"
    + _END
)
# "عليا دم؟" (do I owe a sacrifice?)
_DAM = re.compile(_START + r"(?:عليا|عليه|عليها|علينا|علي)\s+دم" + _END)
# Validity words count only together with a ritual ("المعلومة دي صحيحة؟" is not fiqh).
_VALIDITY = re.compile(_START + r"(?:[تي]صح|صحيح\w*|باطل\w*|[تي]بطل)" + _END)
_RITUAL = re.compile(_START + r"(?:ال)?(?:عمر|طواف|سعي|احرام|صلا|حج|تحلل)\w*" + _END)


def is_fiqh_question(text: str) -> bool:
    """True if the message clearly asks for a religious ruling (high precision, not full recall)."""
    t = normalize_ar(text)
    if _RULING.search(t) or _DAM.search(t):
        return True
    return bool(_VALIDITY.search(t) and _RITUAL.search(t))


# 📘 Concept: Callback = a hook ADK calls at a fixed moment. A before_agent_callback runs before the
#    model; if it returns content, that content is the reply and the model is skipped (0 requests).
# 🧪 Try it: "ما حكم قص الشعر قبل الطواف؟" → the referral appears, and the terminal shows no model request.
def fiqh_guardrail(callback_context) -> types.Content | None:
    """before_agent_callback: answer clear fiqh questions with a fixed referral, skip the model."""
    content = callback_context.user_content
    text = " ".join(p.text for p in (content.parts or []) if p.text) if content else ""
    if is_fiqh_question(text):
        return types.Content(role="model", parts=[types.Part(text=REFERRAL_MSG)])
    return None
