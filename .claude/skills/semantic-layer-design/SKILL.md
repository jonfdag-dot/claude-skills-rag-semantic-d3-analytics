---
name: semantic-layer-design
description: "Designs and reconstructs semantic layers from SQL intake, field profiles and inferred meaning through value evidence, entity resolution, runtime catalogs and governed portable context. Use when defining column or metric contracts, entity aliases, semantic preparation, reviewed edits, generation readiness, text-to-SQL grounding or semantic drift. Not for one SQL query, general vector-index tuning or deploying an application."
---

# Semantic Layer Design

Build meaning that a named consumer can use and verify. A semantic layer transforms storage facts into field definitions, metric contracts, entity evidence and bounded context. Its consumers may be reasoning models, query engines, analytical applications or portable context readers. Each needs a different projection of the same authorized evidence.

## Contract

Inputs are the requested outcome, consumer, admitted source and query identities, query/parameter revisions, output fields, available facts and the intended authority of reviewed meaning. Return typed inputs and outputs, storage relationships, transformation order, failure/readiness rules and a success plus rejection example. Ask when a missing choice changes authority, source population or the requested capability; represent ordinary missing evidence as unknown.

The references describe a proposed architecture. The supplied workbook and verifier demonstrate selected deterministic seams; they are not a complete service, production deployment, model-quality result or performance claim. Reading this skill authorizes no database operation, provider call, migration or deployment. A caller-supplied scope is an assertion to verify against authenticated authority.

Keep source facts, inferred suggestions, reviewed definitions, executed results and display text distinct. SQL type, semantic meaning, analytical role, permitted operation, metric algebra, provenance and display binding are independent axes. A numeric identifier is not a measure. A filter cannot widen authorization. Unknown aggregation does not mean AVG. A partially completed generation is not ready.

## Select the outcome

| Outcome | Open | Produce and check |
| --- | --- | --- |
| Define the consumer, evidence and context tiers | [Consumers and evidence](references/00-consumers-and-evidence.md) | Consumer → failure → receipt, entity cards and storage responsibilities |
| Define field/metric vocabulary or adapters | [Field and metric contracts](references/field-and-metric-contracts.md) | Typed meanings, operations, metric algebra and explicit enum/shape adapters |
| Admit SQL and identify its outputs | [SQL intake](references/01-sql-intake-and-identity.md) | Bound population identity, unique fields and optional physical lineage |
| Measure fields or add optional enrichment | [Profiles](references/02-column-profiles-and-enhancement.md) | Exact/estimated/sampled facts, deterministic examples and independent embedding state |
| Infer field meaning and protect reviewed edits | [Column meaning](references/03-column-semantics-and-facets.md) | Canonical effective meaning, typed facets and shape-aware retrieval text |
| Explain query intent and constrain analytical SQL | [Query meaning](references/04-query-semantics-and-contracts.md) | Population/grain/joins/metrics/filters plus a validated query contract |
| Build a value corpus and companion evidence | [Values and co-occurrence](references/05-value-samples-and-cooccurrence.md) | Admission receipts, actual coverage, conditional observations and compatible text units |
| Resolve words into exact filter bindings | [Entity resolution](references/06-entity-resolution-and-semantic-retrieval.md) | Scoped candidates, explicit ambiguity/no-match and typed bound predicates |
| Feed analytical, answering or navigation consumers | [Catalogs and consumers](references/07-runtime-catalog-and-consumers.md) | Generation-correct snapshots, caches and complete metadata delivery |
| Compile portable or governed context | [Compilation](references/08-portable-and-governed-compilation.md) | Admitted evidence, reviewed definitions, deterministic manifests and publication prerequisites |
| Rebuild the complete chain or diagnose readiness | [Orchestration](references/09-orchestration-and-reconstruction.md) | Stage graph, fenced attempts, persisted coverage and atomic publication |
| Select structural and quality checks | [Quality and enforcement](references/quality-and-enforcement.md) | Protected invariants, meaningful denominators and actual validation receipts |

Read the selected reference and only a missing prerequisite. For an end-to-end design start with orchestration, then follow its stage links. The [schema](assets/semantic-contract.schema.json) defines the small teaching records; the [workbook](assets/reconstruction-workbook.json) supplies original synthetic inputs and expectations. Run the controlled examples from any directory with `python3 -B <package>/scripts/verify_contracts.py`. The script requires Python 3.10+ with the standard-library SQLite module; it uses an in-memory synthetic database and no network, credentials or private checkout.

## Apply the method

Trace producer → transformation → persisted revision → consumer projection. Require one source/query/population/generation identity through every join. Normalize only at declared boundaries: a scalar `description.value` can become a string, while an array or structured object retains its own schema. Apply authorized reviewed edits to one canonical object before regenerating runtime, export and retrieval projections.

Keep the old published generation readable while staging. Publish only after exact required artifacts, type/reference/metric checks, current attempt fencing and successful storage are established. Track optional absence and embedding readiness separately. A shared run identifier records derivation; it does not establish a common source snapshot or authorize the resulting data.
