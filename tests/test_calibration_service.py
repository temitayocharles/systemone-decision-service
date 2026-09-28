from decide.calibration_service import fit_profile
from decide.calibration_profiles import CalibrationProfileStore


def test_fit_profile_persists_binary_profile(monkeypatch, tmp_path):
    path = tmp_path / "profiles.json"
    monkeypatch.setenv("SYSTEMONE_CALIBRATION_PROFILES", str(path))

    examples = [
        {
            "probability": 0.9 if i % 2 else 0.1,
            "label": 1 if i % 2 else 0,
        }
        for i in range(20)
    ]

    profile = fit_profile(
        provider="p",
        model="m",
        question_type="null",
        examples=examples,
        version="v1",
    )

    assert profile.samples == 20
    assert profile.temperature > 0
    loaded = CalibrationProfileStore(str(path)).get(
        "p", "m", "null", "v1"
    )
    assert loaded is not None
    assert loaded.temperature == profile.temperature
