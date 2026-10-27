# Define the metric and shape contract

Use this reference before writing a query, selecting a renderer or changing an existing view. Inputs are semantic definitions and an approved source; output is one immutable analytical contract consumed by the query compiler, result validator and data adapter. The schema and field names below are a **proposed portable v1 design**. The package supplies contracts and controlled examples; a host implements and verifies the runtime.

## Assign roles without confusing them with columns

| Concept | Meaning | Example |
| --- | --- | --- |
| Source field | Stable approved identity in the input relation | `value`, `ts_utc`, `channel` |
| Metric | Calculation over a defined population at a grain | mean non-null event value in USD |
| Logical role | Responsibility in the chart | `x`, `y`, `y2`, `series`, `time` |
| SQL alias | Exact output property the adapter reads | `x`, `y`, `y2`, `series`, `time`, `s_y` |
| Display label | Human text, independent of access | `Mean value`, `UTC day` |
| Category | Discrete dimension on x, series or a facet | channel A/B; category is not automatically a series |
| Series | Independent sequence/category grouping within a view | one line per channel, or an inner bar band |
| Time | Analytical bucket coordinate or separate animation frame | temporal x for a line; separate time with categorical x for a race |
| Stack | Geometric arrangement of compatible series | derived baseline/topline per x/series; not another metric |

A horizontal bar exchanges screen directions, not the semantic roles: categorical x still identifies the category, y still identifies its metric. A secondary axis assigns a different scale and formatter to y2; it does not grant permission to use a different population secretly or to sum unlike units. A temporal filter field can constrain a category chart without appearing as a returned dimension.

## Separate field meaning from display binding

[The field schema](../assets/field-contract.schema.json) defines an illustrative descriptor; [field examples](../assets/field-examples.json) supply all fields for the SQL fixture plus independent taxonomy cases. The verifier checks the schema, semantic cross-field rules and display-binding adapter. These are design contracts, not a deployed semantic catalog.

| Axis | Definition | Required distinction |
| --- | --- | --- |
| Logical type | Representation and legal parsing: string, integer, decimal, boolean, date, timestamp or duration | An integer account code denotes an identifier, not an amount |
| Semantic meaning | What the value denotes: identifier, nominal/ordinal category, event time, calendar date, elapsed duration, quantity, currency, ratio, free text or flag | Named category membership differs from a measured quantity |
| Analytical role | How a field participates: dimension, measure, time dimension or entity key | One field can group a result and be a filter target |
| Operations | Explicit filter operators, grouping, order and aggregate eligibility | Filterability is a predicate capability, not a data type or access grant |
| Metric contract | Computation over a named population at explicit input/output grains, with units/nulls/state | A measure needs an approved operation; no AVG default follows from numeric storage |
| Scope and provenance | Source identity, descriptor revision/review authority and independently authenticated access restrictions | A reviewed catalog describes meaning; it cannot override server authorization |
| Display binding | Result alias and encoding kind for x/y/y2/series/time | The chart schema's category/temporal/number enum is separate from every preceding axis |

A **categorical** value denotes membership in a discrete group. A **nominal** category has no intrinsic order; an **ordinal** category has a declared order, such as low → medium → high. Its lexical order is not a substitute. A **dimension** groups or slices observations at an identified grain. A **measure** has an explicitly justified computation and unit. Cardinality and numeric storage alone do not decide these roles.

A **timestamp** denotes an instant under an explicit parsing/zone contract. A **date** denotes a calendar date, not automatically midnight UTC. A **duration** denotes elapsed time with a unit; it is a numeric measure, not an event-time axis merely because it concerns time. Calendar buckets and fixed elapsed intervals differ, including across daylight-saving changes. Unknown meaning or a conflicting type/operation yields a missing-input or invalid decision rather than a guessed class.

