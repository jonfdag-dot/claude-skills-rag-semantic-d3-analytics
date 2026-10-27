# Build current catalogs for distinct consumers

Read this when turning prepared evidence into analytical context, grounded answers, navigation or renderer metadata. Inputs are one published generation and its [effective meaning](03-column-semantics-and-facets.md), [query contract](04-query-semantics-and-contracts.md) and value evidence. Produce typed consumer projections and verify the fields actually delivered.

## Resolve one current snapshot

Resolve the authenticated query/source identity and one published generation pointer first. Read qualified field IDs with explicit ordering and required coverage. Do not combine active flags, latest timestamps, greatest-row-count selection or last-row-wins reductions into a supposed coherent snapshot. If a field fails projection/schema validation, return partial/error status with failed IDs; catching the exception cannot make the remaining snapshot ready.

A consumer snapshot contains identity/input hash, admitted base SQL/binding reference, fields, tables/lineage, effective query meaning, dictionaries and capabilities. Each field carries stable ID/output alias, native/logical type, meaning/roles/operations, profile facts and missingness, metric/unit/time metadata, display hints and evidence references. Aliases are result names, not proof of physical lineage. Use path/kind adapters before schema validation: unwrap a known scalar `description.value`, preserve arrays/objects, apply reviewed precedence, then independently check cardinality/grain/behavior enum compatibility.

Catalog projections may classify fields for selection, but their categories must map explicitly to the canonical axes. Numeric-ID heuristics never override reviewed identifier meaning. Unknown facts remain unknown. Automatic capability hints such as log scale need actual data-domain validation; numeric type alone does not prove positive values.

## Rank roles with explanations

Use independent temporal, measure, dimension, series, key-like and risk candidate lists when a field can serve several roles. Store evidence/reasons and final constraints separately from scores. Example terms include declared temporal role/native type, reviewed metric eligibility, categorical cardinality, series intent, key evidence and null/unknown risk. Naming heuristics are optional weak candidates. Keep scores in declared bounds and reject ineligible fields explicitly; negative scores or missing cardinality cannot accidentally enter a group.

Workload-selected weights/top-k and cardinality/null thresholds need rationale and boundary checks. A risk flag need not remove an otherwise valid candidate, but the selected role must satisfy its hard type/grain/unit/cardinality constraints. Null rate does not prove uniqueness. A numeric identifier must never become a measure merely because its datatype permits SUM. Preserve explicit user role choices unless they violate an invariant.

Construct dictionaries from bounded permitted samples with actual domain/selected coverage. A semantic digest can show available fields, metric algebra, time roles, unit constraints and sample qualifications. It cannot invent FK relationships when none were supplied. Cache by scope/source/query/revision/population/generation plus semantic/serializer/policy versions; use the same key on get and set. Invalidate on relevant changes rather than rely on a timestamp TTL alone.

## Deliver the analytical contract

The analytical path is intent → roles → entity bindings → reviewed SQL contract → validated execution → statistics/narrative → display payload. Updated questions can reuse frozen artifacts only where their identity/population/metric contract remains compatible. Carry required fields through every mapper; an optional field in the destination type is not evidence the producer supplied it.

| Boundary | Required delivery |
| --- | --- |
| SQL generation | Allowed fields/relations, admitted base/bindings, required authorization/analytical predicates, grouping and metric algebra |
| Narrative | Executed query/result identity, measured statistics, coverage/disclosure and exact unit/behavior/direction metadata when used |
| Renderer | Actual result aliases x/y/y2/series, typed values, independent metric units/scales and labels |
| User explanation | Which population/grain/filter/limits produced the numbers, including omissions or requery requirements |

The workbook's `x` month, `y` billed sum, `y2` visit count and `series` zone exist in the returned row keys. The controlled consumer projection materializes `{identity,rows,bindings}` rather than checking only upstream metric metadata. Each binding has an alias and label; the two metric bindings also carry the admitted metric ID and unit:

| Role | Alias | Label | Metric ID | Required unit |
| --- | --- | --- | --- | --- |
| x | x | Visit month | — | — |
| y | y | Billed amount | billed_total | USD |
| y2 | y2 | Visits | visit_count | visits |
| series | series | Zone | — | — |

Human labels do not replace row keys. The verifier validates the materialized bindings against this declared role contract and metric registry, rejecting missing axis units/labels and swapped units, aliases, labels or metric IDs. USD and visits remain independent units. This is a controlled payload boundary, not a renderer or proof that every application mapper propagates all metadata. Unknown unit is displayed as unknown or blocks an incompatible operation under its own contract. Empty result is explicit, not fabricated chart measurements.

## Grounded answers and navigation

For answers about one query, retrieve separately typed query descriptions, field meaning, profiles and literal samples. Normalize scores within source before mixing them; singleton/equal-score behavior needs definition. Reserve required source classes, select optional candidates by intent, deduplicate by identity/provenance and use context overlap only as declared ranking evidence. A score-gap cutoff can select a useful subset, but it is a workload heuristic; validate behavior when all scores are equal or nearly equal. Count all fallback/header/sample additions before a hard token bound.

Enumeration requires domain coverage evidence. A bounded sample cannot support a complete-list claim. If six states are known but three shown, say six states with examples; do not invent the other three. An analysis-needed response is preferable when neither profile nor meaning exists. Avoid treating top-k evidence as an aggregate population.

For cross-query navigation, intersect candidates with active authenticated ownership first. A ladder can try admitted rewritten query, lexical terms, broader scoped semantic query and catalog fallback. Rank and diversify query candidates, increase detail only under a defined sparse-context condition and cap expansion. Fence each query's context with its identity so same-named fields are not merged. Suggested queries are navigation results, not executed analytical answers.

The verifier checks exact-generation joins, cache keys, the controlled alias/label/metric/unit payload boundary and fixture arithmetic. It does not implement a UI, ranker, answer generator or renderer, and it makes no claim about their quality.
