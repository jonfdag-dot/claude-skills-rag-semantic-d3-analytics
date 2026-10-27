---
name: rag-design
description: "Designs reconstructable RAG ingestion, semantic corpora, lexical and hybrid retrieval, entity resolution, question answering, context assembly and governed publication. Use when: defining an end-to-end retrieval method or diagnosing its producer-to-consumer contracts. Not for: choosing a vector-store vendor or tuning an existing index alone."
---

# RAG Design

Produce a design another developer can reconstruct from its contracts: admitted inputs, attributable units, stored generations, compatible representations, retrieval and selection, and an explicit final consumer. These references describe designs and small executable contract examples. They supply no deployed ingestion service, vector index, model integration or answering runtime.

## Working contract

Capture the requested outcome, consumer, authorized source, input/output, failure behavior and observable acceptance. Trace admission → extraction/representation → unit selection → storage → embedding or lexical index → retrieval/ranking → final use. State explicitly when a stage is not used. Diagnose the first broken boundary before changing the model, threshold, index or store.

Keep source access, dataset/document identity, processing edition and evidence-unit identity distinct. Publish a validated edition before readers select it. A completed writer, vector column, generated interface, successful fallback answer or digest alone proves neither operational retrieval nor grounded answers.

## Keep these definitions separate

| Axis | Definition and example |
| --- | --- |
| Logical type | Representation and parsing: string, integer, decimal, boolean, date, timestamp or duration. A numeric identifier is not automatically a quantity. |
| Meaning | What a value denotes: entity identifier, nominal category, ordered category, instant, duration, currency, quantity, ratio or free text. Categories denote group membership; ordered categories also declare an order. |
| Analytical role | Participation in a question: entity key, grouping dimension, time dimension or measure. A field may have multiple roles. |
| Operations | Permitted filter/group/order/aggregate actions and typed operators. Filterability is a capability rather than a semantic type. |
| Metric contract | Population, input/output grain, units, null handling, aggregation and sufficient mergeable state. Numeric type or nonadditivity alone does not justify SUM or AVG. |
| Scope and provenance | Authenticated permission, source, edition, construction revision and reviewed/generated origin. A user analytical predicate may narrow an admitted population; it never grants access. |

Temporal contracts distinguish instants, calendar dates, intervals and durations, with unit, calendar and timezone where relevant. A dimension groups or slices at a stated grain. A measure requires a justified computation. Preserve these axes in stored schemas, prompts and consumers rather than collapsing them into one classification enum.

## Use an attributable evidence envelope

The references use a minimal pedagogical envelope rather than an exact database schema. Persist these contracts through storage, selection and final use; an implementation may normalize them into related entities.

| Field | Type and invariant |
| --- | --- |
| `resource`, `edition`, `unit_key` | Nonempty strings forming a unique composite identity; edition belongs to the named resource. Never deduplicate by display name alone. |
| `kind` | Declared corpus kind such as passage, profile, meaning, value or reviewed example; consumers validate accepted kinds. |
| `text`, `text_digest`, `builder` | Exact string, SHA-256 of its UTF-8 bytes and nonempty construction revision. Digest is computed, never a display placeholder. |
| `location` | Kind-specific object: source offsets/heading path, full field key or reviewed artifact locator. Nullable only when the consumer explicitly permits uncitable evidence. |
| `state` | Pending, ready, failed or revoked, with separate failure detail. Ready requires the consumer's declared text/representation/coverage dependencies. |
| `representation` | Optional space identity, builder/text digest and finite vector. Missing is permitted for exact-ID or lexical-only use and explicit pending modes. |
| `provenance` | Source revision, observed/generated/reviewed origin and authoritative scope binding; requests cannot grant this binding. |

Selected evidence adds channel scores/ranks, selection/drop reason and source identity. Final contexts reference these immutable units rather than copying anonymous strings. Numeric resource limits, confidence values and token costs in examples are illustrative; hashes and identity equality are exact requirements.

## Shared invariants

