# Check the contract against real arithmetic

Use these examples to implement or test the portable design. [events.json](../assets/events.json) contains eight synthetic events; [checked-examples.json](../assets/checked-examples.json) contains nine full contracts, SQL strings, bound parameters, exact alias maps, expected rows and chart behavior. They are instructional artifacts, not captured customer data or actual model outputs. [chart-contract.schema.json](../assets/chart-contract.schema.json) defines their proposed v1 structure.

The fixture uses text timestamps normalized to UTC, so lexical range predicates and `substr` daily keys are valid for this dataset. SQL is a PostgreSQL-compatible aggregate subset executed by the verifier on in-memory SQLite. PostgreSQL timezone/driver/execution behavior and browser rendering are separate checks; no local database service is started.

| Day | Channel | Values | Event users | Converted / eligible |
| --- | --- | --- | --- | --- |
| Jan 1 | A | 10, 20, null | u1,u2,u3 | 1 / 3 |
| Jan 1 | B | 90 | u2 | 1 / 1 |
| Jan 2 | A | 30 | u1 | 1 / 1 |
| Jan 2 | B | 50,70 | u3,u4 | 1 / 2 |
| Jan 3 | A | null | u5 | 0 / 0 |

## Category average with sufficient state

`category-avg` uses bar.standard/single, roles x=channel→x and y=mean_value→y, grain `["x"]`, unit USD, first-day half-open range, AVG(value), null inputs ignored, state `{sum:s_y,count:n_y}`. The complete contract is linked above; this is its readable summary.

```sql
SELECT channel AS x, AVG(value) AS y,
       SUM(value) AS s_y, COUNT(value) AS n_y
FROM events
WHERE ts_utc >= $1 AND ts_utc < $2
GROUP BY channel
ORDER BY x
```

Bind `$1="2026-01-01T00:00:00Z"`, `$2="2026-01-02T00:00:00Z"`. Returned records:

```json
[
  {"x":"A","y":15,"s_y":30,"n_y":2},
  {"x":"B","y":90,"s_y":90,"n_y":1}
]
```

Aliases are `{x:"x",y:"y"}`; a legacy key config is `{xKey:"x",yKey:"y"}`. Prepared records retain A/B as categories and 15/90 as values. Expected graph: two bars at those heights, mean-value USD label; neither state column becomes a series. Combining channels gives `(30+90)/(2+1)=40`, not `(15+90)/2=52.5`, nor 105 from summing means. A separate verifier case checks the requested 100/10 and 90/1 example: `190/11`, not 50. Retaining only y values is insufficient to recover the combined mean.

## Time series with a category series

`daily-channel-sum` uses line.multi/long, x=UTC day, series=channel, y=SUM(value), grain `["x","series"]`, and sum/count state. Its SQL is:

```sql
SELECT substr(ts_utc,1,10) || 'T00:00:00Z' AS x,
       channel AS series, SUM(value) AS y, COUNT(value) AS n_y
FROM events
WHERE ts_utc >= $1 AND ts_utc < $2
GROUP BY 1, channel
ORDER BY x, series
```

Range ends January 4. Rows are Jan1/A=30, Jan1/B=90, Jan2/A=30, Jan2/B=120, Jan3/A=null; n_y is 2,1,1,2,0 respectively. The file contains the exact JSON rows. Aliases `{x:"x",series:"series",y:"y"}` map to xKey=x, timeKey=x, seriesKey=series, yKey=y. Expected graph: chronological A and B lines with fixed colors. Jan3/A is a missing measurement, not zero. Jan3/B has no row; only a declared daily grid permits creating a null gap for it.

Hide B as a visual action without changing A's values. A monthly SUM can merge complete daily state to 60, B to 210. Recovering hourly values or filtering by an omitted user_id requires a new query. A value-axis tick change needs no regrouping.

## Daily dual axes

`daily-dual` uses line.dualAxis/dual, grain `["x"]`, no series. y is total USD; y2 is conversion percent with ordered inputs converted/eligible and separate numerator/denominator state.

