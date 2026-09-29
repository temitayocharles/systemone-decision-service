# System One — Live Video Runbook

This is the **single authoritative runbook** for recording the System One video.

It contains the complete camera sequence: what to say, what to show, where to click, what commands to run, when to pause, and what the viewer should notice.

Use these cues only:

- **SAY** — spoken narration
- **SCREEN** — what should be visible
- **CLICK** — exact UI action
- **DO** — command or typed input
- **PAUSE** — intentional on-camera hold
- **EXPECT** — what should appear before continuing

Do not maintain a separate video runbook.

---

# 0. Private preflight — before recording

Do this off camera.

## Repository

```bash
cd /Volumes/512-B/Documents/PERSONAL/AI-LEVERAGE-LAB/workspace/systemone-decision-service

git fetch origin
git status --short
git log -1 --oneline
```

Confirm local `main` is current and the working tree does not contain unresolved conflicts.

## Start the stack

```bash
docker compose down
docker compose up -d --build
docker compose ps
```

Confirm the core services are running:

- System One Decision Runtime — port `8002`
- RAG service — port `8001`
- Chroma — port `8000`
- Ollama — port `11434`

## Start the product UI

```bash
cd demo/ui
python3 serve_demo.py
```

Expected startup output includes:

```text
System One UI: http://localhost:8080
Runtime:       http://localhost:8002
RAG:           http://localhost:8001
Local source:  .../Downloads (read-only)
```

Open:

```text
http://localhost:8080
```

## Prepare the built-in knowledge

In the UI:

1. select **Engineering**
2. click **Index collection**
3. wait for success
4. select **Business**
5. click **Index collection**
6. wait for success
7. return to **Engineering**

This ensures the repository corpora are indexed with current source provenance.

## Verify Downloads access

Select **Downloads** once.

Confirm the UI shows a live local source summary similar to:

```text
Live local source · /Users/.../Downloads · N files · N text-readable · read-only
```

Do **not** reorganize or modify the folder. The adapter is read-only.

Return to **Engineering** before recording.

## Recording integrity

- Never speak benchmark, latency, cost, calibration, token, or probability numbers unless they are visible from the current live run.
- Do not claim a model/provider is better unless representative benchmark evidence exists.
- Do not describe model-internal reasoning as visible.
- The Knowledge Provenance view shows **observable lineage**, not hidden chain of thought.
- Keep credentials and sensitive local filenames off screen if needed.
- If a live stage errors, stop and fix it rather than narrating around the error.

---

# 1. Opening — what System One is

## SCREEN

Start on the **System One browser workspace**.

No terminal on screen.

Keep the full workspace visible.

## SAY

Hello, my name is Temitayo Charles.

A lot of AI systems are very good at generating information.

You ask a question, the system retrieves documents or searches some knowledge, and it gives you an answer.

That is useful, but there is still another problem.

Sometimes the next application does not need another paragraph. It needs a structured decision.

Which option is most likely?

Is this situation actionable?

How strongly does the available evidence support a particular outcome?

That is what System One is for.

System One is a provider-independent decision runtime.

It can work directly from application state, or it can sit behind retrieval so that the decision is grounded in evidence.

## PAUSE

Hold on the clean workspace for about two seconds.

## EXPECT

The viewer understands that System One is the product being demonstrated—not a model-specific chat interface.

---

# 2. Explain the stack to the viewer

## SCREEN

Stay in the browser workspace.

Scroll to **Knowledge provenance**.

Keep the provider/inference area visible afterward if practical.

## SAY

Before I run anything, here is the stack at a high level.

The browser workspace is the product surface.

Behind it are two main application services.

The first is the RAG evidence layer.

Documents enter the system, they are broken into chunks, those chunks are converted into embeddings, and Chroma stores the vector representation so relevant evidence can be retrieved later.

In this local setup, Ollama provides the bundled local models. One model handles generation and local decision inference, while another produces embeddings.

The second service is the System One Decision Runtime.

That is the decision layer.

It receives state and typed questions, resolves an eligible inference instance, applies calibration when available, executes the decision, records telemetry, and returns a normalized result.

The inference target is interchangeable. It can be the local Ollama instance, a hosted compatible endpoint, or another model running inside a cluster.

Around the runtime are calibration profiles, benchmark records, and telemetry.

Those are operational evidence used for calibrated probabilities, empirical routing, health-aware selection, and runtime inspection.

So at a high level the flow is:

documents become searchable evidence,

evidence becomes a grounded answer,

