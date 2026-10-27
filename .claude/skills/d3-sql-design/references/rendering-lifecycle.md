# Render quickly without losing correctness

Use this reference to build the renderer and its owner. Inputs are a validated prepared view, viewport, theme and presentation state. Output is marks/interactions for the current revision plus a complete update/destroy interface. The recipes are proposed reconstruction guidance; no measured rendering-speed or leak-freedom claim is made here.

## Construct scales and marks from meaning

Use a band scale for categorical x, an inner band for grouped series, and an explicit temporal scale for time. A UTC scale makes instant positioning independent of browser locale; use business-zone labels when SQL buckets use a named local zone. Values keep their declared units. y and y2 need separate domains, formatters and axis labels, with clearly distinguishable mark styles. Dual axes invite misleading visual correlations, so preserve the units and provide separate panels when comparison would otherwise obscure them.

Bars ordinarily use a zero baseline, with sign-aware geometry for negative values. Line domains need not start at zero, but their extent must be disclosed and consistent with the intended comparison. Empty and constant domains need explicit layout behavior, not fake observations. An outlier is not silently clipped. Logarithmic, diverging, percentage and indexed modes require the corresponding metric/eligibility rules before rendering.

Group line records by stable series, sort by time within each group, and retain explicit missing entries. Use independent `.defined` predicates for y and y2; removing missing points first creates false continuity. Choose linear or monotone interpolation deliberately; interpolation is drawing between observations, not an additional measured value. Stacks produce baseline/topline geometry from compatible long rows; compute the scale domain from those coordinates, including negative stacks when supported. The source SQL remains unchanged by a purely geometric stack.

Join by semantic identity. A compact categorical example after validation is:

```js
const visible = prepared.records.filter(d => d.yValue !== null);
plot.selectAll("rect.mark")
  .data(visible, d => d.key)
  .join("rect")
  .attr("class", "mark")
  .attr("x", d => x(d.xValue))
  .attr("width", x.bandwidth())
  .attr("y", d => y(Math.max(0, d.yValue)))
  .attr("height", d => Math.abs(y(d.yValue) - y(0)));
```

