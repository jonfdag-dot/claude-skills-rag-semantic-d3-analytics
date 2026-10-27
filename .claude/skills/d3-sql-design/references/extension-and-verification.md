# Recreate and extend the capability

Use this reference when implementing the package in another product, adding a shape/option, or assessing completion. Inputs are the chosen contracts/rules and host stack; output is a versioned integration with evidence at every boundary. The proposed files below are organization guidance, not files supplied as a new application.

## Build in dependency order

```text
analytics/
  metrics.ts
  capability-registry.ts
  chart-contract.ts
  decide-chart.ts
  compile-query.ts
  validate-sql.ts
  validate-result.ts
  classify-change.ts
charts/
  prepare-data.ts
  adapters/line.ts
  adapters/bar.ts
  chart-instance.ts
  formatters.ts
fixtures/
  metric-and-shape-cases.json
```

Metrics and source catalog own meaning/access identity. Registry owns support. The decision layer consumes both and freezes the contract. Query compilation/model proposal consumes that contract, and SQL validation precedes execution. Result validation consumes actual rows/metadata/coverage. Preparation maps exact aliases and retains analytical values. Render adapters own scales/marks; chart-instance owns asynchronous identity, update and disposal. Formatters own text precision. Change classification decides which earlier boundary must rerun.

Start with single category bars and temporal lines using one numeric metric and explicit nulls. Add long series, then independent dual axes, then stack/race only after their extra semantics and lifecycle exist. Keep framework-specific container properties, React hooks and source-loader choices in the adapter. Import D3 modules through the host's normal dependency system. If an integration evaluates template source dynamically, that is an additional executable-code trust boundary; a chart contract or model response must never grant arbitrary code execution.

## Add one graph shape safely

Write the analytical question and row identity first. For example, a proposed dual-series shape must say whether each series owns one y/y2 pair or whether metrics are long rows assigned to axes. Define units, scale/legend mapping, missing-side behavior, sorting and duplicate policy. Do not simply add `series?` to the old dual type.

Create a new versioned registry entry with experimental state, input/output schemas, required/forbidden roles, options, adapter entrypoint and proving cases. Update the compiler, model-facing registry projection, SQL validation, returned-row validation, alias adapter, renderer, update/destroy and persistence/migration handling together. Keep existing artifact versions readable; never reinterpret old rows under a changed shape. Enable the entry only after its complete pipeline is proven. A type name or menu item alone leaves it unavailable.

## Add one option safely

Classify the option first. Color/label/orientation options affect layout. Normalization, percent stacking, bucket grain, ranking scope and source filters affect analytical meaning or its explicit derived view. Register type, domain, default, compatible variants, transport field and consumer. Unknown options must produce a typed unsupported result rather than being dropped between prompt, payload and template. Trace one non-default value through generation/schema, plan, payload, frontend preparation and actual marks. Test updates and restored artifacts, including clearing an omitted option so stale state cannot survive.

For an analytical transform, define order relative to aggregation, per-series partitioning, nulls, base/denominator, units and inverse/raw-value display. Version its output. For a performance option such as sampling, preserve analytical data and disclose coverage; test extrema/gaps/small series before enabling it. Do not change a production dependency or install a new renderer solely because a registry mentions it.

## Verify at the layer that can prove the claim

| Claim | Smallest meaningful evidence |
| --- | --- |
| Metric and example correctness | Execute synthetic SQL; compare exact expected rows and sufficient-state math; exercise unequal groups, nulls, distinct overlap and independent axes |
| Prompt/contract agreement | Parse candidate union/schema; compare frozen fields and aliases; reject mutated SQL/metric/filter/shape; no model run required for this STATIC example check |
| Arbitrary generated SQL is safe/equivalent | Host AST/compiler tests plus read-only driver/object/function policy; fixture string comparison cannot prove this |
| Complete result coverage | Executor/driver metadata or bounded sentinel protocol tested at row/cell limits, plus declared Top-K/preview handling |
| Adapter preserves values | Typed round-trip including labels, date/category IDs, precision, nulls and per-axis validity; immutable input comparison |
| Option/variant works | Trace producer to consumer and render a non-default fixture; unsupported/disabled variant rejected |
| Updates preserve scope | Filter/regroup/refresh/restore tests compare contract identity, values and coverage; late completion and same-length data changes included |
| Cleanup is complete | Browser resource/subscriber/portal/listener/observer/timer checks over repeated redraw and destroy, including two simultaneous charts and empty/error paths |
| Rendering is faster | Measured workload/environment and separate preparation/layout/paint/transition timings with unchanged correctness; mechanism presence is not speed evidence |