and System One turns the state and evidence into a structured decision.

## SCREEN

Point to the Knowledge Provenance sequence:

**Source documents → Chunk → Embed → Chroma → Retrieved → Grounded answer → Decision**

## SAY

This provenance view is important.

It shows the observable knowledge lineage.

It does not pretend that we can see hidden model reasoning.

What we can see is where the knowledge came from, how it entered the system, what was retrieved, what grounded the answer, and what decision came out.

## PAUSE

Hold the provenance graph for about three seconds.

## EXPECT

The viewer understands:

- UI = product surface
- RAG = evidence layer
- Chroma = vector store
- Ollama or other compatible endpoints = inference resources
- System One Runtime = decision layer
- provenance = real observable lineage

---

# 3. Show built-in knowledge entering the system

## SCREEN

Keep **Engineering** selected.

Show the **Knowledge provenance** panel.

## SAY

I am starting with the built-in Engineering knowledge.

These are actual repository documents and runbooks.

The provenance view tells me how many source documents are present, how many chunks they become, which embedding model is configured, and how many records are currently indexed in Chroma.

## CLICK

If Engineering has not been indexed in the current environment, click:

**Index collection**

If it is already indexed, simply point to the indexed state.

## PAUSE

Let the viewer see the provenance nodes and source-document chips.

## SAY

Notice that the identity of the source is preserved.

The system does not just store anonymous text.

The filename, collection, chunk number, and retrieval metadata stay attached so I can trace an answer back to the evidence that produced it.

---

# 4. Ask the Engineering question

## SCREEN

Scroll back to **Ask System One**.

Ensure **Engineering** is selected.

## DO

Use:

```text
My payment-service pod is in CrashLoopBackOff with exit code 137. What should I check first?
```

## SAY

Now I will ask a normal operational question.

When I submit it, watch the pipeline.

System One is fast, so the interface leaves a visual trace of every stage instead of artificially slowing the backend down.

## CLICK

Click:

**Ask System One**

## SCREEN

Keep the four-stage pipeline visible:

1. **Retrieve** — blue
2. **Answer** — violet
3. **Decide** — amber
4. **Record** — green

The button should become disabled and display:

**System One is working…**

## SAY

First, the system retrieves evidence.

Then it generates the grounded answer.

Then System One produces the typed decision.

Finally, the execution is recorded.

## PAUSE

Do not click anything while the pipeline is moving.

Let the stages finish naturally.

After completion, hold the completed colored stages and their elapsed times for about two seconds.

## EXPECT

All four stages complete.

No error banner is visible.

---

# 5. Show the exact sources used

## SCREEN

Move to **Knowledge response**.

Show **Sources used** before focusing on the grounded answer.

## SAY

This is the transparency layer I care about.

These are not generic citations added after the answer.

This is the source set returned with the grounded query itself.

For each source I can see the actual runbook or document name, the collection, the chunk, the retrieval distance, and the excerpt that was used.

## SCREEN

Slowly move through the source cards.

For the CrashLoopBackOff example, point out whichever real Engineering documents were actually returned.

Do not predict which files should appear. Read the live source names from the screen.

## SAY

So before I even look at the answer, I can inspect the evidence chain.

That makes it much easier to understand what the system actually grounded itself on.

## PAUSE

Hold the source cards for two to three seconds.

## EXPECT

The source count matches the source cards shown.

---

# 6. Show the grounded answer

## SCREEN

Move from the source cards to the bold **Grounded answer** block.

## SAY

Now this is the grounded answer produced from that retrieved evidence.

The important distinction is that I have already seen the sources that support it.

I am not treating the generated answer as a black box.

## PAUSE

Give the viewer enough time to read the first part of the answer.

Do not read the whole answer word-for-word unless it is unusually short.

---

# 7. Show the System One decision

## SCREEN

Move to the **Decision** panel.

## SAY

This is where System One becomes different from a normal RAG answer.

The output is structured.

A **choice** selects a recommended path and gives me the probability distribution across the alternatives.

A **probability** answers a binary question, such as whether the situation is actionable now.

A **score** evaluates a defined scale.

The application receives those typed outputs directly instead of having to interpret another paragraph.

## SCREEN

Show the live:

- recommended path
- probability distribution
- actionable probability
- evidence-strength score

## PAUSE

Hold the decision card for two seconds.

## CLICK

Expand **Technical details**.

## SAY

The technical details are still available when I want them.

Here I can see the actual inference instance, model, latency, and token usage when the provider reports it.

