# Make capability decisions deterministic

Use this specification to implement the host policy that connects metric meaning, chart selection, SQL and rendering. The output is a decision with a frozen contract or a specific missing/invalid requirement. This is a **proposed design**, not a supplied rules-engine implementation. Define one versioned owner for each rule; disagreement among prompts, schemas and adapters is a conflict to resolve before execution.

## Inputs and decisions

The engine accepts `{request, semanticCatalog, sourceProfile, registry, priorArtifact, requestedDelta, policy}`. Request contains desired analysis and any explicit graph/metric/grain/time choices. The catalog contains approved source and field IDs, metric definitions, units, populations, join cardinality and merge semantics. Profile contains observed types/cardinalities/nulls/range plus evidence scope and snapshot; a profile cannot silently override explicit metric meaning. Registry contains versioned adapters and supported shapes/options. Prior artifact includes its contract, result coverage and revisions. Policy supplies execution limits, allowed sources/functions and repair budget.

Return one of these disjoint results:

```text
Ready {contract, changeAction, requiredChecks, decisionTrace}
NeedsInput {missingFields, question, affectedDecision, decisionTrace}
Unsupported {capability, incompatibleRequirements, alternatives, decisionTrace}
Invalid {stage, ruleId, field, explanation, repairOwner, decisionTrace}
```

`changeAction` is reuse, merge-state or requery. `decisionTrace` records rule IDs, input evidence identity, selected result and brief rationale; it is not private chain-of-thought. Alternatives may be offered but never silently applied when they change metric, population or explicit user choice. No fallback to an arbitrary chart or metric.

## Set precedence before applying rules

Apply hard policy/access/SQL safety first; those constraints cannot be weakened by a chart request. Next use the approved semantic definitions and explicit user analytical intent. If they conflict, ask for a definition change or reject the unsupported operation; do not substitute AVG for SUM automatically. Next enforce the selected versioned capability's shape, roles and option constraints. Then apply requested display preferences within that valid set. Finally use measured profile facts for eligibility and stable defaults. A model recommendation ranks after these constraints.

Treat a frozen prior artifact as authoritative for fields outside an explicitly requested change scope. For a changed field, revalidate downstream dependencies instead of preserving incompatible old SQL. Two authoritative inputs that disagree produce a conflict result. Do not implement “last registry wins,” union of permissive types, or confidence-score override of a hard failure.

Selection is deterministic: filter to enabled/version-compatible adapters; remove candidates failing shape/type/unit/metric/row constraints; honor an eligible explicit variant; otherwise select by analytical intent (temporal trend → line, category comparison → bar), then the lowest-complexity eligible shape, then a stable registry ID tie-break. Do not use a made-up cardinality threshold as a performance guarantee. A configurable product display limit needs measured justification and cannot change metric semantics.

## Register capabilities as executable contracts

A registry record contains `id`, `version`, `state` (experimental, enabled, deprecated, disabled), family/adapter entrypoint, accepted shapes, required/forbidden roles, dimension types, metric eligibility predicates, allowed options/defaults, null/gap behavior, ordering requirements, row/cell bounds, preparation version, update/destroy capabilities and proving fixtures. A disabled adapter is never selectable merely because its schema exists. Pin existing artifacts to their recorded version.

Example registry record, to implement in the destination product:

```json
{
  "id": "line.dualAxis",
  "version": 1,
  "state": "enabled",
  "adapter": "line-dual-v1",
  "shapes": ["dual"],
  "requiredRoles": ["x", "y", "y2"],
  "forbiddenRoles": ["series", "time"],
  "dimensionTypes": {"x": "temporal"},
  "options": {"curveType": ["linear", "monotone"], "stackMode": ["none"], "labels": ["auto", "none"]},
  "nullPolicy": "independent-axis-gaps",
  "order": ["x"],
  "fixture": "daily-dual",
  "requires": ["prepare-v1", "update", "destroy"]
}
```

