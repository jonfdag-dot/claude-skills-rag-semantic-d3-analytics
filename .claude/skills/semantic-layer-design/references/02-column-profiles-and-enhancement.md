# Measure field facts before inferring meaning

Read this to produce generation-bound observations from the exact admitted query population. Inputs are the [intake inventory](01-sql-intake-and-identity.md), native type capabilities, bound SQL/values and source snapshot or collection window. Outputs feed [column meaning](03-column-semantics-and-facets.md) and [value admission](05-value-samples-and-cooccurrence.md).

## Separate the products

Deterministic facts describe observed data. Optional synonym/description enrichment proposes wording. Semantic inference proposes business meaning. Retrieval embeddings index selected text. Each can have independent readiness. Do not require a disabled enrichment path before meaning unless a real consumer depends on it.

Measure the complete admitted query result when exact facts are required. Planner statistics describe estimated physical-table distributions; a sample describes its sampling method/population. Never promote either into exact projected-domain size or an unrestricted uniqueness constraint. SQL row-return limits do not bound rows scanned inside an aggregate.

| Fact | Meaning and null rule |
| --- | --- |
| N | Total rows of admitted population |
| NN | Non-null count for the field |
| D | Distinct non-null values, with exact/estimated/sample method |
| Null fraction | `(N-NN)/N` when N>0; undefined when empty under this contract |
| Range | Supported native MIN/MAX plus type/unit/collation evidence |
| Text lengths | Supported character-length mean/max; missing differs from zero |
| Examples | Bounded selected set with deterministic ordering and actual stored count |
| Physical constraints | Qualified declared PK/FK membership; composite membership is not individual uniqueness |

Validate safe nonnegative counts with `0≤D≤NN≤N` in exact mode. All-null D=0 stays zero. Unknown is not zero; empty is not complete non-null data. Use exact integers or an explicit large-count encoding rather than silently lose precision. Backend operations vary: do not assume UUID/JSON/boolean supports every aggregate just because text/numeric does.

## Build one consistent observation

Group catalog lookup by qualified source/schema/relation/column, with a verified complete result limit. Keep optional physical-key facts separate from valid output statistics, especially expressions. Execute an omnibus aggregate over one bound population where practical. Preserve binding values through the wrapper. For independent statements, retain collection times and disclose their consistency limits.

Select examples before limiting under a declared policy: lexical order, frequency with a stable secondary key, or a reproducible statistical sample. Sorting an arbitrary limited subset afterward does not make selection deterministic. A few examples, frequency-ranked values and a random sample are different products.

A profile record needs full identity/field ID, observation method, N/NN/D, optional typed range/lengths/examples, source-snapshot or collection-window evidence, profile revision and status. Cardinality labels and “small enumeration” hints are derived policy, not analytical roles. Choose thresholds from the workload and test boundaries. A unique date/amount remains temporal/measure; it is not automatically an identifier. Closed cardinality domains require explicit adapters.

Stage profiles without deactivating the prior published generation. Same-generation retries use an idempotent field/revision key; another generation appends. Return expected/persisted/failed field IDs. Storage errors returned as values must be inspected, not just thrown exceptions. Timeout races do not cancel underlying work; align statement, worker, lease and recovery deadlines and record uncertain delivery.

## Derive retrieval text and optional enrichment

Serialize selected permitted facts deterministically with builder version, exact text/hash and source/generation identity. Do not render unknown null fraction as “no nulls” or unique amounts as “unsuitable for aggregation.” Validate embedding response count/order, finite coordinates and dimension under an admitted [space contract](05-value-samples-and-cooccurrence.md). Facts may be ready while embeddings remain pending.

Optional synonyms/descriptions need a typed output schema, exact profile input revision, review state and compatible storage key. A model score is uncalibrated unless validated; do not assign universal confidence. Repair must expect the same array/string/object shape as the original task. Failed optional storage stays failed/absent, without pretending an enhancer ran or that an unconsumed suggestion affected the analyzer.

The workbook computes twelve rows, eight non-null feedback scores, distinct categories and unique billed/time values. Separate empty/all-null variants preserve D=0. Its verifier also tests count distinctions and deterministic sampling. It does not establish scan performance, adapter behavior for every native type, live embedding readiness or model enrichment quality.
