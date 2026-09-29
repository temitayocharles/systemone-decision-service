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

# 2. Walk through the repository architecture first

The goal of this section is not to teach every line of code. It is to give a nontechnical viewer a mental map before opening the product UI.

## SCREEN

Open the repository/workspace tree.

Keep the root folders visible.

Do not open secrets or the real .env file on camera.

## SAY

Before I use the interface, I want to show you how the system is organized.

At the highest level there are two application services.

One service is responsible for evidence.

The other service is responsible for decisions.

The evidence service is the RAG layer.

The decision service is System One itself.

That separation is deliberate.

It means I can change where knowledge comes from without changing the decision contract, and I can change the decision provider without rebuilding the knowledge system.

## 2A. corpora/ — the knowledge being supplied

## SCREEN

Open the corpora folder.

Show Engineering and Business.

Open one short runbook and one of the longer runbooks just enough for the viewer to see that they are real documents with different lengths.

## SAY

This is the raw knowledge I am feeding into the evidence layer.

In an engineering organization these could be incident runbooks, operating procedures, maintenance manuals, recovery procedures, or standards of practice.

In a mechanical or manufacturing environment they could be equipment manuals, inspection procedures, safety practices, troubleshooting guides, or the material a new engineer might spend weeks learning before becoming productive.

In a corporate environment the same idea could apply to procurement procedures, vendor onboarding, finance controls, customer escalation procedures, HR policies, or service manuals.

The important point is that this material already exists in organizations.

System One does not require that knowledge to be rewritten into prompts by hand.

The RAG layer makes the existing knowledge searchable.

## 2B. rag/ — the evidence service

## CLICK

Open the rag folder, then rag/app.

## SAY

This directory contains the evidence service.

Its job is not to make the final System One decision.

Its job is to turn a large body of knowledge into a small set of relevant evidence for the question I am asking.

### chunker.py

## CLICK

Open rag/app/chunker.py.

## SAY

The chunker breaks large documents into smaller overlapping passages.

That matters because a long runbook could contain thousands of words, but a particular question may only need one or two sections.

Instead of handing an entire manual to the model every time, the system creates manageable pieces that can be retrieved independently.

### embeddings.py

## CLICK

Open rag/app/embeddings.py.

## SAY

The embedding layer converts each text chunk into numbers that represent its meaning.

A simple way to think about that is a map of meaning.

Two passages discussing similar ideas tend to land closer together on that map even when they do not use exactly the same words.

When I ask a question, the question is embedded too.

That allows the system to quickly find the chunks whose meaning is closest to the question.

The embedding is not a rewritten version of the document. It is a numerical representation used for semantic search.

### store.py

## CLICK

Open rag/app/store.py.

## SAY

The vector store is where those embeddings and their source metadata are kept.

In this project that store is Chroma.

The source filename, path, collection, chunk number, and other provenance stay attached so I can trace a retrieved passage back to the document it came from.

### llm.py

## CLICK

Open rag/app/llm.py.

## SAY

Once the relevant evidence has been retrieved, the RAG service can ask the configured language model to produce a grounded answer from that evidence.

That gives me readable context.

But that is still not the final System One decision.

### pipeline.py

## CLICK

Open rag/app/pipeline.py.

## SAY

The pipeline ties those pieces together.

Document to chunks.

Chunks to embeddings.

Embeddings to storage.

Question to retrieval.

Retrieved evidence to a grounded answer.

That is the evidence service.

## 2C. eval/ — measured evidence about providers

## CLICK

Open the eval folder.

Show benchmark_runtime.py and eval/data.

## SAY

This directory is different from the knowledge corpus.

The corpus contains domain knowledge.

The eval directory is where I measure the behavior of the decision providers themselves.

A benchmark uses labelled examples where I already know the expected outcome.

System One can run the same labelled workload against different provider-and-model combinations and record things such as accuracy, calibration error, latency, failure rate, and cost when cost information is available.

The benchmark record also stores provenance such as the run ID, dataset hash, timestamp, and dataset path.

That matters because I do not want System One choosing a model because somebody said it was good.

I want the choice to be based on measured evidence from a known workload.

The small dataset shipped with the repository is useful for exercising the benchmark pipeline.

It is not enough evidence for me to make broad performance claims about one model being better than another.

