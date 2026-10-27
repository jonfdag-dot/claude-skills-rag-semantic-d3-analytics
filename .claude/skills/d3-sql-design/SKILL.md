---
name: d3-sql-design
description: "Designs SQL-result-to-D3 capabilities that preserve metric meaning through contracts, aliases, aggregation, view changes and rendering. Use when: rebuilding or adapting an analytical chart pipeline, defining chart/result schemas, or diagnosing metric changes between SQL and marks. Not for: selecting a single chart or styling an isolated component."
---

# Design a SQL-to-D3 capability

Build a system in which metric meaning survives the journey from a question to SQL, returned rows, prepared records and rendered marks. This package is a design guide with proposed contracts, a reusable generation prompt and executable synthetic examples. It supplies neither a complete query service nor chart renderers.

## Contract

Inputs are the requested analysis, approved source and field catalog, metric definitions and populations, source/result grain, available adapters/options, temporal meaning, and any prior artifact plus requested delta. Missing aggregation, count population, denominator, time zone or supported shape yields a precise missing-input or unsupported result. Resolve routine presentation choices from the host's conventions.

Output is a versioned capability design: eligible shape, field/metric/display contract, parameterized SQL, result/coverage checks, exact alias adapter, lifecycle and extension evidence. Distinguish proposed design, implemented integration and checked runtime behavior. A schema or registry name alone does not establish an executable adapter. This skill grants no database, deployment or access authority.

## Choose an outcome

| Outcome | Resource → artifact and check |
| --- | --- |
| Define fields, metrics, shapes and aliases | [Contracts and aliases](references/contracts-and-aliases.md) → field descriptors and chart/result contract; check orthogonal axes, exact aliases and unique grain against the schemas |
| Preserve metric meaning in SQL | [SQL and aggregation](references/sql-and-aggregation.md) → parameterized query and sufficient state; check population, joins, nulls and merge math |
| Select shapes and enforce policy | [Rules engine](references/rules-engine.md) → deterministic decision/diagnostics; check version, eligibility, precedence and owning boundary |
| Give a model a bounded proposal task | [Generation prompt](references/generation-prompt.md) → candidate using the [system template](assets/system-prompt.md); compare frozen contract, SQL, parameters and aliases |
| Adapt rows into renderer input | [Prepared data](references/prepared-data.md) → immutable analytical rows and derived geometry; check types, precision, exact keys, order and independent axes |
| Change filters, buckets or views | [View changes](references/view-changes.md) → reuse, merge-state, requery or unsupported; check sufficient state, scope and invalidation |
| Render, update and dispose | [Rendering lifecycle](references/rendering-lifecycle.md) → instance/update/destroy contract; verify marks, revisions and owned resources in the host browser |
| Verify arithmetic and row shapes | [Worked examples](references/worked-examples.md) → nine synthetic SQL cases and counterexamples; run the package verifier |
| Build the full journey or extend it | [Extension and verification](references/extension-and-verification.md) → module seams, capability/option rollout and evidence receipt; trace producer to actual consumer |

Read only what answers the requested outcome. For a rebuild, start with field/metric meaning and contracts, then rules/SQL/results, then preparation/rendering and update/disposal. The references define their supporting schemas, assets, algorithms and failure conditions without a private source checkout.

## Preserve these invariants

1. Keep logical type, semantic meaning, analytical role, permitted operations, metric definition, scope/provenance and display binding distinct. A numeric identifier is not a quantity; filterability grants no authorization.
2. Resolve each metric explicitly: operation, inputs, population, grain, unit, nulls and mergeable state. No default AVG or SUM follows from numeric storage. Carry y/y2 independently.
3. Return one row per declared dimensional tuple. A renderer cannot silently SUM duplicate aggregate rows.
4. Keep source field, exact returned alias and display label separate. Rename rows and mappings atomically or preserve an explicit bijection.
5. Validate model structure, SQL safety, semantic equivalence, actual result shape/coverage and adapter eligibility separately. Prompts do not enforce them.
6. Preserve exact analytical values. Formatting, sampling, stacking, normalization and transitions produce explicit derived views and cannot redefine the metric.
7. Classify each change as reuse, sufficient-state merge, requery or unsupported. A user predicate can only narrow the server-authorized population.
8. Give every resource an owner and disposer, including all filter subscriptions, portals, events, observers, timers and asynchronous completions.

## Verify

Use [runtime setup](references/extension-and-verification.md#run-package-checks) and `python3.12 -B scripts/verify_examples.py` with [requirements.txt](requirements.txt) installed and timezone data available. The verifier checks synthetic schema, SQL, alias/grain/state arithmetic and targeted contract counterexamples. Report actual commands/results and unrun limits; it proves neither arbitrary SQL safety nor model compliance, PostgreSQL execution, browser cleanup or performance.