Here x/y scales and the zero-inclusive domain are already built; no aggregation occurs in the join. [D3's keyed join contract](https://d3js.org/d3-selection/joining) explains identity and ordering, including duplicate-key enter/exit behavior. Unique keys are a correctness prerequisite, not proof of faster rendering on every workload.

## Give instances and redraws separate owners

| Owner | Resources and lifetime |
| --- | --- |
| Host instance | Current contract/result revision, filter service, persisted view spec, one subscription, render generation token |
| Redraw/layout | SVG subtree, controls, tooltip/portal nodes, local listeners, geometry, layout observer and pending RAF |
| Async work | Query/load/font promises, abort controller where supported, delayed autoplay and transitions, obsolete-result guard |
| Final destroy | Dispose every resource above owned by this instance; leave shared loaders/caches and other charts intact |

An update may retain the host's filter selection and subscription while replacing geometry. Full destroy must unsubscribe **all** owned filters, destroy **all** owned portals and unbind **all** owned events, also on empty/error paths. If the filter service is instance-owned, destroy it too. Never preserve an evaluation-local unsubscribe handle across a redraw that creates a new closure. Never clean another chart's portals using a global selector.

Register disposal immediately when creating each resource. One small disposal mechanism is:

```js
function createScope() {
  const disposers = [];
  let disposed = false;
  return {
    own(dispose) {
      if (disposed) throw new Error("SCOPE_DISPOSED");
      disposers.push(dispose);
    },
    destroy() {
      if (disposed) return;
      disposed = true;
      const failures = [];
      for (const dispose of disposers.splice(0).reverse()) {
        try { dispose(); } catch (error) { failures.push(error); }
      }
      if (failures.length) throw new AggregateError(failures, "CHART_CLEANUP_FAILED");
    }
  };
}
```

This shows ownership, idempotence and attempting all disposers without hiding failures. It is not a complete renderer. The host reports cleanup errors and still removes stale revision ownership. Register subscription unsubscribe, observer disconnect, event removals, portal destroy, timer/RAF cancellation and transition interruption separately. Setup failure must destroy its partially created scope and preserve both setup and cleanup errors if both fail.

Interrupt named transitions on the root and descendants; interrupting only the root or unnamed transition leaves other work active. A cancelled transition's completion promise rejects, so identify expected cancellation without swallowing unrelated failures. [D3 transition control](https://d3js.org/d3-transition/control-flow) defines those semantics. Track autoplay timeouts before scheduling them. A delayed callback must check the current generation and disposed flag before touching DOM.

In React, keep a stable DOM owner ref, explicit dependencies and symmetrical setup/cleanup; do not let React and D3 both own the same mark subtree. Guard obsolete asynchronous work even if it cannot be aborted. Strict Mode's development setup/cleanup cycle is a useful test of ownership, not a reason to disable cleanup. [React 18 effect lifecycle](https://18.react.dev/reference/react/useEffect) supplies the host lifecycle contract.

## Keep interaction semantics visible

Hover, legend emphasis and zoom ordinarily affect presentation. Source filtering or analytical-range selection follows the [view-change classifier](view-changes.md). Show raw and transformed units consistently in axes, legends, tooltips and summaries. Use stable IDs for joins and filters, human labels for text, and text insertion for untrusted labels. Provide keyboard-accessible equivalents for values/actions, an accessible title/description and a table or summary when visual marks alone cannot communicate the result. Respect reduced-motion preferences for transitions and race playback.

For a race adapter, declare frame time separate from category, ranking scope/ties, whether missing entities mean zero or unknown, and whether interpolation is permitted. Playback/scrub/filter/update must rebuild from the same analytical scope. Cancel both the playback controller and delayed start, preserve user-selected frame only if still valid, and expose a static frame/table. An animation branch existing in source does not establish these guarantees.

## Use measured optimizations

Prepare/parse once per result revision; reuse keyed maps for repeated stack/cell lookups. Separate data work from layout work so resize only changes scales/geometry. Batch DOM measurement before writes, coalesce layout using RAF, and bound labels/hover search. Reuse template/loading promises and immutable prepared structures when their dependencies truly match. Binary search requires sorted per-series time; nearest-point and interpolation policies are distinct.

These mechanisms are useful candidates, not established speedups. A cache keyed only by source-array identity can go stale after in-place mutation; use immutable results plus revisions and include filter/adapter dependencies. Repeated cell scans, global sampling and redundant layout work remain hypotheses until measured. Choose resize debounce from the interaction budget rather than copying a fixed delay. A duration ending after template invocation does not measure completed transitions or interactive frame rate. No “60 fps,” maximum-series threshold or universal SVG/Canvas crossover is established by this research.

To verify performance, choose representative bounded workloads and record environment, rows, series, categories, missingness and update type. Measure query separately from parse/preparation, scales/geometry, first paint and transition completion. Exercise mount, data refresh, filter, sort, resize and destroy repeatedly. Inspect frame timing and heap/resource counts using the host's existing tooling; compare correctness before interpreting speed. Do not add telemetry or a benchmark service merely to apply this guide. Adopt sampling, Canvas or workers only after a measured bottleneck and a separate design decision.

## Verify reliability in the browser

Test two charts simultaneously, repeated redraws, family changes, same-length changed data, empty→nonempty, primary-null/secondary-valid data, rapid updates, resize during load, failed preparation, delayed autoplay and unmount. Confirm one live subscription per instance, no owned portals/listeners/observers/timers after destroy, no late DOM writes, and preserved filter state only where promised. Check values and labels against the fixture oracle. Static source probes and a passing build cannot establish these runtime properties.