```sql
SELECT substr(ts_utc,1,10) || 'T00:00:00Z' AS x,
       SUM(value) AS y, COUNT(value) AS n_y,
       100.0 * SUM(converted) / NULLIF(SUM(eligible),0) AS y2,
       SUM(converted) AS num_y2, SUM(eligible) AS den_y2
FROM events
WHERE ts_utc >= $1 AND ts_utc < $2
GROUP BY 1
ORDER BY x
```

```json
[
  {"x":"2026-01-01T00:00:00Z","y":120,"n_y":3,"y2":50,"num_y2":2,"den_y2":4},
  {"x":"2026-01-02T00:00:00Z","y":150,"n_y":3,"y2":66.66666666666667,"num_y2":2,"den_y2":3},
  {"x":"2026-01-03T00:00:00Z","y":null,"n_y":0,"y2":null,"num_y2":0,"den_y2":0}
]
```

Mapping is `{x:"x",y:"y",y2:"y2"}`; legacy keys use timeKey=x and yKey2=y2, with no seriesKey. Draw separate USD and percent scales and independent gaps. Merging all days yields y=270 and y2=`100×4/7≈57.142857`; averaging the two finite daily percentages gives ≈58.333333 and is wrong for this population. A separate keyed-alignment check retains `{x:t,y:null,y2:4}`; do not drop the entire row or align arrays by index.

## Counts and extrema are distinct metrics

Five category cases use the same first-day predicates/grain/aliases as category-avg and replace the y expression with `MIN(value)`, `MAX(value)`, `COUNT(*)`, `COUNT(value)` or `COUNT(DISTINCT user_id)`. Their complete contracts/SQL/results are in the fixture file.

| Operator | A | B | Whole first day | Valid merge |
| --- | --- | --- | --- | --- |
| MIN(value) | 10 | 90 | 10 | min of valid minima |
| MAX(value) | 20 | 90 | 90 | max of valid maxima |
| COUNT(*) | 3 | 1 | 4 | sum disjoint event counts |
| COUNT(value) | 2 | 1 | 3 | sum disjoint non-null counts |
| COUNT DISTINCT(user_id) | 3 | 1 | 3 | union identities or requery; scalar sum 4 is invalid |

There are two drawn bars in every case. That does not make the event count 2. For raw values `[10,20,null]`, count rows=3, count non-null=2, mean=15, min=10, max=20. The all-null Jan3 group has count rows=1, count value=0 and null AVG/MIN/MAX/SUM. An empty global aggregate yields counts 0 and null aggregates; an empty grouped query yields no rows. The verifier executes these distinctions rather than asserting them from the labels.

## Keep category and frame time separate

`category-time` uses bar.race/category-time with x=channel, time=UTC day, y=SUM(value), grain `["time","x"]` and no series. It projects the same observations as the long example, but as `{x:"A",time:"2026-01-01T00:00:00Z",y:30,n_y:2}` and corresponding rows. SQL groups by channel and daily time, orders time then x, and aliases map `{x:"x",time:"time",y:"y"}`. Use xKey=x, timeKey=time, yKey=y.

The checked result proves the shape. Expected static frame Jan1 has A=30, B=90; Jan2 has A=30, B=120. A separately implemented animation adapter may interpolate under an explicit policy. This package supplies no animation adapter; the fixture proves only its input shape and arithmetic.

## Run the oracle and read its limits

From the installed skill directory:

```sh
python3 -B scripts/verify_examples.py
```

The Python floor and jsonschema dependency are declared in [requirements and runtime setup](extension-and-verification.md#run-package-checks); the verifier fails clearly if jsonschema is unavailable and does not install dependencies. It parses the contract schema, executes all nine SQL examples over the synthetic events, compares every result key/value/order, checks aliases/grain/state and validates the prompt candidate. It also exercises invalid duplicates, invalid role combinations, incomplete results, metric mutation, numeric boundaries, time changes, filters and independent-axis alignment. It prints decisive numerical values and rejection outcomes. These checks establish the example contracts and arithmetic, not arbitrary SQL safety, model compliance, complete rules-engine implementation, browser accessibility, cleanup or performance.
