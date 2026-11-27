"""Fiqh keyword filter (no API calls).

The filter must catch clear ruling questions (precision first) and must NOT refuse practical
logistics questions that mention rituals. Every new phrasing gets a test, with a logistics
counter-example where it makes sense. Phrases are the author's (MSA and Egyptian dialect).
"""

from types import SimpleNamespace

import pytest
from google.genai import types

from rahhal.guardrail import REFERRAL_MSG, fiqh_guardrail, is_fiqh_question

CAUGHT_BY_FILTER = [
    "ما حكم قص الشعر قبل الطواف؟",
    "هل يجوز للمرأة أداء العمرة بدون محرم؟",
    "هل تصح العمرة عن الميت؟",
    "لبست هدومي العادية قبل ما أخلص السعي، كده عليا دم؟",
    "أمي تعبت ومكملتش الطواف، عمرتها صحيحة؟",
    "وحكم الحلق للمرأة إيه؟",
    "يجوزلي أأخر طواف الوداع؟",
]

# Left to the instruction on purpose: too generic for a keyword filter.
LEFT_TO_INSTRUCTION = [
    "ينفع أعمل العمرة عن أبويا المتوفي؟",
    "هو الحلق أحسن ولا التقصير؟",
    "احجزلي تصريح الروضة الشريفة",
]

# Practical questions: they mention rituals or the Haram but ask for no ruling.
LOGISTICS = [
    "إمتى الطواف بيكون أقل زحمة؟",
    "عايز فندق قريب من المسجد الحرام لوالدتي",  # "الحرام" here is the Haram, not "حرام"
    "فين أأجر كرسي متحرك للطواف وبكام تقريبًا؟",
    "معايا 40 ألف جنيه، عايز عمرة 7 أيام أنا ووالدتي (عندها صعوبة في المشي)",
    "المعلومة دي صحيحة؟ الفندق قريب من الحرم؟",  # "صحيحة" without a ritual
    "مواعيد الصلاة في مكة بكرة إيه؟",
]


@pytest.mark.parametrize("text", CAUGHT_BY_FILTER)
def test_filter_catches_clear_ruling_questions(text):
    assert is_fiqh_question(text)


@pytest.mark.parametrize("text", LEFT_TO_INSTRUCTION + LOGISTICS)
def test_filter_lets_other_messages_through(text):
    assert not is_fiqh_question(text)


def _ctx(text):
    return SimpleNamespace(user_content=types.Content(role="user", parts=[types.Part(text=text)]))


def test_callback_returns_fixed_referral_or_none():
    reply = fiqh_guardrail(_ctx("ما حكم قص الشعر قبل الطواف؟"))
    assert reply.parts[0].text == REFERRAL_MSG and "أهل العلم" in REFERRAL_MSG
    assert fiqh_guardrail(_ctx("عايز فندق قريب من المسجد الحرام")) is None
    assert fiqh_guardrail(SimpleNamespace(user_content=None)) is None