## Run package checks

The executable examples are tested with **Python 3.12**, SQLite from Python's standard library, and the jsonschema version pinned in [requirements.txt](../requirements.txt). An IANA timezone database must be available to Python zoneinfo for America/New_York; on platforms without system timezone data, install the public tzdata package in the environment. The verifier does not install dependencies. The PostgreSQL date-bucketing snippets and D3 snippets are explanatory patterns, not executable database or browser fixtures supplied here.

From this package directory, prepare an environment and run:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -B scripts/verify_examples.py
```

A clean environment containing the declared dependencies is sufficient; no private checkout, graph service, database server, model, credential or local worker is required. The script resolves assets relative to its own file, so it can also be called by absolute path from another working directory. If the runtime floor has not been tested in the adopting environment, report that limit explicitly.

The fixture limits of 64 rows and 256 cells are illustrative bounds chosen to exceed this tiny dataset while exercising resource-policy fields. A host selects and enforces its own bounds consistently at admission and execution based on workload, latency and capacity. A limit does not establish completeness; the result validator still requires coverage evidence.

For package integrity, parse JSON/schema, resolve all relative links, inspect scripts and examples for private context, and compare any native twins while preserving intended metadata differences. A native host owns discovery and registration. For actual adoption, run the AST/driver/permission, complete-result, browser, accessibility, update and disposal checks in the preceding table. No application build or runtime claim follows from a package-only pass.

## Finish with evidence, not a file count

The capability is ready to adopt when a builder can follow metric meaning → selection → contract → SQL → actual result validation → exact alias mapping → prepared data → marks, and can explain which stages rerun for each change. Keep implementation, partial/inactive source, defects and recommendations visibly distinct. Include actual commands, statuses, decisive output and unrun runtime/performance/model checks. Source links locate full implementation details; never reproduce the huge line/bar engines just to make the guide appear complete.

## Trace the complete journey

| Stage owner | Input → output | Required boundary |
| --- | --- | --- |
| Semantic catalog and access layer | Approved source/field descriptors, metric meaning and authenticated scope → scoped planning context | Meaning, operations, provenance and access remain independent |
| Intent/selection/role planner | Request plus catalog and enabled registry → analytical intent, eligible shape and exact bindings | No invented adapter, metric or implicit aggregation; conflicts explicit |
| Grain/query planner | Frozen metrics, filters, time, dimensions, ranking and transforms → versioned query contract | Complete y/y2 definitions and one authoritative operation/population per metric |
| Compiler or model proposal | Trusted contract plus bounded untrusted context → SQL, bound parameter references, role aliases and provenance | Model proposes; host checks structure, immutable fields, safety and equivalence |
| Executor | Validated read-only query under authenticated scope → actual rows, typed columns, snapshot and coverage | Reconcile resource bounds, cancellation and completeness; no cap/preview masquerades as full data |
| Result validator and optional bounded refinement | Result evidence → accepted final artifact or typed failure | Exact grain/alias/type/state; narration and persistence bind to the final data-producing pass |
| Payload/controls bridge | Accepted contract/result/options/labels → explicit raw transport | Preserve every field, nondefault option and revision; raw rows are not already prepared |
| Driver and preparation adapter | Raw transport and field metadata → exact typed immutable analytical rows plus derived view | Precision/nulls/category/time/independent axes survive once; no heuristic reducer |
| Render instance | Prepared current revision plus layout → marks/interactions and update/destroy interface | Own all resources, preserve semantic identity, discard obsolete asynchronous completions |
| Restore/change coordinator | Saved version/spec/snapshot/coverage plus delta → reuse, legal derived rollup or requery | Rebuild preparation rather than revive DOM; declare separately which interaction state is restored |

For each option and capability, preserve a short receipt containing version, source/scope, contract hash, result revision/coverage, adapter version, checks run and the final status. Stable canonical serialization excludes volatile DOM/closure objects. A partial hash over SQL alone cannot establish preservation of the full metric/filter/time contract.

An adopting product chooses persistence, framework and database mechanisms. This package defines the seams and controlled examples; it does not ship the orchestration service, a production SQL AST validator, a general output-union parser, authentication or a complete chart engine.