For a real comparison I would use a representative labelled dataset for the workload I actually care about.

## 2D. decide/ — System One itself

## CLICK

Open the decide folder.

## SAY

This is the decision service.

The evidence layer answers: what information is relevant?

System One answers: given the state and that evidence, what structured decision should the application receive?

### runtime_api.py

## CLICK

Open decide/runtime_api.py.

## SAY

This is the stable API surface.

Applications send state and typed questions to System One.

The request can use the configured default provider, explicitly select a provider, supply an empirical selection policy, or use an ensemble.

The browser UI I will show in a moment is simply presenting these APIs in a way that is easier to follow.

### providers/

## CLICK

Open decide/providers.

## SAY

Providers are configured as runtime resources rather than hardcoded into the application.

That is why I can have a local model and a cloud model behind the same System One interface.

The provider IDs, driver, endpoint, model, optional API key, timeout, concurrency, capabilities, and attributes come from configuration.

I do not have to write new application logic every time I change an inference endpoint.

For local development that configuration can come from environment variables.

In a production environment, secret values should come from the platform's secret-management mechanism rather than being committed to source code.

Do not show the real .env values on camera.

### capabilities.py

## CLICK

Open decide/capabilities.py.

## SAY

Capabilities describe what a configured provider can actually do.

For example, a decision workload may require token log probabilities or another feature.

A provider that cannot satisfy the required capability should not be considered eligible merely because it is configured.

### health.py

## CLICK

Open decide/health.py.

## SAY

Health uses observed runtime telemetry.

If the latest observed request to a provider failed, a health-aware empirical policy can exclude it from selection.

So configuration tells me what should exist.

Telemetry tells me what has actually been happening.

### selection.py

## CLICK

Open decide/selection.py.

## SAY

This is empirical selection.

This is important, because empirical selection is not the same thing as simply using the default provider.

When I supply a selection policy, System One looks at persisted benchmark records and filters the candidates.

It can consider the task type, capabilities, observed health, calibration error, latency, cost, accuracy, and other constraints.

Among the candidates that remain eligible, the current scoring combines measured accuracy, calibration quality, latency, cost, reliability, and the amount of sample support.

So the easiest way to explain empirical selection is:

do not choose the model by brand; choose among eligible models using evidence measured on the work that matters to you.

If no provider has qualifying benchmark evidence, empirical selection fails closed. It does not invent a winner.

### calibration_service.py

## CLICK

Open decide/calibration_service.py.

## SAY

Calibration answers a different question.

Suppose a model says it is 90 percent confident many times.

If outcomes show that those 90 percent predictions are only correct 65 percent of the time, then the raw confidence is overconfident.

Calibration uses labelled outcomes to fit a correction so the reported probabilities better match observed reality.

This implementation uses temperature-based calibration.

The goal is not to make the model smarter.

The goal is to make its probabilities more trustworthy.

### calibration_profiles.py

## CLICK

Open decide/calibration_profiles.py.

## SAY

A calibration profile is stored for a specific provider, model, question type, and version.

That means local Qwen and a cloud model do not have to share the same correction.

Even choice, probability, and score questions can have separate profiles.

### engine_v2.py

## CLICK

Open decide/engine_v2.py.

## SAY

This is the lower-level decision engine used by compatible providers.

It turns the typed questions into model calls and converts model evidence into the normalized System One result.

The important product contract remains the same even when the provider changes.

### runtime.py

## CLICK

Open decide/runtime.py.

## SAY

The runtime is the orchestrator.

It receives the request, resolves the routing mode, invokes the selected provider or providers, records telemetry, and returns the normalized answer.

There are four routing ideas worth separating.

Default means use the provider configured as the runtime default.

Explicit means I choose a specific provider for this request.

Empirical means System One chooses among benchmarked eligible candidates using the selection policy and measured evidence.

Ensemble means more than one provider is invoked and the successful typed results are merged.

Those are deliberately different modes.

## 2E. tests/ — proving contracts before the demo

## CLICK

Open the tests folder.

## SAY

This directory contains the regression tests.

I do not need to walk through every test on camera.

The important point is that the API contract, provider routing, calibration, capability selection, provenance, batching, RAG behavior, and UI expectations are covered here.

