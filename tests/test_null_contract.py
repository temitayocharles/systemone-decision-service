from decide.providers.openai_compatible import _normalize_answer, _normalize_question


def test_canonical_null_question_translates_to_internal_engine_type():
    q = _normalize_question({
        "type": "null",
        "instructions": "Is this actionable now?",
    })
    assert q["type"] == "noul"
    assert q["prompt"] == "Is this actionable now?"


def test_null_aliases_share_the_internal_binary_dispatch_type():
    for qtype in ("noul", "binary", "abstain"):
        q = _normalize_question({"type": qtype, "instructions": "Test"})
        assert q["type"] == "noul"


def test_internal_noul_answer_is_normalized_to_public_null_contract():
    answer = _normalize_answer({
        "type": "noul",
        "value": 0.73,
        "confidence": 0.73,
    })
    assert answer["type"] == "null"
    assert answer["value"] == 0.73