The descriptor's operations list states semantic eligibility, while the capability registry states what an implemented adapter/version supports. Both must allow the operation. For example, a catalog can permit weighted_mean for a currency field while this instructional chart v1 still requires a versioned metric extension to execute it. Likewise date → temporal is an encoding decision, not proof that the UTC-text fixture driver handles arbitrary calendar dates.

A deterministic binding adapter checks the field and requested role, then maps nominal/ordinal categories and entity identifiers used as dimensions to category; date/event-time dimensions to temporal; and approved quantitative metrics to number. It rejects free-text grouping without explicit admission, duration → time, identifier → AVG and any undeclared operation. Mapping to an encoding never changes the field's meaning or parsing requirements. The fixture ts_utc field has timestamp meaning but a normalized UTC-text driver representation.

The descriptor records nullable and missingPolicy independently. retain_null preserves unknown measurement; explicit_group requires a declared collision-safe null-group identity and label; reject fails at the boundary. A nullable source category does not authorize dropping rows or coercing null to an empty string. This chart v1 requires non-null result dimensions: the compiler must use an explicit admitted missing-group projection or return an unsupported result before preparation.

A **filter** is a predicate: target field, operator, typed value, purpose, authority and editability. The field schema's predicate definition distinguishes analytical predicates from server-derived authorization restrictions. The host receives authenticated scope through a trusted channel and executes authorized_population ∩ analytical_predicates; values claiming authority=server inside caller/model JSON are untrusted. A user may select every visible category and still cannot expand the authorized population. Scope is enforced again by the executor/database.

Predicate operator meanings are explicit: eq/ne compare one non-null value, in admits membership in a nonempty typed list, lt/lte/gt/gte are ordered comparisons, between includes both typed endpoints in [low,high], and is_null uses boolean true for IS NULL or false for IS NOT NULL. Null is never an eq/in parameter or an implicit wildcard. Use the admitted is_null capability for missingness; distinguish it from an empty result or unavailable field. The typed field checker rejects malformed/naive timestamps, booleans as numbers and caller-controlled authorization metadata.

The chart schema's small SQL-predicate subset is deliberately narrower: eq → =, gte → >=, lt → < with bound parameters. An in/between/is_null field capability does not make that operator valid in chart v1; use a tested, versioned compiler extension or return unsupported. Preserve source WHERE, aggregate HAVING and visual hiding as separate operations. See [view changes](view-changes.md) for when retained data is insufficient.

The public field examples demonstrate numeric identifiers, nominal and ordinal dimensions, instant/date/duration parsing, allowed metric operations and scope intersection. Predicate metadata and a passing fixture do not implement authentication or row-level access control.

## Specify the complete portable artifact

The machine-readable [contract schema](../assets/chart-contract.schema.json) is closed to unknown fields. Cross-field rules belong to the [rules engine](rules-engine.md); schema validity alone is insufficient. Its intentionally small operator set covers the worked examples. Weighted means, percentiles, snapshots and rolling windows need explicit extensions, never coercion into a vaguely similar operator.

| Field | Meaning and owning layer |
| --- | --- |
| `version`, `id`, `capabilityVersion` | Schema/adapter compatibility and human artifact identity. `id` is not a content hash. Host computes a separate canonical content digest when caching. |
| `source` | Approved source ID/relation, physical row grain and snapshot identity. Host resolves access; model text cannot grant access. |
| `capability`, `shape` | Registry ID and one of single, long, dual, category-time. Capability registry owns valid combinations. |
| `roles` | Role → exact alias, type, source/metric reference and label. For y/y2, `ref` names a key in `metrics`; for dimensions it names an approved field. |
| `metrics` | Named operation, source inputs, unit, population ID, input null policy, legal merge and state-alias map. Semantic catalog is authoritative. |
| `resultGrain` | Ordered output aliases defining one unique analytical row, e.g. `["x","series"]`. It must equal the selected shape's dimensional identity. |
| `time` | Null, or explicit role/source/zone/grain/origin/half-open interval/missing-bucket policy. Role must be present and temporal. |
| `filters`, `parameterTypes` | Source-scope predicates with positions into bound parameter values. This v1 supports `>=`, `<`, `=`; broader filters require a versioned extension. |
| `order` | Stable SQL/adapter ordering, with deterministic tie-breaks. Temporal series must be chronological independently. |
| `options` | Validated presentation settings. Analytical transformations are not arbitrary display options. |
| `resultPolicy` | Maximum rows/cells and whether complete analytical coverage is required. The result must separately report actual coverage. |