The live demo is not the first time these paths are exercised.

## 2F. demo/ui/ — turn the endpoints into a product surface

## CLICK

Open demo/ui.

Show serve_demo.py and system-one-demo-ui.html.

## SAY

Finally, this is the product-facing workspace.

I could demonstrate the whole system with API calls in a terminal, but that would make the architecture harder to follow.

So the UI collects the important endpoints into one place.

It calls the ingest, provenance, retrieve, query, provider, benchmark, calibration, metrics, and decision endpoints.

The local host adapter also lets me connect a read-only source such as my Downloads folder.

Now that we have seen the architecture, I can move into the UI and every part of the screen should have a meaning.

## 2G. Move from the repository into the live UI

## SCREEN

Switch to http://localhost:8080.

Scroll to Knowledge provenance.

## SAY

This is the same architecture expressed as a live product.

Source documents become chunks.

Chunks become embeddings.

Chroma stores them.

A question retrieves the relevant evidence.

The RAG layer produces a grounded answer.

Then System One produces the typed decision.

That provenance view is observable lineage.

It does not claim that we can inspect hidden model reasoning.

## PAUSE

Hold the provenance graph for about three seconds.

## EXPECT

The viewer now has a mental model of both the repository and the UI before the first live question.

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

# 5. Show the grounded answer

## SCREEN

Move to **Knowledge response**.

The bold **Grounded answer** is at the top of the response panel.

## SAY

This is the grounded answer produced from the retrieved evidence.

I keep the answer first because it is the fastest way to understand the result, but the evidence is directly underneath it so I can immediately verify what grounded it.

## PAUSE

Give the viewer enough time to read the first part of the answer.

Do not read the whole answer word-for-word unless it is unusually short.

---

# 6. Show the exact sources used

## SCREEN

Move directly from the grounded answer to **Sources used** underneath it.

## SAY

This is the transparency layer.

These are not generic citations added after the answer.

This is the exact source set returned with the grounded query itself.

For each source I can see the actual runbook or document name, the collection, the chunk, the retrieval distance, and the excerpt that was used.

## SCREEN

Slowly move through the source cards.

For the CrashLoopBackOff example, point out whichever real Engineering documents were actually returned.

Do not predict which files should appear. Read the live source names from the screen.

## SAY

So I get the answer quickly, and immediately underneath it I can inspect the evidence chain that produced it.

## PAUSE

Hold the source cards for two to three seconds.

## EXPECT

The source count matches the source cards shown.

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

# 9. Demonstrate provider routing with the same evidence

## SCREEN

Move to the Inference section.

Show the configured provider cards and the Decision routing control.

## SAY

Now I can demonstrate why provider independence matters.

The providers you see here are not hardcoded into this page.

The UI reads the provider registry from System One.

In my environment I have a local provider and I may also have a cloud provider configured.

I can keep the evidence exactly the same and change only the decision routing.

That gives me a fair way to inspect how different providers behave on the same state and the same typed questions.

## 9A. Default provider

## CLICK

Set Decision routing to Default provider.

## SAY

Default does not mean System One is benchmarking providers.

It means use the provider configured as SYSTEMONE_DEFAULT_PROVIDER, or the first configured provider when no explicit default is set.

This is the simplest production path when I already know which provider I want to use by default.

## CLICK

Run the same Engineering question if necessary.

## SCREEN

Point to the result banner above the Decision card.

## SAY

The result tells me which provider and model actually executed the request, the routing mode, and the measured latency for this live run.

I am not hiding the fact that my local model can be slower on this Mac.

That latency is part of the real execution evidence.

## 9B. Explicit local provider

## CLICK

Open Decision routing and select the actual local provider shown by the UI.

Do not use a scripted provider name if the UI reports a different ID.

## SAY

Now I am explicitly overriding the routing.

For this request System One is not choosing.

I am telling it to use this provider.

That is useful for testing, certification, debugging, or workloads where an application has a hard provider requirement.

## CLICK

Run the same question.

## PAUSE

Show the provider/model, latency, probabilities, recommended path, actionable probability, and score.

## 9C. Explicit cloud provider

Only perform this beat if the cloud provider appears in the configured-provider list.

## CLICK

Choose the cloud provider from Decision routing.

## SAY

