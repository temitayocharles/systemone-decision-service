# System One demo UI

A warm-palette, single-page interface for walking non-technical audiences
through the decision service. It renders probability bars instead of raw JSON
and shows provider, model, routing mode, latency, and tokens when the runtime
returns them.

## Run it

```bash
cd demo/ui
python3 serve_demo.py
```

Then open http://localhost:8080 in a browser.

`serve_demo.py` is a same-origin proxy: it serves the page and forwards
`/health` and `/v2/*` to the runtime (default http://localhost:8002; override
with `--runtime`). The runtime does not serve CORS headers, hence the proxy.

```bash
python3 serve_demo.py --port 8080 --runtime http://localhost:8002
```

## Templates

Six scenario templates ship in the page: email triage, AC support ticket,
Kubernetes alert, contract clause, competitor note, and file review. There is
also a batch mode and a trust panel describing what the model does and does
not do (probabilities only; deterministic code acts on thresholds).

## Status

Schema-validated against the v2 OpenAPI contract. Not yet exercised against a
live provider stack; run the first end-to-end pass locally before any
audience sees it.
