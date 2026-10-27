# Preserve meaning in SQL and rollups

Use this reference when constructing a query or deciding whether existing result rows can answer a different view. Inputs are the approved source, metric definition, population and target grain. Output is parameterized read-only SQL plus result/aggregation evidence for the adapter. These are proposed reconstruction rules; a host must establish one authoritative metric definition and reject violations at the owning boundary.

## Build the query in semantic order

1. Establish the observation grain and permitted joins. If one event joins three tags, a subsequent SUM(value) counts that event three times unless the intended metric is event-tag exposure. Pre-aggregate each fact relation to the target join key, use a semijoin for filtering membership, or prove the join cardinality. DISTINCT on displayed values is not a general fan-out repair.
2. Apply source predicates and eligibility rules. Keep WHERE (which observations exist), HAVING (which aggregates remain), and visual hiding separate. Resolve parameters outside string concatenation; identifiers come from an allowlist or compiler, not bound values pretending to be identifiers.
3. Derive the time bucket and dimensions. GROUP BY exactly the output grain, not every convenient source column. An extra date or ID creates duplicate chart cells even when the SQL itself is valid.
4. Compute each metric and required merge state at that grain. Independent y/y2 metrics can share a GROUP BY or be aggregated in separate CTEs and joined by keys. Never join by row position. Different eligibility masks are permitted only when independently named and disclosed; no accidental common-denominator inference.
5. Apply analytical transforms after aggregation, in defined partitions/order: e.g. per-series rolling calculation. A window of three returned rows is not a three-day window when days are missing. Normalize only after the metric has its final grain; retain the original values and units.
6. Apply ranking/Top-K at the declared scope, then final ordering and resource bounds. Top-K categories over a period differ from Top-K independently at every timestamp. Define ties, stable secondary keys, remainder semantics and coverage.
7. Validate the SQL artifact before execution, then validate the actual result. Do not confuse SELECT-only syntax with a proof that AVG or its denominator matches the request.

For an approved base SELECT, strip trailing statement terminators before wrapping `WITH base AS (...)`. Preserve query parameters and bind them once. Use a database role with read-only permissions, parser/AST policy, approved objects/functions, single statement, statement timeout, row/cell bounds and cancellation. Lexical regex checks alone cannot prove SQL safety. This guide does not supply a production SQL parser.

## Give every metric a valid merge

| Requested quantity | State at each complete partition | Correct merge over compatible partitions | Invalid shortcut |
| --- | --- | --- | --- |
| SUM(v) | sum plus non-null count if all-null distinction matters | sum of known sums; null if all counts are zero | sum values from overlapping/fan-out populations |
| AVG(v) | sum(v), count(v) | Σsum / Σcount, null for total count 0 | AVG of unweighted group means; SUM of means |
| Weighted mean | Σ(weight×value), Σweight under defined eligibility | Σnumerator / Σweight | weight by result-row count or COUNT(*) when nulls/eligibility differ |
| MIN/MAX(v) | corresponding extremum and validity | min of valid minima / max of valid maxima | SUM or AVG of extrema |
| COUNT(*) | source row count | add only disjoint source-row partitions | count returned aggregates or rendered marks |
| COUNT(v) | non-null input count | add compatible disjoint partitions | include null rows or sum v |
| COUNT DISTINCT(id) | exact identities, or compatible unionable sketch with disclosed error | union then count, or merge the approved sketch | add overlapping distinct-count scalars |
| Ratio/rate | eligible numerator and denominator | Σnumerator / Σdenominator, with defined factor/unit | average rates without weights; assume each row has equal exposure |
| Median/percentile | full required distribution or approved mergeable sketch | use metric-specific algorithm/error bounds | median of medians or mean of percentiles |
| Balance/snapshot | time ordering, entity identity and as-of rule | select last/first valid observation per declared rule | SUM balances across time |

PostgreSQL's aggregate definitions distinguish row counts, non-null counts, and null results for empty aggregates; the fixture verifier independently checks those cases. [PostgreSQL 17 aggregates](https://www.postgresql.org/docs/17/functions-aggregate.html) supports the SQL definitions. Mergeability depends on metric meaning and retained components, not a blanket “non-additive means AVG” rule. [Kimball's additive/non-additive guidance](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/additive-semi-additive-non-additive-fact/) supports that distinction.

