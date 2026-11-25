"""Generate the synthetic demo data for Rahhal: hotels and exchange rates.

Everything here is fictional. A fixed random seed means every run writes identical files, so the
tests and the golden cases always see the same hotels. Run it with:

    uv run python scripts/generate_data.py
"""

from __future__ import annotations

import json
import random
from pathlib import Path

SEED = 1447
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

NAME_PARTS_A = ["النور", "السكينة", "الرحمة", "الضيافة", "البركة", "الهدى", "الصفا", "المروة", "الإيمان", "الأمان"]
NAME_PARTS_B = ["بلازا", "ريزيدنس", "إن", "سويتس", "جراند", "تاور"]

# Demo exchange rates, NOT live: the value of 1 unit of each currency in Saudi riyals.
FX_RATES_TO_SAR = {"SAR": 1.0, "EGP": 0.075, "USD": 3.75, "AED": 1.02, "KWD": 12.2}


def make_hotels(rng: random.Random) -> list[dict]:
    """14 hotels in Makkah and 8 in Madinah. Every name ends with "(وهمي)" (fictional)."""
    hotels: list[dict] = []
    used: set[str] = set()
    for city, count, max_distance in (("makkah", 14, 2500), ("madinah", 8, 1800)):
        for _ in range(count):
            while True:
                name = f"فندق {rng.choice(NAME_PARTS_A)} {rng.choice(NAME_PARTS_B)} (وهمي)"
                if name not in used:
                    used.add(name)
                    break
            distance = rng.randrange(150, max_distance, 50)
            stars = rng.choice([3, 3, 4, 4, 5])
            base = {3: 220, 4: 420, 5: 900}[stars]
            price = round(base * (1.6 - distance / max_distance) / 10) * 10  # closer = pricier
            shuttle = distance > 900 and rng.random() < 0.7
            hotels.append(
                {
                    "id": f"{city[:3].upper()}-{len(hotels) + 1:03d}",
                    "name_ar": name,
                    "city": city,
                    "distance_to_haram_m": distance,
                    "stars": stars,
                    "price_sar_per_night": price,
                    "has_shuttle": shuttle,
                    # Close to the Haram, or a shuttle bus: suitable for elderly travellers.
                    "elderly_friendly": distance <= 700 or shuttle,
                }
            )
    return hotels


def main() -> None:
    rng = random.Random(SEED)
    DATA_DIR.mkdir(exist_ok=True)
    hotels = make_hotels(rng)
    (DATA_DIR / "hotels.json").write_text(
        json.dumps(hotels, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    fx = {"note": "Demo rates for testing only, not live market data.", "to_sar": FX_RATES_TO_SAR}
    (DATA_DIR / "fx_rates.json").write_text(
        json.dumps(fx, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"wrote {len(hotels)} hotels and {len(FX_RATES_TO_SAR)} exchange rates to {DATA_DIR}")


if __name__ == "__main__":
    main()
