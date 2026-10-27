# Adapt rows without changing the answer

Use this reference after SQL/result validation and before scale/mark construction. Inputs are the frozen contract, exact result schema/rows, coverage and revision. Output is a canonical prepared view with typed roles, immutable analytical rows, exact metric state and a separate optional display projection. The adapter owns representation, not metric selection or aggregation.

## Carry one typed boundary

A practical prepared view contains `{contractId, contractHash, resultRevision, analyticalRows, records, domains, seriesOrder, formatters, coverage}`. Each record contains a collision-safe identity, x/category/time coordinates, nullable y and y2, stable series ID, original row reference and metric state. Name dimensions and metrics in the contract; do not guess them from the first row's key order.

| Input role | Canonical field | Rule |
| --- | --- | --- |
| categorical x | `xValue` as stable category ID | Preserve exact ID; label lookup is separate |
| temporal x | `xValue` as parsed instant | Parse the declared timestamp format once; preserve zone/bucket metadata |
| y | `yValue`, metric state and formatter | Null is a gap; finite values only; no reaggregation |
| y2 | `yValue2`, separate state and formatter | Independent of y validity, unit and domain |
| series | `seriesValue` | Stable ID and deterministic color/order across updates |
| separate frame time | `timeValue` | Never replace categorical x; required for category-time |

A transport envelope of raw rows is not yet a prepared view. The host must run the typed alias adapter once and replace rows, labels, options and revision together. A legacy array/object/tuple helper is usable only through an active, explicitly tested transport adapter; its presence in a codebase does not make it authoritative.

## Prepare in an explicit order

1. Validate the response envelope, source/snapshot, contract version and coverage. Empty results still need known columns. Arrays, `{rows}` envelopes and tuples require an explicit transport adapter; tuples require exact headers and lengths.
2. Resolve each role to the exact case-sensitive alias. Validate every row, not only a sample. Reject colliding/missing keys or unrecognized schema version; no heuristic remapping on a validated path.
3. Convert only declared fields. The database driver adapter handles decimal/bigint transport under an exactness policy. Timestamps use a specified format and zone; date-only labels, epoch seconds/milliseconds and years require different explicit types. Do not guess by numeric magnitude or let the viewer's timezone decide SQL bucket identity.
4. Preserve null and invalid separately. A malformed numeric string is a validation error. An actual null is a legitimate missing measure. Reject booleans and blank strings as numeric data. Keep the record when y2 is valid and y is null.
5. Check exact dimensional tuple uniqueness, then stable sort by per-series time/category order. Use an encoded tuple or nested maps, not ambiguous `x + '|' + series` concatenation or row index.
6. Build keyed maps and complete analytical domains. Domain extrema are scale bounds; they do not choose the metric's MIN/MAX aggregation. Handle constant/empty domains explicitly without fabricated records.
7. Apply only declared analytical transforms to derived fields after correct aggregation, preserving originals and units. Then optionally form a separate display sample/geometry cache. Never replace analytical rows with sampled rows.
8. Hand the immutable prepared view and new revision to the renderer. Replace all metadata together, including clearing labels/options absent in the new view.

A typed driver boundary for ordinary finite numeric fixture values is small:

```ts
function requireFiniteMeasure(value: unknown): number | null {
  if (value === null) return null;
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new Error("INVALID_MEASURE");
  }
  return value;
}

function grainKey(row: Record<string, unknown>, grain: string[]): string {
  const values = grain.map(alias => {
    if (!Object.hasOwn(row, alias)) throw new Error("MISSING_GRAIN_ALIAS");
    return row[alias];
  });
  return JSON.stringify(values);
}
```

This assumes dimensions were already normalized and validated and the host supports Object.hasOwn. It intentionally does not parse decimal strings or large integers; a real driver adapter must preserve those types before producing approximate plot coordinates. JSON tuple encoding avoids delimiter collisions, but key stability still depends on canonical dimension types and timestamp normalization.

