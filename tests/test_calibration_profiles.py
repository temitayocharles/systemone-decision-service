from decide.calibration_profiles import CalibrationProfile, CalibrationProfileStore


def test_profile_round_trip(tmp_path):
    store = CalibrationProfileStore(str(tmp_path / "profiles.json"))
    profile = CalibrationProfile(
        provider="p",
        model="m",
        question_type="choice",
        version="2026-09-28",
        temperature=1.25,
        samples=100,
        ece_before=0.10,
        ece_after=0.03,
    )
    store.upsert(profile)
    loaded = store.get("p", "m", "choice", "2026-09-28")
    assert loaded == profile
    assert store.get("p", "m", "choice").temperature == 1.25