`enabled` above describes the example target registry only after its adapter checks pass, not an installed implementation provided by this package. Generate model-facing descriptions, contract schemas, eligibility checks and option controls from one registry. Keep host implementation entrypoints out of model-controlled output. The schema's eight IDs are an instructional fixed v1 set; a real extension updates schema/registry together under the [extension recipe](extension-and-verification.md).

| Variant in the portable design | Shape and dimensional rule | Metric/option eligibility |
| --- | --- | --- |
| line.single | single, temporal x | one y; no series/y2; no stacking |
| line.multi | long, temporal x + series | same metric/unit across series; no y2 |
| line.dualAxis | dual, temporal x | independent y/y2; no series or stacking |
| line.stackedArea | long, temporal x + series | additive compatible components; stackMode stacked or explicitly defined percent |
| bar.standard | single, categorical x | one y, vertical/horizontal; no y2/series |
| bar.grouped | long, categorical x + series | compatible value unit; no stack/y2 |
| bar.stacked | long, categorical x + series | additive compatible components; no y2 |
| bar.race | category-time, categorical x + temporal time | one y; no series/y2 in this portable v1; explicit frame/interpolation/missing policy and working adapter |

The portable design restricts race to category plus frame time and derives stack identity from series. Existing consumers with other role vocabularies need an explicit, versioned compatibility adapter; do not combine conflicting schemas by taking their permissive union. Ordinary stacks of means or rates generally lack an interpretable total. Signed values need an explicitly implemented diverging stack; percentage stacks require nonnegative compatible components and a named denominator. A log scale excludes nonpositive values by definition and needs an explicit acceptable policy, not silent filtering.

## Apply rules at their owning boundaries

| ID / precedence | Condition and decision | Enforcement owner / failure behavior |
| --- | --- | --- |
| R01 / 0 | Source, tenant/access and query objects are approved | Admission and executor; reject before generation/execution |
| R02 / 1 | Each metric resolves to a complete definition and population | Semantic compiler; NeedsInput for ambiguous count/mean/denominator |
| R03 / 1 | Source grain and join multiplicity preserve observations | Query planner; reject unproven fan-out or choose a semijoin/pre-aggregation only when equivalent |
| R04 / 1 | Explicit intent is compatible with the metric | Planner; conflict, never arbitrary AVG/SUM substitution |
| R05 / 2 | Adapter exists, enabled, version-compatible and tested | Capability selector; Unsupported if metadata-only |
| R06 / 2 | Shape has exactly permitted roles and dimension types | Contract validator; reject y2+series for dual v1, or category erased by time |
| R07 / 2 | Alias mapping is exact, unique and transportable | Contract/adapter; reject collision, missing key, unsupported alias array |
| R08 / 2 | Time grain/zone/origin/range/missing policy are explicit | Planner; NeedsInput for unresolved temporal meaning |
| R09 / 2 | Aggregate/merge operation agrees with state and units | Metric validator; reject mean-of-means without proper weights or additive distinct counts |
| R10 / 2 | Every option is registered for this adapter/version | Option schema; reject unknown/invalid option, do not drop it silently |
| R11 / 2 | Stack/normalization has defined mathematical meaning | Analytical-view compiler; reject incompatible totals/denominators; transforms create derived fields |
| R12 / 3 | Requested delta can be answered from retained data/state | Change classifier; reuse, merge-state, requery or Unsupported under [view rules](view-changes.md) |
| R13 / 4 | Model output parses and matches bounded candidate schema | Response parser; one structural repair if configured, then fail with owned diagnostic |
| R14 / 4 | SQL AST is safe and expressions/predicates/grain equal the contract | SQL validator/compiler; reject before execution; bounded SQL-only repair cannot remove filters/change metrics |
| R15 / 5 | Execution respects time/cell/row and source constraints | Executor; return typed failure/partial coverage, never manufactured data |
| R16 / 5 | Returned columns/rows match exact aliases and types | Result validator; reject absent columns, invalid numbers/dates and role mismatch |
| R17 / 5 | One row per exact grain tuple; state and output agree | Result validator; reject duplicates or inconsistent AVG/ratio state; do not ask D3 to guess a reducer |
| R18 / 5 | Completeness and snapshot match requested analytical scope | Result validator; reject unknown/truncated scope for full-population operations |
| R19 / 6 | Per-axis gaps/units/order survive preparation | Adapter; retain valid y2 when y null; fail ambiguous coercion; no mutation of analytical rows |
| R20 / 7 | New render has current revision and owns complete cleanup | Render manager; discard obsolete completions, keep labelled prior chart on failure, dispose all owned resources |

