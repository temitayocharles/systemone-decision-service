# Build packet

This file is the project packet for the System One Decision Service and RAG Demo. The workspace is built in phases in the order shown in the prompt. Every acceptance condition is checked and the README is updated with the actual executed results.

The package includes the local RAG service, the decision service, the calibration harness, the demo script, and the fictional corpora used to compare RAG-only with RAG plus action filtering.

## Stop conditions and honesty rules (for any agent working this packet)

These exist because an unsupervised run once built a keyword heuristic that
pretended to be a calibrated model. Scope has walls now:

1. **Never invent probabilities.** If the model provider is not configured or
   does not return logprobs, the service answers HTTP 502 with the reason.
   No fallback heuristic, no keyword scoring, no boosted confidence.
2. **Never invent measurements.** Latency is timed, token counts come from the
   provider's own `usage` field, ECE comes from labeled data. If a number was
   not measured, the output says "not reported", it does not estimate.
3. **Calibration claims need labeled data.** Do not assert ECE, accuracy, or
   "calibrated" status without running /v1/calibrate on at least 50 fresh
   labeled examples and reporting the before/after numbers.
4. **Tests must not be circular.** A test may not derive its labels from the
   same logic the implementation uses. Probability math gets deterministic
   unit tests; provider behavior gets mocked contract tests; live-provider
   tests skip without credentials and are never faked.
5. **Stop and report, do not push through.** If a phase's acceptance condition
   cannot be met (no provider key, no labeled data, a dependency is down),
   stop, say exactly what is missing, and leave the code in the honest
   refusing state. "Done" means verified, not "ran without crashing".
