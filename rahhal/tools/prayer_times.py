"""A local prayer-times tool: calculated on your machine with the `salat` library, no API.

Method: Umm al-Qura (Fajr at 18.5°, Isha 90 minutes after Maghrib, 120 minutes in Ramadan).
The results are calculated; the official announcement at the Haram takes priority.
"""

from __future__ import annotations

import datetime as dt
import warnings

import salat
from hijridate import Gregorian

from .travel import CITY_ALIASES

TIMEZONE = "Asia/Riyadh"
# Saudi Arabia is UTC+3 all year (no daylight saving), so a fixed offset is exact. It also works on
# Windows, which has no time-zone database for ZoneInfo("Asia/Riyadh") without an extra package.
SAUDI_TIME = dt.timezone(dt.timedelta(hours=3), TIMEZONE)
COORDINATES = {"makkah": (21.4225, 39.8262), "madinah": (24.4672, 39.6111)}  # (lat, lon) of the two Harams

with warnings.catch_warnings():
    # salat detects Ramadan through the old package name `hijri-converter`, which warns that it is now
    # called `hijridate`. Harmless; our own code uses `hijridate` directly.
    warnings.simplefilter("ignore", DeprecationWarning)
    _METHOD = salat.PrayerTimes(salat.CalculationMethod.MAKKAH, salat.AsrMethod.STANDARD)


# ⚠️ Pitfall: the model doesn't know today's date. Asked for "tomorrow", it called the tool with no date
#    and got today's times. `days_ahead` lets it say "tomorrow" (1) and the tool counts the days itself.
def get_prayer_times(city: str, date: str | None = None, days_ahead: int = 0) -> dict:
    """Get calculated prayer times for Makkah or Madinah on one day (local Saudi time).

    Args:
        city: "makkah" or "madinah" (Arabic names like مكة or المدينة are also accepted).
        date: Optional exact day as YYYY-MM-DD. Use it only if the user gives a specific date.
        days_ahead: Days after today in Saudi Arabia when no date is given: 0 = today,
            1 = tomorrow (بكرة), 2 = the day after tomorrow. You don't know today's date, so use
            this for relative days. The result includes the date used; tell the user that date.

    Returns:
        A dict with status, city, date, hijri_date, timezone, method, and times in 24-hour
        HH:MM for fajr, sunrise, dhuhr, asr, maghrib and isha. Times are calculated, not the
        official announcement of the Haram.
    """
    city_key = CITY_ALIASES.get(city.strip().lower())
    if city_key is None:
        return {"status": "error", "error": "city must be 'makkah' or 'madinah'"}
    if date:
        try:
            day = dt.date.fromisoformat(date.strip())
        except ValueError:
            return {"status": "error", "error": "date must be YYYY-MM-DD"}
    else:
        if not 0 <= int(days_ahead) <= 366:
            return {"status": "error", "error": "days_ahead must be between 0 and 366"}
        day = dt.datetime.now(SAUDI_TIME).date() + dt.timedelta(days=int(days_ahead))
    lat, lon = COORDINATES[city_key]
    times = _METHOD.calc_times(day, SAUDI_TIME, lon, lat)
    hijri = Gregorian(day.year, day.month, day.day).to_hijri()
    return {
        "status": "success",
        "city": city_key,
        "date": day.isoformat(),
        "hijri_date": f"{hijri.year}-{hijri.month:02d}-{hijri.day:02d}",
        "timezone": TIMEZONE,
        "method": "Umm al-Qura (Isha +120 min in Ramadan)",
        "times": {name: t.strftime("%H:%M") for name, t in times.items()},
        "note": "Calculated times; the Haram's official announcement takes priority.",
    }