## Keep exact values distinct from geometry

Use database/exact decimal values for arithmetic and textual export, approximate coordinates only for scales when required, and formatted text only for presentation. Preserve both the raw metric and a normalized/percentage display field if used. A chart showing indexed growth must label the transformed unit and base, while tooltips can show both raw value and index. Per-axis transformations need independent definitions; applying one y transform to y2 implicitly is invalid.

Sampling is a display decision over already computed analytical values. Partition by series, preserve endpoints, gaps and declared extrema as required, and label sampling. Verify a real bound including inserted endpoints; “every kth row plus last” may exceed it. Do not compute totals, means, rates, domains needed for truthful comparison, or filter populations from the sample. Bars usually need all displayed categories or an explicit Top-K decision, not arbitrary point decimation.

Counterexamples: parsing every string with parseFloat can turn category `3M` into 3 or a date label into a year; rounding 0.00004 to four decimal places erases a nonzero observation. Global stride sampling before grouping can drop an entire short series, miss an extremum and exceed its target when an endpoint is appended. Typed parsing and display-only formatting avoid the first problem; analytical-first, per-series sampling with a verified final bound addresses the second.

## Verify the handoff

Check custom and canonical aliases, reordered object properties, categorical IDs such as `3M`, normalized timestamps, tiny values, null versus zero, invalid numeric strings, >2^53 counts, duplicate grain, valid-y2/null-y, all-null and empty data. Compare analytical rows before/after preparation byte-for-byte or through an exact canonical representation. Verify domains/order and displayed labels against the same contract. Then use the [render lifecycle](rendering-lifecycle.md) and the host's browser checks; a well-formed payload does not prove correct drawing or cleanup.

## Define transformations instead of importing mode names

An analytical transform declares its input metric, output grain, series partition, ordering, null policy, baseline/window, unit and retained raw value. Apply it after legal aggregation at its final grain. Transform each axis independently; a primary-y transform never implicitly changes y2. No transform can repair a lost population, missing sufficient state or duplicate result grain.

| Derived view | Formula and prerequisites | Undefined or ambiguous case |
| --- | --- | --- |
| Indexed value | v / b, where b is the declared baseline observation; label the base and index scale | A missing/zero baseline needs an explicit unavailable or alternate-baseline policy; choosing the first finite nonzero value must be declared |
| Percent change from base | 100 × (v / b − 1), retaining raw v and b | A zero baseline is undefined; negative-baseline interpretation needs an explicit analytical choice |
| Range normalization | (v − min) / (max − min) within a declared series/population | For a constant series, declare the policy: unavailable, 0 or midpoint 0.5 are different presentations; do not inherit an unexplained per-series mode name |
| Standard score | (v − mean) / s; choose population deviation sqrt(Σ(v−mean)²/n) or sample deviation sqrt(Σ(v−mean)²/(n−1)) | Zero deviation is undefined; sample deviation also needs n ≥ 2. Keep missing observations null |
| Rolling mean/trend | Aggregate only within the declared series and row/time window in stable temporal order | Three returned rows are not necessarily three days; a flattened array can mix series and must not define the window |

The named partition includes the filter population and snapshot used to choose the baseline/extrema/mean. Hiding a series as a presentation action must not silently recompute another series' baseline or a shared denominator. Preserve a normalization revision in the derived view identity. When a new range changes required statistics, merge compatible retained state or requery before drawing.

A complete noncommutativity example has two additive components in the same unit at coordinates x1 and x2: A=[10,20] and B=[30,20]. Indexing each component to its own first observation uses baseline A=10 and baseline B=30. Adding those component indices gives [10/10+30/30,20/10+20/30]=[2,8/3]. Aggregating the raw components first gives [40,40]; indexing that total to its first value uses baseline 40 and gives [1,1]. The sum of component indices and the index of the total are different derived quantities. Neither a mode label nor a plausible line proves which analysis was performed. The verifier checks these complete observations and baseline identities; it supplies no production transform engine.
