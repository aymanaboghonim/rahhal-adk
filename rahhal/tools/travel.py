"""Two plain-Python tools: currency conversion and hotel search.

They never call a model, so tests run them offline (tests/test_tools.py). All data is fictional.
"""

# 📘 Concept: Tool = Python function + docstring. The model never sees the code below; it reads the
#    function name, the docstring and the type hints, and decides when to call it and with which values.

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

# The model may pass the city the way the user wrote it (often in Arabic), so accept common forms.
CITY_ALIASES = {
    "makkah": "makkah", "mecca": "makkah", "makka": "makkah",
    "مكة": "makkah", "مكه": "makkah", "مكة المكرمة": "makkah", "مكه المكرمه": "makkah",
    "madinah": "madinah", "medina": "madinah", "madina": "madinah",
    "المدينة": "madinah", "المدينه": "madinah", "المدينة المنورة": "madinah", "المدينه المنوره": "madinah",
}


@lru_cache(maxsize=1)
def _fx() -> dict[str, float]:
    return json.loads((DATA_DIR / "fx_rates.json").read_text(encoding="utf-8"))["to_sar"]


@lru_cache(maxsize=1)
def _hotels() -> list[dict]:
    return json.loads((DATA_DIR / "hotels.json").read_text(encoding="utf-8"))


# 🧪 Try it: type "معايا 40 ألف جنيه، يطلعوا كام ريال؟" and open the Events tab: you'll see a
#    function_call with amount=40000, from_currency="EGP", to_currency="SAR", then its response (3000).
def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """Convert an amount between currencies using DEMO (not live) rates.

    Args:
        amount: The amount of money to convert, e.g. 40000.
        from_currency: ISO code of the source currency: EGP, SAR, USD, AED or KWD.
        to_currency: ISO code of the target currency: EGP, SAR, USD, AED or KWD.

    Returns:
        A dict with status, the converted amount (rounded to 2 decimals), and a note
        that rates are for demo only.
    """
    rates = _fx()
    src, dst = from_currency.strip().upper(), to_currency.strip().upper()
    if src not in rates or dst not in rates:
        return {"status": "error", "error": f"unsupported currency; supported: {sorted(rates)}"}
    if amount < 0:
        return {"status": "error", "error": "amount must be non-negative"}
    return {
        "status": "success",
        "amount": amount,
        "from_currency": src,
        "to_currency": dst,
        "converted_amount": round(amount * rates[src] / rates[dst], 2),
        "note": "Demo exchange rates, not live market rates.",
    }


def search_hotels(
    city: str,
    max_price_sar_per_night: float | None = None,
    elderly_friendly_only: bool = False,
    max_distance_m: int | None = None,
    limit: int = 5,
) -> dict:
    """Search the (synthetic) hotel catalogue for Umrah trips.

    Args:
        city: "makkah" or "madinah" (Arabic names like مكة or المدينة are also accepted).
        max_price_sar_per_night: Optional nightly budget cap in SAR.
        elderly_friendly_only: If true, only hotels close to the Haram or with a shuttle.
        max_distance_m: Optional maximum walking distance to the Haram in meters.
        limit: Maximum number of results (1-10), sorted by distance then price.

    Returns:
        A dict with status and a list of matching hotels. All hotels are fictional demo data.
    """
    city_key = CITY_ALIASES.get(city.strip().lower())
    if city_key is None:
        return {"status": "error", "error": "city must be 'makkah' or 'madinah'"}
    limit = max(1, min(int(limit), 10))
    results = [
        h
        for h in _hotels()
        if h["city"] == city_key
        and (max_price_sar_per_night is None or h["price_sar_per_night"] <= max_price_sar_per_night)
        and (not elderly_friendly_only or h["elderly_friendly"])
        and (max_distance_m is None or h["distance_to_haram_m"] <= max_distance_m)
    ]
    results.sort(key=lambda h: (h["distance_to_haram_m"], h["price_sar_per_night"]))
    return {
        "status": "success",
        "count": len(results[:limit]),
        "hotels": results[:limit],
        "note": "Fictional demo hotels. Book only through official or trusted providers.",
    }
