# System One Decision Service + RAG Demo

Jev proved the pattern; this is a working implementation on open models with honest, measurable calibration.

## Positioning

This repo is a Jev-style implementation built on open models with measured calibration. It is not Jev. It is not a TypeSafe product, and it does not claim parity with TypeSafe RLCD training.

## Directory map

- systemone-decision-service/
  - openapi.yaml
  - EVAL_HARNESS.md
  - corpora/
    - engineering/
    - business/
  - rag/
  - decide/
  - eval/
  - demo/
  - packet/
  - docker-compose.yml
  - README.md

## Quickstart

The supported runtime is Python 3.11 for the local evaluation harness and Docker Compose for the services.

```bash
docker compose up -d --build
docker compose exec ollama ollama pull nomic-embed-text
docker compose exec ollama ollama pull qwen2.5:3b
curl http://localhost:8001/v1/health
curl http://localhost:8002/v1/health
```

Run the live comparison after both health endpoints respond successfully:

```bash
. .venv/bin/activate
PYTHONPATH=. python demo/compare.py --question "My payment-service pod is in CrashLoopBackOff with exit code 137, what do I check first?" --collection engineering --top-k 8 --verbose
```

## Status

Status is intentionally honest: verified means it ran, everything else is labeled as not yet measured.

**2026-09-24 repair:** the decision engine that shipped earlier was a keyword
heuristic that invented probabilities (it boosted winners toward 0.95 and
returned fixed 0.97/0.03/0.5 values for noul). It has been replaced with a real
engine: single-label-token prompts against an OpenAI-compatible
chat-completions endpoint, probabilities from the model's own token logprobs,
temperature scaling fitted by minimizing NLL. Without a configured provider
the service answers HTTP 502 instead of guessing.

- Engine: real logprob implementation; probabilities sum to 1, no boosting.
- Calibration: temperature fitting per question type is implemented and
  unit-tested on synthetic data with known temperatures (recovery verified).
  NOT yet run against a live provider on labeled data, so no measured ECE,
  accuracy, latency, or cost numbers exist yet. Do not claim them.
- Tests: 19 unit + contract tests pass with a mocked provider
  (`pytest tests/`); the one live-provider smoke test skips without
  `DECIDE_API_KEY`.
- Demo: rewritten. Path A queries RAG; Path B retrieves the same chunks and
  filters them with one noul question per chunk ("does this chunk help answer
  the user's question?", default threshold 0.7). Latencies are timed,
  token counts are the providers' own reported usage. Nothing is padded or
  estimated.
- Services: RAG on :8001 (Ollama + ChromaDB), decision on :8002.
- Provider for decisions: set `DECIDE_API_KEY` (and optionally
  `DECIDE_BASE_URL` / `DECIDE_MODEL`) in `.env`; see `.env.example`.
  NVIDIA's OpenAI-compatible endpoint is the default.

## Demo command

## Video narration

This is a working implementation of the Jev pattern on open models. The product here is the comparison between a full RAG answer and a filtered decision path that keeps only actionable evidence, with every number on screen actually measured.

## Notes

- No secrets, API keys, or tokens are stored in this repo.
- All model configuration is environment-driven.
- Corpora are fictional Acme content only.