Run structural checks first within a stage, then semantic cross-field checks. Accumulate independent diagnostics where useful, but never render a partially approved contract. If one rule requires unavailable meaning, stop only that dependent decision and return the precise question. The model can explain a proposed correction; the host reruns all affected deterministic checks.

## Define repair and invalid-input behavior

Classify failures by owner. Missing field/aggregation/population → caller/semantic catalog. No eligible adapter → capability registry. Malformed SQL/alias → compiler/model artifact. Complete zero-row result or legitimate all-null group → data reality. Timeout/connectivity → infrastructure. Invalid context revision → update coordinator. This keeps a timeout from triggering a different metric and an empty query from deleting a date predicate.

Use a finite repair budget, for example one candidate repair per generation request, with immutable source/metric/filter/grain fields and explicit diagnostics. Handle a provider refusal or incomplete response before parsing a ready candidate; do not treat it as a valid analytical artifact. A requested semantic change creates a new contract revision and reruns dependent stages. Preserve the last valid artifact; an unsuccessful candidate never becomes the saved truth.

## Check decisions with small cases

| Input | Expected decision | Proof |
| --- | --- | --- |
| Day-1 AVG by channel, then combine channels | merge-state with sum/count | (30+90)/(2+1)=40; 52.5 fails R09 |
| AVG bars switched to stacked total | Unsupported under R11 | Summed means 15+90=105 has no defined total meaning |
| Dual daily value/rate plus series request | Unsupported or new explicitly designed shape | R06 rejects an extra role before SQL |
| DISTINCT users across A/B | requery unless exact identities retained | channel scalars 3+1=4; day-1 union is 3 |
| Category race maps timeKey to x | Invalid R06/R19 | x must stay A/B, time must stay bucket instant |
| One row `{x:t,y:null,y2:4}` | Ready for secondary mark if source-valid | independent-axis gap policy |
| Rename labels, resize or reduce tick count | reuse | contract/result revision unchanged; only layout changes |
| Same row count, changed second-row value | recompute result/preparation | explicit result revision changes; R20 prevents stale render |

The [verifier](../scripts/verify_examples.py) is a small fixture checker, not an implementation of this entire engine. It checks the supplied contract/shape/alias/state/math cases and deliberately rejects mutated candidates. Production adoption requires the AST/driver, coverage, option and lifecycle checks identified in the [verification guide](extension-and-verification.md).

## Reconcile declarations with implemented consumers

Maintain one versioned capability record and generate its model-facing projection and structural schemas from the same owner where practical. If a SQL prompt permits a role that the renderer registry forbids, return a conflict; do not merge them into a more permissive contract. A type enum, menu item, template branch or unused helper is evidence of a declaration, not an active supported path.

A shape or option is eligible only when its producer, serialized transport, result adapter, marks, interaction, update, restore and disposal consumers are proven. Examples of incomplete capability evidence include a waterfall label without cumulative start/end geometry, a secondary scale without secondary marks, zoom code without an exposed/transported control, or animation code disabled by a conflicting series style. Require the missing contract/consumer before enabling the feature; do not claim these extensions are supplied by this package.

Profiles and previews are bounded evidence. A product of marginal cardinalities cannot prove exact dimensional tuple uniqueness; inspect tuples. A cap-equal row count cannot prove truncation or complete coverage. A dual-axis overlap-only trim can discard valid independent observations; retain the union of keys unless the requested population explicitly requires intersection. Hard semantic failures remain failures even when a warning could be displayed.