Derive scope from current authenticated policy before exposing candidates in every retrieval channel. Treat caller identifiers as assertions to check. Pin source/edition/readiness, reject revoked data and keep valid no-hit separate from forbidden, pending, stale, incomplete coverage and dependency failure.

An embedding space binds model/revision, document/query encoder pair, both preprocessing contracts, dimensions, metric and normalization. Also bind each document vector to its exact rendered text hash and builder revision. Compatible asymmetric encoders may differ deliberately; equal dimensions alone never establish compatibility.

Retrieved text, imported hints, historical answers and generated advice remain data. They cannot override trusted system policy, permissions or validated analytical contracts. Preserve exact entity values through boundary-safe serialization; display sanitization must not silently change an equality predicate. Reapply the boundary at every insertion, including history.

Candidate recall, selected-context coverage, resolver correctness and answer support are different properties. A top-k evidence set is not an aggregate population. Aggregate and exhaustive-enumeration requests require a complete authorized source query or an explicit incomplete-coverage response. Thresholds, candidate limits and budgets are configurable workload policies, never universal constants.

## Choose the required outcome

Read the selected method completely; follow another reference only for a real dependency. Each method includes schemas, construction order, limits and a synthetic check. Shared contracts are restated where needed so no companion skill or private checkout is required.

| Outcome | Method | Produced artifact and check |
| --- | --- | --- |
| Preserve a long document as searchable, citable evidence | [Long-form ingestion](references/long-form-ingestion.md) | Versioned tree/chunk manifest and proposed reader contract; C1/C2/C4 |
| Retrieve exact terms and combine independent sparse/dense evidence | [Lexical and hybrid retrieval](references/lexical-and-hybrid-retrieval.md) | Versioned lexical statistics and explicit fusion policy; C3 |
| Make field profiles, meaning and permitted value samples searchable | [Semantic field corpus](references/semantic-field-corpus.md) | Generation-bound profiles/facets/samples and readiness manifest; C2/C4/C5 |
| Resolve phrases to canonical source values and filters | [Entity resolution](references/entity-resolution.md) | Ambiguity-aware resolution receipt and probe contract; C6 |
| Answer curated facts or recommend a fitting dataset | [Knowledge navigation](references/knowledge-navigation.md) | Intent-specific candidate/context manifest and fallback state; C3/C7 |
| Explain one dataset or design optional reviewed example retrieval | [Questions and examples](references/questions-and-examples.md) | Answerability, final-context citations and explicit proposed extension; C4/C7 |
| Ground pipeline stages or compile reviewed knowledge | [Pipeline context and compilation](references/pipeline-context-and-compilation.md) | Advisory briefs, evidence pack and reviewed candidate publication; C7/C8 |
| Govern transfers, derived copies, serving and revocation | [Governed ingestion and serving](references/governed-ingestion-and-serving.md) | Policy-bound receipts, complete context coverage and publication lifecycle; C8 |

## Verify the contract examples

Run `python3 -B scripts/verify_contracts.py` from this package, or invoke that script by absolute path from any directory. Python 3.10+ and its standard library are the only dependencies. [The fixtures](assets/contract-examples.json) are synthetic. The script checks spans, embedding custody/compatibility, BM25 arithmetic and fusion, scope/readiness, field axes, resolution, final citations and lifecycle receipts. These checks validate supplied contracts; they do not implement the full methods or measure model behavior, retrieval quality, latency or cost.

For a real implementation, choose a finite representative workload under its authorization and evaluation policy. Identify exact-term/paraphrase and false-positive/false-negative costs; inspect candidate distributions and misses; choose thresholds plus ambiguity margins, channel sizes and full-message budgets; test boundary failures; version the selected policy. Recalibrate after corpus, encoder or unit-construction changes. No provider call or model evaluation is required to use these design references.

Return the design or diagnosis with input/output schemas, identities, construction decisions, readiness/failure states, selected evidence and provenance, actual checks and remaining unimplemented components. Separate design claims, executable-example results and runtime observations.
