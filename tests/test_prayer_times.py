"""Prayer-times tool (no API calls).

Reference times come from two public prayer-time tables (al-adkar.com and timesprayer.com, Umm al-Qura
method), read once in 2026-11; the official Umm al-Qura site was not reachable from our network.
"""

import datetime as dt

import pytest

from rahhal.tools import get_prayer_times
from rahhal.tools.prayer_times import SAUDI_TIME


def _minutes(hhmm: str) -> int:
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m


# Makkah, 2026-11-25: al-adkar.com and timesprayer.com agree on all six times.
REF_MAKKAH_2026_11_25 = {"fajr": "05:17", "sunrise": "06:38", "dhuhr": "12:08",
                         "asr": "15:15", "maghrib": "17:37", "isha": "19:07"}
# Makkah, 2026-03-01 (12 Ramadan 1447). Both sites show Isha 19:55 (Maghrib + 90): they skip the
# Umm al-Qura Ramadan rule, so Isha is checked against Maghrib + 120 instead.
REF_MAKKAH_2026_03_01 = {"fajr": "05:25", "sunrise": "06:41", "dhuhr": "12:33",
                         "asr": "15:55", "maghrib": "18:25"}


@pytest.mark.parametrize("ref,date", [(REF_MAKKAH_2026_11_25, "2026-11-25"),
                                      (REF_MAKKAH_2026_03_01, "2026-03-01")])
def test_makkah_matches_reference_within_2_minutes(ref, date):
    result = get_prayer_times("makkah", date)
    assert result["status"] == "success"
    for name, expected in ref.items():
        assert abs(_minutes(result["times"][name]) - _minutes(expected)) <= 2, name


def test_ramadan_isha_is_120_minutes_after_maghrib():
    ramadan = get_prayer_times("مكة", "2026-03-01")
    normal = get_prayer_times("مكة", "2026-11-25")
    assert ramadan["hijri_date"].startswith("1447-09")
    t = ramadan["times"]
    assert _minutes(t["isha"]) - _minutes(t["maghrib"]) == 120
    n = normal["times"]
    assert _minutes(n["isha"]) - _minutes(n["maghrib"]) == 90


def test_madinah_differs_and_accepts_arabic_name():
    madinah = get_prayer_times("المدينة المنورة", "2026-11-25")
    assert madinah["city"] == "madinah"
    assert madinah["times"] != get_prayer_times("makkah", "2026-11-25")["times"]


def test_default_date_is_today_in_saudi_time():
    result = get_prayer_times("makkah")
    assert result["date"] == dt.datetime.now(SAUDI_TIME).date().isoformat()
    assert result["timezone"] == "Asia/Riyadh"


def test_days_ahead_counts_from_today_in_saudi_time():
    today = dt.datetime.now(SAUDI_TIME).date()
    assert get_prayer_times("makkah", days_ahead=1)["date"] == (today + dt.timedelta(days=1)).isoformat()
    assert get_prayer_times("makkah", days_ahead=-1)["status"] == "error"


@pytest.mark.parametrize("city,date", [("cairo", None), ("makkah", "25/11/2026")])
def test_bad_input_returns_error(city, date):
    assert get_prayer_times(city, date)["status"] == "error"
