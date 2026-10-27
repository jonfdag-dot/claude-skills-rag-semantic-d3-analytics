# Turn query meaning into an analytical contract

Read this when a whole saved query needs purpose, role suggestions or executable analytical constraints. Inputs are exact [intake](01-sql-intake-and-identity.md) identity and [effective column meaning](03-column-semantics-and-facets.md). Query interpretation does not execute SQL and does not prove grain, join safety or reviewed business meaning.

## Compress evidence deliberately

Join profiles and meaning by stable field ID within one query revision/population/generation. Reject mixed generations, missing required fields and fetch errors explicitly. Never assemble “latest” from independent timestamps or bare aliases. Preserve logical/native type, missingness, qualified lineage where known, meaning/roles, allowed operations, unit/time metadata and authoritative review references.

Adapt wrapped scalars, arrays and objects according to path/kind before schema validation. Useful guidance arrays remain arrays; a generic object parser must not reject them merely because another row stores an aggregate. Keep canonical IDs separate from display labels. Shortened names are display text and cannot replace identities in joins or predicates.

Split context into required and optional content before ranking. Reserve requested metric/time/group/filter contracts, authorized scope and units first. Rank optional descriptions, synonyms and examples with explainable evidence. Reordering a shortlist cannot rescue a required field already discarded. Measure the fully assembled prompt, including recovery/header/example additions. If a hard budget cannot fit required context, return insufficient-context rather than remove schema or invent a placeholder.

## Distinguish suggestions from reviewed rules

Query inference can suggest title/purpose, analytical pattern, metric/dimension/time/filter concepts, visualization roles, filter widgets, display defaults and non-obvious guidance. Its output schema must agree with validation and repair: field references are in-scope, operations type-compatible, enums finite and empty guidance legitimate. A concise decision/change summary supports audit without treating model explanations as evidence.

Use the same schema for bounded parse/repair and validate final completeness. Store raw and effective revisions separately when needed. Project only declared facets and record what stays raw; storing a dashboard object does not mean a consumer reads it. Keep independent embedding readiness and exact text/hash versions. A selected projection containing `{text:...}`, `{value:...}`, arrays or `{columns:[...]}` requires a path-specific adapter; serializer headings without their values are not acceptable representations.

The reviewed analytical contract adds what suggestions cannot establish:

| Contract part | Required meaning |
| --- | --- |
| Population | Admitted base SQL, parameter binding, authorization and analytical filters |
| Input/output grain | Represented input fact, available grain keys, grouping/time bucket and permitted rollups |
| Relationships | Qualified endpoints, join type, cardinality evidence and fanout handling |
| Metrics | Expressions, permitted aggregations/axes, mergeable state, unit/conversion, null/zero rules |
| Time | Chosen event/reporting role, timezone, calendar, precision and interval endpoints |
| Result/display | Expected aliases/types, x/y/y2/series bindings, metric/scale units and labels |
| Authority/identity | Reviewed definition/version and exact query/source/policy/population/generation |

Unknown grain remains unknown. Removing the visit key from the workbook projection means it cannot support event deduplication after a one-to-many join. A related-concept string or “join likely” score supplies none of the missing endpoints/cardinality. If source fact grain is reviewed but its key is not projected, state that limitation rather than fabricate the key.

## Generate and verify against the contract

Own and hash the admitted base query. Generate an outer read-only SELECT against that relation through one parameter-preserving composer. Handle trailing delimiters, leading comments, nested CTEs and reserved alias collisions with a real SQL-aware boundary; string concatenation is not a general SQL parser. Validate against allowed names, required filters, metric expressions, grouping and result aliases before execution. Independently enforce source authorization, read-only execution and runtime budgets; [quality and enforcement](quality-and-enforcement.md) details the defenses.

Do not silently constrain dates or top-k merely to fit a budget. Disclose accepted reductions and their effect. If existing rows lack mean sum/count, ratio components, exact distinct state or required grain, requery. A nonadditive metric cannot default to AVG. A mixed-currency sum needs an explicit compatible conversion/filter policy; AVG does not repair mixed units or repeated event amounts.

For a controlled example, the workbook's all-outcome total is 1480, while `outcome='closed'` yields 1075. Monthly closed totals by zone are Harbor610, Hill370 and Lake95 in the declared UTC calendar. That restriction comes from an explicit predicate, not a model's metric name. The verifier executes equivalent SQLite aggregates and checks aliases separately from labels. It also checks mean-of-means, counts, ratio components, invalid grain and joined duplication. These results establish the fixture calculations, not general SQL-generation accuracy.

Publication requires exact current required fields/facets, payload identity, successful storage and validated consumer projections. Failed or partial repair is not coverage; a historical facet label cannot satisfy a missing new payload. See [orchestration](09-orchestration-and-reconstruction.md) before treating a successful stage response as ready.