Now I am keeping the retrieved evidence and question structure the same, but moving the decision request to the cloud provider.

Nothing in the application contract changes.

The provider changed because of configuration.

## CLICK

Run the same question.

## SCREEN

Show the real result.

## SAY

The probabilities may be different.

The recommended path may be different.

The latency may be different.

That is exactly what I want to observe.

I am not caching a preferred answer and I am not forcing the providers to agree.

This is live provider behavior.

## 9D. Compare configured providers side by side

## CLICK

After a normal question has completed, click Compare providers.

## SAY

This comparison reuses the exact same grounded state and the same typed questions.

System One explicitly invokes each configured provider and displays the real results side by side.

That lets me compare the provider, model, latency, recommended path, actionable probability, and evidence score without changing the evidence between runs.

## SCREEN

Hold the provider comparison table.

## SAY

This table is an observation.

It is not yet a benchmark.

One question can show me that providers behave differently, but it is not enough data to conclude that one provider is generally better.

That is what the benchmark system is for.

## 9E. Empirical selection

## SCREEN

Show the Runtime evidence panel.

Point to benchmark records.

## SAY

Empirical selection is where System One is allowed to choose based on measured evidence.

But it can only do that when benchmark records actually exist.

The benchmark workload contains labelled examples.

Each provider is measured against the same representative task, and the persisted record can contain accuracy, expected calibration error, p95 latency, failure rate, cost when known, sample count, and provenance for the benchmark run.

## CLICK

Choose Empirical selection.

## SAY

With empirical routing, System One first filters out candidates that do not satisfy the policy.

That can include the wrong task type, missing capabilities, unhealthy providers, excessive calibration error, excessive latency, excessive cost, or insufficient accuracy.

Then it scores the eligible benchmarked candidates using measured accuracy, calibration quality, latency, cost, reliability, and sample support.

If no candidate has qualifying evidence, System One fails closed.

It does not silently pretend that it knows which provider is best.

## EXPECT

If representative benchmark records exist, the live request should return a route labelled Empirical selection.

If no benchmark evidence exists yet, show the UI's honest message and explain that a real benchmark must be run first.

Do not create or claim benchmark results just to make this beat succeed.

## 9F. Ensemble

Only perform this beat when at least two providers are configured and you want to show the merged behavior.

## CLICK

Choose Ensemble · all configured.

## SAY

Ensemble is different again.

Instead of choosing one provider, System One invokes the configured providers and merges the successful typed results.

For a choice question that means combining the probability distributions.

For a probability question it averages the returned probabilities.

For a score it averages the returned scores.

The ensemble latency shown by the runtime reflects the slowest successful provider because they run concurrently.

## CLICK

Run the same question.

## PAUSE

Show the live merged decision.

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

The button should immediately change to a visible indexing state and remain disabled while the background job runs.

## SAY

Now I am sending those normalized local documents through the same knowledge pipeline. The browser is polling the indexing job rather than holding one long request open, so I can see that work is active even when a larger local folder takes time.

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

# 15. Bring benchmark evidence, calibration, and telemetry home

## SCREEN

Show the Runtime evidence panel.

## SAY

There are three ideas here that sound technical but solve very practical problems.

Benchmarks ask: which configured provider has performed well on this kind of labelled work?

A benchmark is like giving several candidates the same exam where I already know the correct answers.

One example is not enough.

I need a representative set before I make a performance claim.

Calibration asks: when a provider says 80 percent, does 80 percent behave like 80 percent in reality?

A model can rank the right answer well and still be overconfident or underconfident.

Calibration uses labelled outcomes to correct the probability scale.

Telemetry asks: what actually happened when the runtime was used?

Which provider ran?

Did it succeed?

How long did it take?

What usage did it report?

Those observations also contribute to provider health.

So I can summarize the three layers this way.

Benchmark evidence helps System One compare providers.

Calibration helps System One trust the probability scale.

Telemetry tells System One what is happening in production.

## SCREEN

Point to the live counts for benchmark records, calibration profiles, and configured providers.

## SAY

These numbers are read from the runtime.

If the benchmark count is zero, I say it is zero.

If calibration has not been fitted, I say it has not been fitted.

The interface should make missing evidence visible rather than filling the gap with a made-up result.

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
