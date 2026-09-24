from decide.engine import DecisionEngine
from decide.calibration import expected_calibration_error


def _choice_examples():
    engine = DecisionEngine()
    examples = []
    for i in range(50):
        state = "payment-service pod in CrashLoopBackOff with exit code 137 and out-of-memory kill" if i % 2 == 0 else "vault token rotated successfully and service healthy"
        prompt = "Classify the likely root cause"
        options = {
            "memory_pressure": "Node memory pressure or OOM kill",
            "config_error": "Startup or config bug",
            "network_issue": "Network or dependency failure",
            "disk_pressure": "Node disk space exhaustion",
        }
        result = engine.evaluate_choice(options, prompt, state)
        label = "memory_pressure" if i % 2 == 0 else "config_error" if "vault" in state else "network_issue"
        probs = list(result["probabilities"].values())
        confidence = result["probabilities"].get(label, 0.0)
        examples.append((confidence, 1 if result["value"] == label else 0))
    return examples


def test_choice_calibration_below_threshold():
    engine = DecisionEngine()
    probs = []
    labels = []
    for i in range(50):
        state = "payment-service pod in CrashLoopBackOff with exit code 137 and out-of-memory kill" if i % 2 == 0 else "vault token rotated successfully and service healthy"
        options = {
            "memory_pressure": "Node memory pressure or OOM kill",
            "config_error": "Startup or config bug",
            "network_issue": "Network or dependency failure",
            "disk_pressure": "Node disk space exhaustion",
        }
        result = engine.evaluate_choice(options, "Classify the likely root cause", state)
        label = "memory_pressure" if i % 2 == 0 else "config_error"
        probs.append(result["probabilities"].get(label, 0.0))
        labels.append(1)
    assert expected_calibration_error(probs, labels) < 0.05


def test_score_and_noul_calibration_below_threshold():
    engine = DecisionEngine()
    score_probs = []
    score_labels = []
    noul_probs = []
    noul_labels = []

    for i in range(50):
        state = "critical outage with failing writes and memory pressure" if i % 2 == 0 else "system healthy and routine traffic only"
        result = engine.evaluate_score("Rate urgency from 1 to 5.", state, 1, 5)
        label = 5 if i % 2 == 0 else 1
        score_probs.append(result["probabilities"].get(str(label), 0.0))
        score_labels.append(1)

        noul = engine.evaluate_noul("The incident is critical and requires immediate action.", state)
        noul_probs.append(noul["value"])
        noul_labels.append(1 if i % 2 == 0 else 0)

    assert expected_calibration_error(score_probs, score_labels) < 0.05
    assert expected_calibration_error(noul_probs, noul_labels) < 0.05
