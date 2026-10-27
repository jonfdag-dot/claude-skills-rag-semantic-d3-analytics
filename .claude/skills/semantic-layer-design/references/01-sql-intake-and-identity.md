# Admit SQL and identify its result fields

Read this when converting an admitted query into a typed output inventory. Produce an immutable query/population record and exact result fields for [profiling](02-column-profiles-and-enhancement.md). Connection, saved query, SQL revision, result alias, physical column, generation and worker attempt are different identities.

## Admit one population

Authenticate scope, resolve the permitted source and policy revision, and validate read-only SQL before storing or testing it. Keep credentials outside semantic records and prompts. A source catalog describes a connection; a query result describes one admitted projection and parameter population. A successful connection or small query test does not establish semantic readiness.

Store canonical SQL with named parameter declarations separately from its bound execution object. A parameter definition needs name, logical type, required/nullability rules, allowed values when applicable and approved-default provenance. A typed string representation for decimal/date values can avoid precision ambiguity on a wire, but define parsing explicitly. Reject undeclared/unused parameters, identifier substitution, invalid/null values, mixed binding modes and missing/unapproved defaults. Never broaden the population when a value is missing.

For the workbook variant the canonical query ends with `WHERE outcome = :outcome`. The admitted value `closed` remains a separate binding. A wrapper such as `WITH base AS (<canonical query>) SELECT COUNT(*) FROM base` carries that same binding object. If an outer query introduces parameters, compose names or positions deterministically and reject collisions. Do not interpolate literals to hide a broken binding path. The verifier executes this seam using SQLite named binding and checks eight rows/1075 billed amount.

Population identity binds SQL revision, parameter schema, admitted values/default approval, source policy and any snapshot/materialization identity. Same SQL with another admitted value is another population. A generation identifier describes derivation; it does not establish a transaction snapshot across later database/model calls.

## Describe the result

1. Introspect permitted source relations using qualified identities and native types. Cache with one documented freshness field plus content/revision identity; check persisted write success rather than trust an HTTP response.
2. Obtain result names/types from database protocol metadata or a read-only describe facility. This must work for empty results. First-row cell values cannot establish native UUID, decimal, date or null-only types.
3. Assign stable field IDs, ordinal positions and unique projected aliases. Reject duplicate aliases unless the entire consumer path supports stable ordinals independently of object keys.
4. Preserve qualified physical lineage when established. Expressions may have expression lineage and unknown source-key facts; never invent a physical column named after an alias.
5. Persist the exact current inventory under query revision/population/generation. Historical active aliases cannot seed or suppress current fields. Seeded unknown statistics differ from measured N=0.

The output contract is `{identity, fields:[{field_id, ordinal, alias, logical_type, lineage, nullable}], describe_status}`. Identity includes authenticated scope/source/query/revision/population/generation. Lineage is a qualified physical reference, expression evidence or explicitly unknown. Native source type and logical representation should both be available when the adapter needs them. Inventory completeness requires all expected fields, not a nonempty list.

## Fail at the right boundary

| Input or failure | Required response |
| --- | --- |
| Empty result without native metadata | Output-schema unavailable; no CREATE/DROP temporary-view fallback under read-only intake |
| Renamed/reintroduced alias | New exact inventory; retire old aliases only in staged generation |
| Two relations project `id` | Unique aliases or fully supported stable-ordinal adapter |
| Computed amount without physical column | Result statistics/expression lineage; physical PK/FK stays unknown |
| Cache/storage error | Failed persistence; old published generation remains available |
| Bound test succeeds, later wrapper loses values | Block preparation; test success cannot stand in for binding propagation |
| Token relation parser finds no relation | Unresolved lineage; no full SQL-lineage claim |

Budget counts should name what they measure: sampled work, query population, returned rows and cells differ. Repeated executions are not source-row ingestion. Never count a helper's presence as a reachable fallback. Rebuild acceptance includes normal, empty, expression, duplicate/renamed aliases, denied source, failed storage and parameter-binding cases. The teaching script covers selected cases; a production describe adapter still needs backend-specific integration evidence.