The data response pairs this contract with `{rows, columns, snapshot, contractHash, resultRevision, coverage, warnings}`. `coverage` records scope and completeness, truncation detection method and any Top-K restriction. Those envelope fields are a host integration specification, not fields emitted by the model. A result cap is a resource bound, not evidence of completeness. A response with no rows still carries typed column metadata.

The synthetic metric fragment in [category-avg](../assets/checked-examples.json) is:

```json
{
  "mean_value": {
    "operation": "avg",
    "inputs": ["value"],
    "unit": "USD",
    "population": "filtered-events",
    "nullPolicy": "ignore-input-nulls",
    "merge": "sum-count",
    "state": {"sum": "s_y", "count": "n_y"}
  }
}
```

`filtered-events` means exactly the source rows passing the contract predicates, before grouping. A ratio's `inputs` are ordered `[numerator, denominator]`; both components must use the same eligible population, with their eligibility/null behavior defined by the metric catalog. The example's converted/eligible fields are non-null flags; zero denominator returns null. `percent` means the stored y2 value is 0–100, while a unit of `fraction` would mean 0–1. Do not format 50 as 5,000% by applying a fraction formatter to a percentage.

## Define shapes before geometry

| Portable shape | Dimensional identity | Measures | Allowed presentation |
| --- | --- | --- | --- |
| single | x | y | one line or categorical bar, subject to x type |
| long | x + series | y with common meaning/unit across series | multiple lines, grouped bars; stacking only with meaningful addition |
| dual | x | independent y and y2 | dual-axis line; no series in this contract |
| category-time | time + x | y | one category frame at a time, or a registered animation adapter |

The portable stack adapter derives stack coordinates from long rows. A legacy consumer may additionally require an alias `stack`; a compatibility adapter can copy `series` into that alias only if their declared meaning is identical. Do not invent another grouping dimension or sum the copied value. This intentional difference is versioned adapter behavior, not a claim that the two wire contracts are identical.

`timeKey=x` is appropriate only when time is the x coordinate. For category-time, map `xKey=x` and `timeKey=time`; a generic `timeKey ?? xKey` rule erases category identity. A dual result with `{x:t,y:null,y2:4}` keeps the secondary observation; mark validity is per axis.

## Resolve aliases exactly once

Preferred path: the compiler projects canonical aliases, the result validator confirms them on every row and in metadata, and the adapter uses those same exact strings. Custom aliases can be supported by an explicit bijection such as `{x:"bucket_start",y:"avg_amount"}`. Validate case-sensitive properties; reject absent or colliding aliases. Either keep that mapping through every consumer or rename every returned row once and publish the new mapping atomically. Never swap a mapping to `y` while rows still contain only `avg_amount`.

Metrics may carry sufficient-state columns beside their displayed value; these are retained for legal regrouping, not guessed as extra series. A second numeric column is not automatically y2. A multi-metric long shape needs a deliberate metric-ID dimension and compatible units, or separate panels; it is not the same as independent y/y2.

## Verify before advancing

Check the schema, exact alias coverage, unique result tuple, role/metric references, same source snapshot/population, correct time binding, explicit null behavior and allowed options. Check both zero-row metadata and a row where only y2 is valid. Pass the immutable contract to [SQL construction](sql-and-aggregation.md), then pass the validated result to [preparation](prepared-data.md). The numerical verifier covers the supplied shapes; production adapters must also test their real drivers' decimal, bigint and timestamp transport.
