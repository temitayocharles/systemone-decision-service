# System One UI

A browser-first product workspace for the System One Decision Runtime and the RAG evidence layer.

## Product flow

The main action is **Ask System One**. One click runs the complete connected workflow:

1. retrieve relevant evidence from the selected collection
2. generate a grounded RAG answer
3. submit the question, answer, and evidence to System One
4. return typed decision outputs
5. refresh runtime telemetry

The interface exposes progress while the request runs, rather than requiring users to work with API commands.

## Product surfaces

- Engineering / Business collection selection
- collection indexing
- plain-English question input
- live Retrieve → Answer → Decide → Record progress
- grounded answer
- retrieved evidence
- structured choice / probability / score outputs
- configured inference instances
- recent browser activity
- recent question history
- live runtime metrics
- benchmark count
- high-level system architecture
- technical route/model/token details on demand

## Run

Start the repository services:

```bash
docker compose up -d --build
```

Then:

```bash
cd demo/ui
python3 serve_demo.py
```

Open:

```text
http://localhost:8080
```

The UI server is a same-origin proxy:

- `/health` and `/v2/*` → System One Decision Runtime on port 8002
- `/rag/*` → RAG service on port 8001

No front-end build step or external JavaScript dependency is required.
