# Decide what a changed view needs

Use this reference for filters, regrouping, time ranges, graph switches, updates and restoration. Input is the prior validated analytical contract/result plus the requested delta. Output is `reuse`, `merge-state`, `requery` or `unsupported`, with the invalidated artifact identities. This classification belongs to the host rules engine, before the renderer sees new props.

## Classify the change

| Change | Decision and reason |
| --- | --- |
| Color, label format, horizontal orientation, axis tick density, container size | Reuse analytical rows; rebuild only affected layout/marks. Preserve role meanings. |
| Sort complete categories | Reuse; stable order and join keys change, metric values do not. |
| Legend highlight or hide | Reuse if it only changes visibility. Keep summaries based on the declared analytical population and label visible-only summaries separately. |
| Grouped ↔ ordinary stacked bars | Reuse only when long rows have unique x/series, same units and additive meaning; otherwise reject. Recompute stack geometry, never the metric. |
| Ordinary ↔ percentage stack | A new explicitly derived percentage view with denominator scope and zero-total policy; not a style toggle over averages or signed components. Preserve raw values. |
| Hide complete precomputed category rows | Reuse displayed values. Recompute totals only with compatible sufficient state; ratios/shares may require new denominators. |
| Filter by an omitted source attribute | Requery. Aggregates cannot reveal membership no longer retained. |
| Filter numeric source values after grouping | Requery for source WHERE semantics; filtering aggregate y is HAVING/visibility semantics, a different question. |
| Daily → monthly | Merge-state only if complete daily partitions, metric state, zone and boundary alignment suffice; otherwise requery. |
| Monthly → daily | Requery; a coarse aggregate cannot recover fine observations. |
| Change timezone or week origin | Requery unless retained data can reconstruct the new boundary partitions. UTC-day aggregates cannot recover a local-day split. |
| Add y2 or a new series dimension | Requery or use separately validated retained raw data; new shape and per-metric contract required. |
| Change SUM to AVG, or count population | Requery unless exact required state/population is already retained and validated. Labels never change an operator. |
| Expand range, Top-K population or source scope | Requery. A limited prior result cannot answer a wider scope. |
| Data refresh with same shape | New result revision; validate and recompute dependent caches. Same length and first row do not mean same content. |
| Restore history | Reconstruct versioned spec and snapshot/coverage, then prepare again. Never restore DOM, subscriptions or closures. |

## Bind time before drawing it

Use an inclusive start and exclusive end, `[start,end)`, expressed as instants. Distinguish calendar buckets in a named zone from fixed elapsed intervals aligned to an origin. For real PostgreSQL timestamptz data, a calendar-day expression is `date_trunc('day', occurred_at, 'America/New_York')`; serialize the resulting instant explicitly and retain the business zone for labels. A fixed 15-minute window can use `date_bin('15 minutes', occurred_at, origin)`. These snippets are PostgreSQL reference patterns, not executed by the fixture script. [PostgreSQL timezone and bucket semantics](https://www.postgresql.org/docs/17/functions-datetime.html) describes the distinction.

The fixtures deliberately use validated UTC text, so `substr(ts_utc,1,10) || 'T00:00:00Z'` is a transparent daily key in both SQLite and PostgreSQL. Do not reuse that shortcut for offsets, local timestamps or arbitrary formats. The verifier separately checks the 23-hour and 25-hour New York calendar days in 2026 using Python zoneinfo.

Temporal x is ordered by actual bucket instant, then series identity. A category-time view has independent category x and frame time; never sort category labels as though they were dates. Preserve stable category/color identity across frames. Race interpolation is display geometry between observed frames, not new measurements; label or disable interpolation where that would mislead.

Missing time rows cannot break a D3 line by themselves. When the expected cadence and complete range are known, build a grid per series and materialize missing entries as null. Otherwise show only observations and disclose irregular cadence. `.defined` then separates segments at those explicit null entries. Axis ticks are display references and do not define SQL groups. [D3 line gaps](https://d3js.org/d3-shape/line) and [UTC time scales](https://d3js.org/d3-scale/time) support these rendering mechanics.

## Invalidate the correct artifacts

Use separate semantic/SQL, result, prepared-data and layout identities. The semantic key includes metric definitions, source/snapshot, population predicates and bound values, dimensional grain, time zone/origin/range, contract/registry version and analytical transforms. Prepared data also depends on actual result revision and adapter version. Layout depends on dimensions, presentation options, theme and visibility state. Canonical serialization and stable ordering make these identities reproducible; a short prefix of one row does not.

A presentation update can retain result identity. A legal rollup creates a new derived contract/result with provenance to the complete inputs. A requery invalidates results and all downstream artifacts. Preserve the previous chart while pending if useful, but label its state and never mix new labels/filters with old values. Compare generation/revision tokens at every asynchronous handoff; late results cannot overwrite a newer view.

An explicit cached fallback may show prior data with snapshot, coverage and stale/error status. It must not claim new filters succeeded, compute from a preview as a full dataset, or overwrite a valid persisted artifact with a failed candidate. On restore, resolve known schema/adapter versions or run a tested migration; unknown versions yield a clear incompatibility result.

## Verify the decisions

The [example verifier](../scripts/verify_examples.py) checks weighted mean, ratios, distinct overlap, nulls, coarse rollup and changed-range/filter expectations. In the host, exercise same-length data updates, changed labels, filter→undo, refresh failure, stale asynchronous completion, day→month→day and both axes missing independently. Assert contract/result identity and displayed value together. A screenshot of a plausible chart cannot prove the population or grain remained correct.

## Keep authorization scope outside user edits

Receive server authorization restrictions independently of editable analytical predicates. Persist their scope identity with the source/result contract and revalidate it on refresh and restoration. A model-generated contract cannot replace that trusted scope, and a cached result from another principal or scope is never reusable merely because its visible shape matches.

For synthetic channels A/B, let trusted scope permit only A. A caller predicate channel IN (A,B) still returns A; channel=B returns no rows. Attempting to relabel a caller predicate as an editable authorization rule is invalid. [The field fixtures](../assets/field-examples.json) and verifier exercise this set-intersection contract over synthetic rows, not a deployed authentication/database policy.

The availability of a filter control does not imply that a retained aggregate can answer it. Source-row membership must be retained at the required grain; otherwise requery under the same authenticated scope. Server rejection, empty authorized results and unavailable metric state are distinct outcomes and cannot be repaired by widening scope.
