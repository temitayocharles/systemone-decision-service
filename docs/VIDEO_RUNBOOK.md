# System One — Viewer Runbook

This is the camera-facing walkthrough. It is deliberately short and explains the system as a product before showing commands.

## Beat 1 — What System One is

### SAY

System One is a decision runtime.

Most AI applications are good at generating text. System One is for the point where an application needs something more structured: a choice between options, a probability that a statement is true, or a score on a defined scale.

It can work directly from application state, or it can sit behind retrieval so the decision is grounded in evidence.

### SCREEN

Open the System One browser workspace.

Do not begin with a terminal.

---

## Beat 2 — High-level stack overview

### SAY

Before I use it, here is the stack at a high level.

At the top is the **System One browser workspace**. That is the product surface a normal user interacts with.

Behind the workspace are two application services.

The first is the **RAG service**. It handles knowledge ingestion and retrieval. Documents are chunked and embedded, and **Chroma** stores those vectors so the system can retrieve the most relevant evidence for a question.

For the bundled local setup, **Ollama** provides the local models. One model handles generation and decision inference, and another produces embeddings.

The second service is the **System One Decision Runtime**. That is the core of the system. It receives state and typed questions, chooses an eligible inference instance, applies calibration when available, executes the decision, and returns a normalized result.

The inference target is not hardcoded. It can be the local Ollama instance, a hosted endpoint, or a model running somewhere else in a cluster.

Around that runtime are three operational evidence layers: **calibration profiles, benchmark records, and telemetry**. Those allow System One to calibrate probabilities, compare provider/model performance, route empirically, and track what happened at runtime.

So the flow is simple:

A user asks a question.

RAG retrieves evidence.

System One evaluates the state and evidence.

The runtime returns a structured choice, probability, or score.

The application decides what to do with that result.

### SCREEN

Open the **System** panel in the browser workspace and show the architecture diagram.

Then close it and return to the main workspace.

### EXPECT

The viewer understands that the browser is the product surface, RAG is the evidence layer, and the Decision Runtime is the decision layer.

---

## Beat 3 — Ask a real question

### SAY

Now I can use the whole stack from one place.

I choose the knowledge collection and ask a question in plain English.

System One will retrieve evidence, generate a grounded answer, turn that context into a structured decision, and record the execution.

### DO

Use the Engineering collection and submit:

```text
My payment-service pod is in CrashLoopBackOff with exit code 137. What should I check first?
```

### SCREEN

Keep the progress steps visible:

1. Retrieve
2. Answer
3. Decide
4. Record

### EXPECT

The viewer sees the system move through the full pipeline rather than a static form.

---

## Beat 4 — Evidence and answer

### SAY

The left side shows the knowledge response.

At the top is the grounded answer.

Below that is the retrieved evidence so I can see what the system used rather than treating the answer as a black box.

### SCREEN

Scroll through the evidence cards.

---

## Beat 5 — Structured decision

### SAY

The right side is the System One decision.

This is where the output stops being another paragraph.

A **choice** selects the recommended path and shows the distribution across the alternatives.

A **probability** answers a binary question such as whether the situation is actionable now.

A **score** evaluates a defined scale.

The technical details are still available, but they are secondary. I can expand them if I want to see the inference instance, model, latency, or token usage.

### SCREEN

Show the decision card, then expand Technical details briefly.

---

## Beat 6 — Provider independence and runtime evidence

### SAY

System One is not built around one provider or one model.

The inference instances are configured at deployment time.

In this local setup I can have a local instance and a hosted instance available behind the same runtime contract.

The System panel also shows live runtime metrics and how many empirical benchmark records currently exist.

Those benchmark records, together with capabilities, health, calibration, latency, accuracy, failure rate, and known cost, can be used for empirical routing when that evidence has actually been collected.

### SCREEN

Open the System panel.

Show:

- request count
- p95 latency when available
- benchmark count
- architecture
- configured inference instances

Do not claim benchmark superiority unless real benchmark records exist.

---

## Beat 7 — Close

### SAY

That is System One.

The browser is the product surface.

RAG gives it evidence when evidence is needed.

The Decision Runtime turns state and evidence into typed probabilistic decisions.

And the model behind it remains interchangeable.

That same pattern can sit behind incident triage, support routing, email classification, approvals, business workflows, or any application that needs a structured decision instead of another free-form answer.
