# Design for a consumer and an observable failure

Read this when choosing the semantic layer's purpose or deciding which evidence and context a consumer needs. Produce a consumer/failure/receipt record, a context-selection contract and an explicit persistence map. The [field contracts](field-and-metric-contracts.md) define record meanings; [orchestration](09-orchestration-and-reconstruction.md) defines completion.

## Name the consumer

| Consumer | Needs | Observable failure | Decisive receipt |
| --- | --- | --- | --- |
| Reasoning model generating SQL or explanations | Allowed names, metric definitions, selected examples and refusal conditions | Invented field, unsupported join, incomplete sample described as complete | Parsed output plus unknown-reference/contract failure tied to evidence IDs |
| Query surface: database and its application | Types, constraints, authorized scope, read-only execution and budgets | Illegal state, scope escape, duplicate grants or unbounded query | Constraint/authorization/validator result and execution receipt |
| Analytical application | Executed measurements, compatible grain, aliases and display metadata | Repeated amounts summed after a join, missing second-axis unit | Query contract/result identity and final payload assertion |
| Portable context reader | Admitted evidence, stable definitions and a self-contained manifest | Export contains unsupported claim or cannot be reconstructed | Input manifest, per-file hashes and required-section coverage |

One system can have all four. Define which failure each descriptor prevents. A field nobody reads is a candidate for removal after caller inspection; absence of a visible test is not permission to delete it. Use the chain `consumer → bad input or descriptor → observable degradation → receipt → required response`. An amount definition with no unit must cause an unsupported aggregation request or clarification rather than silently assume a currency.

## Stage the context

Use compact entity cards to select relevance, full descriptors to make a decision and deep evidence when the decision requires it. This is a design option, not a requirement to store a semantic layer as a skill directory.

| Tier | Contents | Loading condition |
| --- | --- | --- |
| Card | Stable ID, canonical/display name, what it denotes, roles, use conditions, aliases, anti-triggers, descriptor reference | Needed to select candidate entities; budget the whole card collection |
| Descriptor | Field/metric contract, operations, scope, grain, missingness, reviewed meaning and evidence references | Card selected for the current question |
| Evidence | Profiles, value coverage, conditional companions, declared relationships and validated examples | A particular claim or operation needs supporting facts |

Keep required identifiers and constraints before optional examples. Partition by relevant domain or query scope. If required context cannot fit, return insufficient-context rather than remove identity or safety clauses. Drop optional evidence with an omission receipt; a missing sample cannot become proof of absence.

A card describes what an entity is and when to use it. It cannot replace the derivation rules in its descriptor. For a numeric site code, aliases might include “branch number”; an anti-trigger can say that billed amounts belong to the amount metric. A site label can share business aliases while its ID, uniqueness and filtering behavior remain distinct. Compare confusable siblings together; individually clear descriptions can still route ambiguously.

## Assign persistence responsibilities

Choose stores according to the required consumer, rather than declaring that every architecture must have the same tables. The important separations are responsibilities and lineage:

| Responsibility | Minimum relationship |
| --- | --- |
| Source/query anchor | Authenticated scope → admitted source policy → immutable query and parameter revision |
| Observed facts | Field/generation/population → measurement method, snapshot or collection window and raw statistics |
| Inferred meaning | Exact input facts → raw response revision → validated candidate meaning |
| Effective meaning | Candidate meaning plus authorized reviewed overlay → canonical effective revision |
| Value evidence | Field/population/generation → literal, frequency, coverage and conditional companions |
| Retrieval artifact | Evidence identity → exact serialized text/hash → declared encoder-space contract and readiness |
| Publication/export | Complete manifest → one published pointer per scope/consumer contract |
| Verification | Interaction/attempt → selected evidence and effective revision → validators and executed result |

Retaining raw responses append-only is a proposed audit design. It is useful when old published meaning must remain explainable; it is not a claim about any existing service. Raw and parsed data have different purposes. Runtime consumers should receive a typed selected projection, not an unbounded raw model response. Preserve raw evidence under the applicable retention/privacy policy and avoid logging sensitive content merely for convenience.

Record deterministic reuse distinctly from failure: `status: reused`, input/output identities and no model call is clearer than interpreting null output as success. If a required probe or validation receipt is missing, readiness is unknown or blocked according to the contract. Observability keys must support joining a bad outcome back to its exact profile, meaning revision, value evidence and attempt.

This design permits source facts without model enrichment, and reviewed meaning without embeddings. It does not promise a complete answering service until retrieval, consumer validation and serving/publication are connected and verified.