But those details are secondary to the normal user experience.

## PAUSE

Hold briefly, then collapse Technical details.

---

# 8. Connect the provenance graph to the live query

## SCREEN

Return to **Knowledge provenance**.

## SAY

Now the provenance graph has extended beyond ingestion.

The first part shows how the knowledge entered the system:

source documents,

chunking,

embedding,

and Chroma.

The live request then extends the same lineage through:

retrieved evidence,

the grounded answer,

and the final System One decision.

## SCREEN

Point sequentially across:

**Source documents → Chunk → Embed → Chroma → Retrieved → Grounded answer → Decision**

## SAY

That continuity is important.

It means the system can show both how knowledge entered and which knowledge actually participated in this decision.

## PAUSE

Hold the completed lineage for about three seconds.

---

# 9. Show provider independence

## SCREEN

Move to the **Inference** / provider cards.

## SAY

System One is not built around one provider or one model.

These inference instances are configured at deployment time.

In this setup I can have a local instance and a hosted instance behind the same System One contract.

The application talks to System One.

The provider and model behind it remain replaceable resources.

## SCREEN

Show the configured provider-instance names and models that are actually visible.

Do not expose API keys.

## PAUSE

Hold for one to two seconds.

---

# 10. Go further live — connect the real Downloads folder

This is the optional extension that demonstrates System One connecting to knowledge that was **not part of the repository demo**.

## SAY

Everything I have shown so far came from knowledge that was already part of this repository.

I want to go one step further.

I am going to connect System One to something live on this Mac: my actual Downloads folder.

This connection is read-only.

System One is not going to move, rename, or delete anything.

It will only inspect the files, normalize safe content and metadata, and pass that knowledge through the same ingestion and provenance pipeline.

## SCREEN

Scroll to the source tabs.

## CLICK

Click:

**Downloads**

## SCREEN

Show the live local-source summary.

It should show the actual local Downloads path, file count, text-readable count, and **read-only** state.

## SAY

This is not a Docker-mounted demo folder.

The small System One UI server is running on my Mac with my normal user permissions, so it can read my Downloads folder directly without giving the containers access to my entire filesystem.

Text-like files can contribute their text content.

For other files, System One can still index useful metadata such as filename, type, size, and modified time.

## PAUSE

Hold the local-source summary long enough for the viewer to see the real path and read-only label.

If personal filenames are visible and unsuitable for publication, blur or remove them before recording.

---

# 11. Index Downloads live

## CLICK

Click:

**Connect & index Downloads**

## SAY

Now I am sending those normalized local documents through the same knowledge pipeline.

## SCREEN

Keep **Knowledge provenance** visible as the indexing completes.

## SAY

The files become normalized documents.

Those become chunks.

The chunks are embedded.

Chroma stores the indexed records.

And the source identity stays attached.

## PAUSE

Wait for indexing to finish.

Then hold the provenance graph and the real Downloads source chips.

## EXPECT

The Downloads provenance view shows:

- source files discovered from the live folder
- chunk counts
- embedding model
- indexed Chroma records
- indexed state

---

# 12. Ask a live Downloads question

## SCREEN

Return to **Ask System One** with **Downloads** selected.

## DO

Use:

```text
What files in my Downloads folder look important, duplicated, old, large, or worth organizing first?
```

## SAY

Now this is no longer repository knowledge.

This is a question over a live local source that I connected during the demo.

## CLICK

Click:

**Ask System One**

## SCREEN

Again keep the four-stage pipeline visible:

**Retrieve → Answer → Decide → Record**

## PAUSE

Let the real request finish.

Do not narrate expected files before the system returns them.

## EXPECT

The response completes using the Downloads collection.

---

# 13. Show Downloads provenance and decision

## SCREEN

Show **Sources used**.

## SAY

These source cards now point back to files from my actual Downloads folder.

For text-readable files, the retrieved evidence can include extracted text.

For other entries, the system can still reason over normalized file metadata.

## SCREEN

Show the live source names, metadata, and excerpts that are appropriate for publication.

Then show the grounded answer.

Then show the Decision panel.

## SAY

And from here the rest of System One is unchanged.

The source changed.

The decision architecture did not.

That is the point of the adapter.

A local folder, a repository corpus, and eventually other sources can all normalize into the same evidence and decision pipeline.

## PAUSE

Hold the provenance graph after the Downloads query completes.

---

# 14. Explain what has and has not happened to Downloads

## SAY

