# Reconstruct the complete preparation and serving journey

Start here for an end-to-end build. The references describe designs; the [workbook](../assets/reconstruction-workbook.json) supplies controlled inputs and expectations, and `python3 -B <package>/scripts/verify_contracts.py` executes selected deterministic seams. It requires Python 3.10+ with standard-library SQLite, creates only an in-memory synthetic database and makes no model/provider call.

## Follow the artifact graph

| Stage | Inputs | Persisted output and next consumer |
| --- | --- | --- |
| [1. Intake](01-sql-intake-and-identity.md) | Admitted source/policy, immutable SQL/parameters and bound population | Exact output inventory/types/optional lineage → profiles |
| [2. Profiles/enhancement](02-column-profiles-and-enhancement.md) | Exact fields, native capabilities and declared population | Observed facts; optional suggestions/retrieval state → meaning and value admission |
| [3. Column meaning](03-column-semantics-and-facets.md) | Current profiles and permitted context | Raw inference revision, canonical reviewed effective meaning and typed facets |
| [4. Query meaning](04-query-semantics-and-contracts.md) | Exact column meanings and SQL | Suggested purpose/roles; separately reviewed analytical contract and typed query facets |
| [5. Values/co-occurrence](05-value-samples-and-cooccurrence.md) | Profiles/meaning plus authorized source population | Admission receipts, ranked literals, conditional companions and retrieval units |
| [6. Entity retrieval](06-entity-resolution-and-semantic-retrieval.md) | Roles/question and ready scoped corpus | Resolved/ambiguous/unresolved tokens and checked bound filters |
| [7. Runtime catalog](07-runtime-catalog-and-consumers.md) | Published facts/meaning/evidence | Consumer snapshot, role candidates, digest/cache and analytical/answer/navigation projections |
| [8. Compilation](08-portable-and-governed-compilation.md) | Admitted mined or reviewed evidence graph | Portable candidates/manifests or governed review/capture prerequisites |
| 9. Orchestration | Required artifact graph, current inputs and worker claims | Fenced attempts, persisted coverage, atomic publication and recovery |

Logical stage numbering is a teaching decomposition, not a required linear queue. For example, value extraction needs column meaning but may precede query inference, while query meaning can consume known field meaning independently of value embeddings. Define actual dependencies from required artifacts; do not invent a required optional enhancer or a reader merely because a writer exists.

## Define the job protocol before workers

Create the complete dependency graph atomically for scope/query/input identity. Idempotency includes the intended operation and admitted input revision; a read-then-insert active-count check is not an atomic concurrency limit. Store job ID, generation, input hash, parent dependencies, state, attempt, holder/lease and explicit expected outputs. Suggested states include queued, running, cancel_requested, completed, failed and cancelled; unknown delivery remains a delivery state, never completion.

Claim under transaction/lease control, increment attempt, return authoritative owner/input/fence and override stale caller payload fields. Start/heartbeat/complete/fail/cancel transitions compare job/generation/attempt/holder/input identity server-side. Only an applied transition counts as acknowledged. A late callback from another holder or prior attempt cannot publish. A cancel request is not a confirmed stop; do not replace a held attempt until its outcome is known under the protocol.

Align statement/provider deadlines, worker deadlines, heartbeat, lease expiry and recovery. Fresh heartbeat and elapsed task timeout have different meanings; define which can recover a task and why. Retrying a timed-out promise does not cancel the original operation. Revalidate fail-closed budget/provider admission before each costly claim. Limit attempts and record retryable versus terminal failures. Delivery success/HTTP acceptance is not persisted work success.

## Publish complete generations

Keep old published output readable while staging new immutable artifacts. Every stage reports expected/persisted/failed IDs and actual payload hashes. Required coverage is not inventory length, settled promises, cross-generation label existence or a success boolean. Facts, semantic readiness and required vector readiness are separate states.

Before promotion, compare current source/query/parameter/policy/effective-review identities, worker fence, required fields/facets/rules and consumer compatibility. Atomically move one publication pointer and store its manifest. Every reader/cache follows that pointer with the same full identity. Concurrent source/query changes fail promotion rather than publish stale artifacts. Record snapshot/materialization identity or collection window honestly; a shared generation does not hold a database transaction open through model calls.

The required failure walkthrough is G1 published → G2 missing one required profile → publication rejected → G1 remains current → retry gets a new attempt/holder → old callback rejected. Optional embeddings can remain pending only if that consumer declares them optional. A required retrieval vector, failed export file or missing serving bridge blocks the corresponding ready claim.

## Rebuild from the workbook

The synthetic `service_visits` data contains twelve visits, numeric site identifiers, category labels/zones/outcomes, timestamp instants, decimal billed amounts and nullable feedback. Row grain is explicitly one visit with projected visit key. A separate missing-key variant is unsupported for deduplication after an item join. One currency USD and UTC calendar are fixture assumptions, never inferred from an amount name.

1. Admit all fields and a separate parameterized outcome variant. Carry bindings through a wrapper; the closed-only variant has eight rows and total1075.
2. Profile the same rows. Preserve exact twelve-row counts, eight non-null feedback scores, unique timestamps/amounts and categorical domains. Empty/all-null variants retain zero.
3. Use supplied candidate meaning as an illustration. Apply the admitted review receipt, unwrap the scalar description, preserve guidance arrays and derive runtime/export/retrieval from one canonical revision.
4. Build query/metric contracts with population/grain, nullable counts, units and mergeable states. Unknown/nonadditive cannot choose AVG automatically.
5. Admit category values under an explicitly illustrative policy. Compute frequencies and conditional companions with completeness and interval bounds; document the contextual text unit.
6. Resolve exact candidate IDs, retain ambiguity/no-match and emit typed bound filters. Intersect analytical predicates with authenticated authorization.
7. Assemble one-generation catalog/cache and execute equivalent controlled SQL. Verify UTC month x, billed sum y, visit count y2 and zone series; labels/units are separate.
8. Build deterministic candidate manifests and check reviewed preaggregation/ratio/snapshot prerequisites. Missing capture/knowledge/serving bridges remain unavailable.
9. Reject partial generation, stale attempt, mismatched input identity and unknown delivery before publication. The verifier is an in-process protocol example; durable atomicity still needs integration evidence.

The verifier also checks weighted-average state, MIN/MAX merging, row/non-null/distinct counts, overlapping distinct groups, repeated amounts after a join, mixed-unit refusal, time-offset bucket differences, compatible encoder pair metadata and canonical file hashes. It emits named pass receipts and fails on a mismatched expectation. These checks do not establish source adapter integration, model quality, authorization deployment, UI behavior or performance.
