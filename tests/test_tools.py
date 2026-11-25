"""Currency and hotel tools, and the data generator (no API calls)."""

from rahhal.tools import convert_currency, search_hotels


def test_convert_egp_to_sar_matches_demo_rate():
    result = convert_currency(40000, "EGP", "SAR")
    assert result["status"] == "success"
    assert result["converted_amount"] == 3000.0  # 40000 * 0.075


def test_convert_is_case_insensitive_and_reversible():
    sar = convert_currency(1000, "egp", "sar")["converted_amount"]
    back = convert_currency(sar, "SAR", "EGP")["converted_amount"]
    assert back == 1000.0


def test_convert_rejects_unknown_currency():
    assert convert_currency(10, "EGP", "XYZ")["status"] == "error"


def test_search_hotels_filters_and_sorts():
    result = search_hotels("makkah", elderly_friendly_only=True, limit=10)
    assert result["status"] == "success"
    hotels = result["hotels"]
    assert hotels, "expected at least one elderly-friendly hotel in Makkah"
    assert all(h["elderly_friendly"] for h in hotels)
    distances = [h["distance_to_haram_m"] for h in hotels]
    assert distances == sorted(distances)


def test_search_hotels_budget_cap():
    result = search_hotels("madinah", max_price_sar_per_night=400)
    assert all(h["price_sar_per_night"] <= 400 for h in result["hotels"])


def test_search_hotels_rejects_unknown_city():
    assert search_hotels("riyadh")["status"] == "error"


def test_search_hotels_accepts_arabic_city_names():
    assert search_hotels("مكة")["hotels"] == search_hotels("makkah")["hotels"]
    assert search_hotels(" المدينة المنورة ")["hotels"] == search_hotels("madinah")["hotels"]


def test_data_is_deterministic(tmp_path, monkeypatch):
    import scripts.generate_data as gen  # pythonpath "." (pyproject) makes scripts importable

    committed_dir = gen.DATA_DIR
    monkeypatch.setattr(gen, "DATA_DIR", tmp_path)
    gen.main()
    for name in ("hotels.json", "fx_rates.json"):
        assert (tmp_path / name).read_bytes() == (committed_dir / name).read_bytes(), name
