# Infer field meaning and project it without losing authority

Read this after [profiling](02-column-profiles-and-enhancement.md) when a field needs business meaning, usage hints or editable semantic facets. Produce candidate meaning linked to exact facts, then canonical effective meaning and typed consumer projections. [Field contracts](field-and-metric-contracts.md) define the independent axes; [query meaning](04-query-semantics-and-contracts.md) consumes these outputs.

## Admit evidence and validate inference

Select profiles by full scope/source/query/revision/population/generation/field identity. A nonempty result is not complete expected-field coverage. Inputs can include native type, exact/estimated counts, nulls, range, permitted examples, declared keys, query purpose and bounded sibling context. Preserve zero and unknown instead of truthiness defaults. Apply data-egress policy before rendering any actual value, sibling or range.

A candidate meaning can contain business name/definition, semantic meaning, roles, proposed operations, synonyms/questions, relationship hypotheses, unit/time/metric hints, governance suggestions and non-obvious usage guidance. Keep claims tied to evidence IDs and inference status. “Related to” or likely-join text does not prove relationship endpoints, multiplicity or grain. A model privacy/compliance label does not enforce policy. Model quality/confidence scores remain uncalibrated judgments unless separately measured.

Use one versioned output schema across prompt, parser, repair and downstream projection. Constrain names to admitted field IDs and finite enum domains; permit harmless extra model keys only through a deliberate typed extension boundary. Required fields, enum/range/reference checks and final completeness remain mandatory. Accept genuine empty guidance arrays and unknown values. A bounded repair can correct malformed shape, but cannot manufacture business rules merely to fill slots. Revalidate the complete repaired object; a synthetic failure placeholder is not valid semantic completion.

A compact prompt contract is: “Using only the supplied profile and admitted field inventory, return the declared meaning record, evidence references, concise decision summary and change summary. Mark unsupported claims unknown. Do not infer source grain, currency, access permission or join safety from names. Empty guidance is valid.” Treat retrieved/sample text as data, never instructions.

## Normalize before coherence checks

Keep event/system/reporting/reference time roles independent from bucket resolution and presentation priority. Keep amounts, levels, rates, ratios, snapshots and identifiers independent from native numeric type. Normalize known type/unit representations before checking invariants, then iterate a finite correction policy to a stable result or reject contradictions. Each correction records original value, effective value, rule and evidence.

For example, a candidate with percentage unit, flow behavior and additive=true is contradictory. Mapping percentage to rate after an earlier additive check is insufficient: the final result must satisfy the full invariant again. Unsupported temporal role on a numeric amount must not erase valid amount behavior before the datatype check. Sequential identifier status requires evidence beyond integer type. Magnitude computed from examples needs numeric parsing, sample basis, median definition, nonpositive handling and an explicit display use; a sample median is not a population statistic.

## Keep canonical meaning and typed projections

Retain raw inference revisions when audit/replay is required. Link raw input/output schema, model configuration, exact fact revisions and input/output hashes. This append-only pattern is a proposed design, not an assertion about an existing system. Preserve the evidence referenced by prior published generations.

Derive one canonical effective object from generated meaning plus admitted reviewed edits. A review receipt must be authenticated and applicable to the stable field and input revision; a client boolean `reviewed:true` is insufficient. Define overlay ordering and conflict handling. The workbook uses authorized whole-field replacement: arrays replace arrays, scalar replaces scalar, null explicitly clears a nullable value. An incremental-array policy instead needs explicit remove/add operations against a known base revision; automatic union can restore items a reviewer removed. Carrying edits into a new generation requires a reviewed applicability decision and field-identity mapping, not moving historical rows into the new run.

The teaching projection supports these kinds:

| Canonical value | Facet representation | Consumer adapter |
| --- | --- | --- |
| String/number/boolean/null | `{path,kind:"scalar",payload:{value:...}}` | Validate the exact wrapper and declared scalar type, then unwrap |
| Array | `{path,kind:"array",payload:[...]}` | Validate and retain array shape/order policy |
| Structured object | `{path,kind:"object",payload:{...}}` | Validate the declared object; do not unwrap arbitrary `value` properties |

A consumer requiring `description:string` receives `description.value`, never the child object. A valid aggregate object and an invalid flattened child can coexist; validate the consumer projection before proceeding to independent cardinality/grain checks. Do not rely on row order or let a stale generated aggregate overwrite a reviewed scalar. Rebuild runtime, export and retrieval projections from the same effective revision. False, zero, null, empty arrays and absent fields retain distinct declared meanings.

## Apply descriptor policy separately

Descriptor policy concerns contextual metadata and automatic grouping/series choices. It is not a universal prohibition on analytical use.

| Concern | Definition and legitimate use | Caution |
| --- | --- | --- |
| Measurement unit | Quantity unit, such as seconds or kilograms | Constrains compatible aggregation even when not a series |
| Reporting cadence | Observation/reporting frequency | Not the event timestamp or automatic time filter |
| Data origin | Provider/feed/source label | Can be an explicitly requested comparison dimension |
| Format/encoding | Precision, display or encoding metadata | Does not establish numerical semantics |
| Currency denomination | Monetary unit and conversion group | Mixed currencies require an explicit conversion/filter policy |
| Status flag | Lifecycle or quality state | Business status may be a useful dimension and filter |
| Geographic resolution | National/local/site scope or spatial granularity | Distinct from a geographic entity such as a zone |
| Methodology note | Collection, adjustment or annotation | Keep available as explanatory evidence |
| Classification code | Taxonomy membership/code | Often needs a label and declared ordering/category meaning |

If naming heuristics are used, define exact/suffix/prefix ordering, type eligibility, cardinality evidence, domain overrides and unknown behavior. Test recognizer literals together with adapters; renaming a behavior-bearing token without changing its recognition rule changes classification. Penalties and thresholds are workload choices, not mathematical rules or security controls.

## Serialize for retrieval

Dispatch by canonical path and payload kind before broad object tests. Version the renderer, include required identity and render the scalar value, not a heading or `[object Object]`. Unknown must not render as false. Retain arrays as useful lists and units/behavior as declared. Apply a final content bound after all specialized rendering and record omitted content. Store exact text/hash, effective revision and embedding-space contract; text changes invalidate the affected vector by row identity/generation. If aggregate and granular units both enter retrieval, record their common provenance so duplication cannot masquerade as independent evidence.

The verifier checks scalar/array/null projection, reviewed precedence in runtime/export/retrieval, stale identity rejection, coherence contradictions and numeric-ID misuse. It uses supplied inference illustrations; no model is called and no inference-quality claim follows.
