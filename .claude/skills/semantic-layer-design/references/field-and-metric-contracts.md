# Keep field meanings and metric algebra separate

Read this before introducing a taxonomy or adapting producer records for a consumer. Produce a versioned field/metric contract and explicit adapters. The [schema](../assets/semantic-contract.schema.json) defines a small teaching format; production systems may choose different storage while preserving these meanings and relationships.

## Define independent axes

| Axis | Meaning | Examples and counterexamples |
| --- | --- | --- |
| Physical/logical type | Stored representation and declared parsing behavior | Integer, decimal, string, boolean, date, timestamp, duration; numeric representation alone does not justify arithmetic |
| Semantic meaning | What the value denotes | Entity identifier, nominal category, ordinal category, event time, amount, ratio, free text |
| Analytical role | Participation in a particular question | Entity key, dimension, time dimension, measure; a time dimension may also be filtered |
| Operations | Admitted actions and typed operators | Equality/range filter, grouping, ordering, explicit aggregations; filterability is not a semantic type |
| Metric contract | Population, input/output grain, algebra and interpretation | Sum, weighted mean, minimum, maximum, row/non-null/distinct count, ratio reconstruction, latest snapshot |
| Scope/provenance | Authority and evidence identity | Authenticated scope, source policy, query/parameter revision, generation, observation method, reviewed revision |
| Display binding | Result key and its presentation | x/y/y2/series aliases, label, unit and scale; a second metric is not automatically a category |

Categorical values denote membership in named groups. Nominal categories have no inherent order; ordinal categories have a declared order. Temporal values represent instants, dates, intervals or durations with explicit units, calendar, timezone and endpoint policy where relevant. A dimension groups or slices at a declared grain. A measure has a justified computation and unit. A filter is a predicate with target, operator, typed value, purpose and authority.

The workbook's integer `site_code` denotes an entity identifier. It permits equality and membership filtering and grouping when useful, but no averaging. `started_at` is a timestamp/event time, a time dimension and a range-filter target. `outcome` is a categorical dimension and filter target. A unique observed billed amount remains a measure; observed distinctness does not make it an identifier.

## Use a small identity model

| Record | Key and ownership | Required relationships and lifecycle |
| --- | --- | --- |
| Source | Scope + stable source ID + policy revision | Credential reference stays outside semantic content; source admission must match execution policy |
| Query definition | Scope/source/query ID + immutable revision | Canonical SQL, parameter declaration, bound-population identity and output field inventory |
| Field | Query revision + stable field ID | Ordinal, unique output alias, logical type; qualified physical/expression lineage may be unknown |
| Generation | Scope/source/query/revision/population + generation ID | Expected outputs, snapshot or collection window, status and input hash |
| Profile/meaning/value | Full generation identity + field ID + artifact revision | Facts versus inference versus review; no join by bare display name |
| Reviewed edit | Authorized review receipt + stable target/path + applicable input revision | Set/replace or explicit patch operation; conflicting or stale applicability blocks publication |
| Projection/embedding | Canonical effective revision + serializer/space version | Rebuild from authoritative meaning; invalidate when text/input hash changes |
| Publication/job | Scope/consumer pointer and claim ID/attempt/holder | Compare input identities and required coverage atomically; retain previous published output on failure |

Define parent deletion and invalidation deliberately. Removing a query should revoke serving and invalidate its derived projections; retained audit evidence follows retention policy. A query revision change stages new artifacts instead of mutating history. Shared generations across queries still require each query ID in joins. Foreign keys or a maintained checked relationship map make convention-based joins explicit.

## Define aggregation as algebra

Each metric specifies population/filter, represented fact per input row, grouping/output grain, expression, null behavior, unit, permitted axes, join/fanout constraints and mergeable state. Unknown grain or unit remains a reason a requested operation can be unsupported.

| Operation | Sufficient state and conditions | Invalid shortcut |
| --- | --- | --- |
| SUM | Sum over compatible units/population and additive axes; each fact counted once | Sum repeated event amounts after a one-to-many join |
| AVG | Sum and non-null count, or original observations | Average subgroup averages with unequal counts |
| MIN/MAX | Subgroup extrema for compatible population/units; explicit null policy | Treat sampled extrema as unrestricted source bounds |
| COUNT(*) | Row count at declared fact grain | Count joined rows as distinct events |
| COUNT(value) | Non-null count for that expression | Replace with row count when nulls exist |
| COUNT DISTINCT | Exact distinct set or compatible sketch and error contract | Sum counts of overlapping groups |
| Ratio | Compatible numerator/denominator state; zero-denominator policy | Average computed ratios without denominator weights |
| Latest snapshot | Entity key, order/time and tie-breaking rule | Sum balances across time or assume MAX means latest |

One value 10 and nine values 20 have mean 19; averaging subgroup means gives 15. A balance may add across accounts at one instant but not across instants. Unknown/nonadditive does not default to AVG. Requery when the available result lacks sufficient state; refuse or request reviewed meaning when the metric itself is unsupported.

## Adapt rather than rename

Use a finite versioned domain for each axis and an exhaustive producer→canonical→consumer adapter. An unrecognized enum returns unsupported with its source value; it does not become dimension or zero. Convert temporal grain names only when semantics agree; second-resolution evidence cannot silently become daily. Display formatting is separate from units: a stored unit token is not silently converted to USD.

Dispatch projections by semantic path and payload shape. For a known scalar field, `{"description":{"value":"A category label"}}` projects to the string `"A category label"`. Validate that wrapper exactly. An array remains an array; an arbitrary object with a `value` member is not automatically a scalar. Apply authorized reviewed changes to the canonical object first, then derive every projection. Null, absent, empty array, false and zero require declared meanings.

Analytical predicates intersect server-derived authorization predicates. Keep authorization purpose and source separate from user display/filter controls. Neither a model's privacy label nor a caller's organization ID creates authority. The controlled verifier checks this intersection and the scalar/array/edit boundary; it does not implement a general policy engine.
