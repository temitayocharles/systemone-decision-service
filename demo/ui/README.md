# System One UI

A browser-first workspace for using the System One Decision Runtime and the RAG example service without writing API commands.

The interface is intentionally white, minimal, responsive, and focused on non-technical workflows.

## What users can do

- choose the Engineering or Business knowledge collection
- index the selected built-in collection
- ask a question in plain English
- review retrieved evidence
- generate a structured System One decision
- batch-triage multiple text items
- see runtime and RAG health
- see configured inference instances
- expand technical route/model/token details only when needed

## Run

Start the repository services first:

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

The UI server is a small same-origin proxy:

- `/health` and `/v2/*` go to the System One runtime on port 8002
- `/rag/*` goes to the RAG service on port 8001 after removing the `/rag` prefix

Override endpoints when needed:

```bash
python3 serve_demo.py \
  --port 8080 \
  --runtime http://localhost:8002 \
  --rag http://localhost:8001
```

No front-end build step or external JavaScript dependency is required.