A weighted-mean definition names the weight field, eligibility of missing value/weight pairs, whether zero weights are retained and whether signed weights have a separately justified meaning. The ordinary exposure-weighted case uses nonnegative weights, excludes pairs missing either required component, carries Σ(weight×value) and Σweight, and returns null for zero total weight. One value of 10 with weight 1 and one value of 20 with weight 9 gives (10+180)/(1+9)=19; averaging the displayed values gives 15 and loses the population weighting. A result-row count is not a substitute for Σweight. Weighted mean is a documented extension here, not a supported v1 chart operation.

Compatible partitions share expression, units, null/eligibility policy, source snapshot and population definition, and cover disjoint subsets of the intended target population. MIN/MAX can tolerate overlap mathematically, but coverage still must match the question. A scalar result cannot prove these conditions. Keep a population ID and source-grain/provenance evidence, and requery when unknown.

## Preserve empty, zero and precision

An empty global COUNT is 0; an empty grouped query has no group rows. AVG/MIN/MAX/SUM of no non-null inputs are null. Zero is an observed value, not a default for missing measurements. Carry null through the adapter and show a gap/unavailable indicator. Zero-fill only for a complete expected grid and a metric definition proving “no events means zero.” A left join to a calendar needs a count of the non-null fact key; COUNT(*) would count the calendar placeholder.

Keep database numeric/decimal and bigint values exact in the analytical layer. JavaScript Number cannot exactly represent every integer above 2^53−1. Preserve a decimal/integer string or explicit exact numeric type, validate it, and make any chart-coordinate approximation explicit. Round tooltips/axis labels at formatting time. Never parse arbitrary category/time strings as numbers, round retained aggregation state, or compute summaries from a display sample.

## Handle independent axes by key

The [daily-dual example](worked-examples.md#daily-dual-axes) computes total value and conversion rate at the same day grain. y's unit is USD; y2's unit is percent. Its state maps are independent. When measures come from separate CTEs, build the union of x keys and align each result to that key set, retaining a null for the missing side. Do not inner-join away a legitimate observation merely to produce two complete lines. Apply `.defined` independently and label both scales clearly.

If an explicit request also asks for series in a dual-axis shape, this v1 rejects it. Supporting it needs a new shape specifying which metric belongs to which series and axis, plus legend, scale and validation changes. Silently dropping series or assigning every series to y2 changes the analysis.

## Treat bounds and remainders honestly

A LIMIT at raw-observation level biases aggregates. A LIMIT after grouping may omit complete groups. Return metadata distinguishing complete aggregate scope, intentional Top-K, execution truncation and preview. Fetch a bounded sentinel row or use trustworthy execution metadata to detect truncation; equality to a limit is only suspicion. If the platform cannot prove completeness, mark it unknown and reject calculations requiring full coverage.

“Other” is a metric over omitted members, not necessarily a sum of displayed scalar values. AVG needs omitted sum/count, rates need components, distinct counts need identity union or another query. Time-series ranking usually needs a scoped category ranking CTE before selecting all frames for those categories. Never select an arbitrary prefix of the rows and call it representative.

## Verify the query/result boundary

The semantic validator compares generated expressions/grouping/predicates/parameter positions with the frozen contract, using an AST or deterministic compiler output. Runtime validation checks typed columns, exact aliases, all row values, duplicate grain tuples, time bucket boundaries/order, state consistency, per-axis null validity, cell/row limits and coverage. An all-null measure is a data result when consistent with the population, not automatic permission to change AVG to SUM or remove a date filter. Attribute the error to meaning, capability, SQL, source reality or infrastructure and repair only that layer.

Run the [worked examples](worked-examples.md), then prove the real database dialect/driver and tenant/object policy in the host. The included SQLite execution checks a PostgreSQL-compatible aggregate subset on a synthetic UTC-text fixture; it does not exercise PostgreSQL timezone functions, query planning, permissions or network execution.
