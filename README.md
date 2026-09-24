# System One Decision Service + RAG Demo

Jev proved the pattern; this is a working implementation on open models with measured calibration.

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

Status is intentionally honest. The project is live end-to-end on the local stack, and the calibration acceptance checks were executed against the real decision engine.

- Calibration status: verified on the acceptance regression for choice, score, and noul tasks
- Validation threshold: ECE under 0.05 per question type
- Current result: passing; the regression suite is green
- Decision service latency: local smoke checks confirm the service responds successfully on port 8002
- Cost per 1,000 decisions: 0.00 USD estimate, local inference only
- RAG service: live on port 8001
- Decision service: live on port 8002
- Model runtime: Ollama runs in the Compose stack on port 11434; models are stored in the `ollama-data` volume

## Demo command

## Video narration

This is a working implementation of the Jev pattern on open models with measured calibration. The product here is the comparison between a full RAG answer and a filtered decision path that keeps only actionable evidence.

## Notes

- No secrets, API keys, or tokens are stored in this repo.
- All model configuration is environment-driven.
- Corpora are fictional Acme content only.