One important detail: this integration is deliberately read-only.

System One has inspected and indexed the folder, but it has not reorganized my Mac.

A future action layer could present a proposed organization and require explicit approval before moving anything.

For this demonstration I want the evidence and decision layer to remain separate from filesystem mutation.

## SCREEN

Keep the **read-only** local-source indicator visible if possible.

---

# 15. Briefly explain calibration, benchmarks, and telemetry

## SCREEN

Stay in the product UI.

There is no need to open Swagger unless you specifically want to show API contracts.

## SAY

Behind the decision runtime there are three important operational evidence layers.

Calibration profiles help make model-derived probabilities better aligned with labelled outcomes.

Benchmark records let System One compare configured provider-and-model combinations on representative tasks.

Telemetry records what actually happened at runtime.

Those signals can be used for capability-aware, health-aware, and empirical routing.

I am not going to claim that one provider is better than another unless I have actually collected representative benchmark evidence for that workload.

---

# 16. Optional API proof — only if you want a technical interlude

This beat is optional. The primary demo should remain browser-first.

## SAY

Everything I have shown in the browser is backed by normal APIs.

If I want to prove the runtime contract directly, I can do that too.

## SCREEN

Switch to a terminal.

## DO

From the repository root:

```bash
curl -fsS http://localhost:8002/health
```

Then:

```bash
curl -fsS http://localhost:8002/v2/providers
```

Optional live certification:

```bash
PYTHONPATH=. python scripts/certify_runtime.py \
  --runtime-url http://localhost:8002
```

## EXPECT

Health succeeds.

Configured providers are visible.

Certification prints `PASS` when the live configured runtime is healthy.

## SAY

The browser is the product surface.

The API remains available for applications and automation.

## SCREEN

Return to the browser immediately after this proof.

---

# 17. Closing

## SCREEN

Return to the completed provenance view or the main System One workspace.

## SAY

That is System One.

The browser is the product surface.

The evidence layer can work with built-in runbooks or a live source such as my Downloads folder.

The provenance view shows how that knowledge entered the system and which evidence actually participated in the answer.

The Decision Runtime turns state and evidence into typed probabilistic decisions.

And the model behind the runtime remains interchangeable.

The same pattern can sit behind incident triage, support routing, document organization, approvals, email classification, business workflows, or any application that needs a structured decision instead of another free-form answer.

## PAUSE

Hold the completed System One workspace for about three seconds before ending the recording.

---

# Camera checklist

Before pressing Record:

- [ ] Current `main` is synced
- [ ] Docker stack is healthy
- [ ] UI is running on `http://localhost:8080`
- [ ] Engineering indexed
- [ ] Business indexed
- [ ] Knowledge Provenance populated
- [ ] Downloads tab detects the real local folder
- [ ] Sensitive Downloads filenames reviewed
- [ ] CrashLoopBackOff query tested
- [ ] Full Retrieve → Answer → Decide → Record path completes
- [ ] Source cards match the grounded-answer source count
- [ ] Decision card completes without error
- [ ] Technical details expand correctly
- [ ] Downloads indexing tested read-only
- [ ] Downloads live question tested
- [ ] No credentials visible
- [ ] No unmeasured performance claims in narration

---

# Recovery commands

If the stack must be restarted before recording:

```bash
cd /Volumes/512-B/Documents/PERSONAL/AI-LEVERAGE-LAB/workspace/systemone-decision-service

docker compose down
docker compose up -d --build

cd demo/ui
python3 serve_demo.py
```

If local `main` has diverged, do not improvise a merge during recording preparation. Resolve the Git state separately before continuing.

---

# Product endpoints used by this runbook

These are reference only. Normal viewers do not need to see them.

| Purpose | Endpoint |
|---|---|
| System One health | `GET /health` |
| Providers | `GET /v2/providers` |
| Decision | `POST /v2/decide` |
| Runtime metrics | `GET /v2/metrics` |
| Benchmarks | `GET /v2/benchmarks` |
| RAG health | `GET /v1/health` |
| Built-in ingest | `POST /v1/ingest` |
| External-document ingest | `POST /v1/ingest/documents` |
| Retrieve | `POST /v1/retrieve` |
| Grounded query | `POST /v1/query` |
| Knowledge provenance | `GET /v1/provenance/{collection}` |
| Local Downloads status | `GET /local/downloads/status` |
| Local Downloads index | `POST /local/downloads/index` |

The authoritative recording sequence is this file: `docs/RUNBOOK.md`.
