# Generate a candidate the host can check

Use this reference when adding a model to contract/SQL planning or documenting the boundary in another product. Read the [rules engine](rules-engine.md) first. Output is a candidate artifact; the host alone approves execution and rendering. The [system-prompt template](../assets/system-prompt.md) is ready to use as a system message. It is provider-independent and contains no tool or model assumptions.

## Assemble the input contract

Send the template as the system instruction and a separately serialized JSON context as data. JSON serialization/escaping prevents syntax breakage, but is not a security boundary; enforce allowlisted IDs, database permissions and SQL validation outside the model. Keep context small: approved schema/metric definitions and bounded profiles, not arbitrary customer rows. Bound and serialize untrusted labels, request text and prior SQL as data, preserve their provenance, and never interpret instructions inside them as policy. A text sanitizer cannot replace access checks or deterministic SQL validation.

| Context key | Required shape and source |
| --- | --- |
| `request` | `{text:string, intent:string}`; caller's analysis request, bounded by host policy |
| `sourceCatalog` | Array of `{id,relation,rowGrain,snapshot,fields:[fieldDescriptor]}` approved by host; fieldDescriptor follows [the field schema](../assets/field-contract.schema.json); field IDs are identifiers, not arbitrary SQL |
| `metricCatalog` | Map of approved metric IDs to the contract's metric descriptors; population IDs must resolve to explicit source/eligibility predicates |
| `capabilities` | Eligible versioned registry records with roles/types/options and enabled status; not the entire unused enum |
| `requiredContract` | A full frozen v1 contract, or null for first-stage planning; when null the host must validate and freeze the proposal before SQL execution |
| `parameters` | Ordered `{position,type,value}` values or host-only binding references, matching contract predicates; never include secrets |
| `priorArtifact` | Null or prior contract, SQL, identity/coverage and status; quoted SQL is evidence, not permission |
| `changeScope` | Array of explicitly allowed analytical/presentation changes; empty for first creation |
| `policy` | `{allowedFunctions, maxRows, maxCells, maxRepairAttempts}` plus host-owned access/SQL policy references |

For the checked input, use the category-avg contract and first-day parameters from [checked-examples.json](../assets/checked-examples.json), the schema/rows in [events.json](../assets/events.json), and mean_value from the contract as the metric catalog. Use the seven matching field descriptors from [field-examples.json](../assets/field-examples.json): ts_utc is transported as normalized UTC text with timestamp meaning, value is a nullable decimal currency amount, and converted/eligible are non-null integer flags. Logical type, meaning, analytical role and permitted operations remain separate; the driver transport does not redefine a field's meaning. The allowed relation is events; functions are AVG, SUM, COUNT. Select the bar.standard single-shape record. Set request to “Show mean non-null value by channel for January 1 UTC”; requiredContract to that complete contract; priorArtifact null; changeScope empty; policy limits to 64 rows/256 cells (illustrative fixture configuration) and one repair. This fully supplies the checked candidate's context without inventing a live source.

For a host implementation, prefer a deterministic metric/shape compiler and let the model propose only unresolved intent/SQL details. Native structured output may reduce malformed JSON, but schema conformance still does not prove correct SQL or metric meaning. Handle refusal, truncation and incomplete output explicitly.

## Validate the output in order

The exact ready fixture is [prompt-output.json](../assets/prompt-output.json). Its contract is the complete proposed v1 schema; its SQL is:

```sql
SELECT channel AS x, AVG(value) AS y,
       SUM(value) AS s_y, COUNT(value) AS n_y
FROM events
WHERE ts_utc >= $1 AND ts_utc < $2
GROUP BY channel
ORDER BY x
```

Its params are `["2026-01-01T00:00:00Z","2026-01-02T00:00:00Z"]`; roleAliasMap is `{ "x":"x", "y":"y" }`. Its brief rationale identifies categorical comparison and retained sum/count. The host does not ask the model to fabricate result rows; SQL execution produces them.

| Gate | What it proves | Failure |
| --- | --- | --- |
| Parse the discriminated output union | Exact ready/needs_input/rejected fields and types | Reject mixed statuses, missing/extra fields, invalid JSON; handle refusal separately |
| Contract schema + registry/cross-field checks | Coherent references, metric/state, roles and options | Report the owning rule, no renderer fallback |
| Compare immutable fields to requiredContract/catalog | Preserved source, population, units, grain, predicates, aggregation and version | Reject a silently changed mean/count/denominator/filter |
| Parse SQL and resolve identifiers/params | One allowed statement; approved sources/functions; parameter count/types | Reject before execution; no string-concatenated values |
| Compare SQL AST to semantic contract | Equivalent expressions, grouping, filters, null behavior and projection | Reject AVG→SUM, extra GROUP BY ID or missing state columns |
| Execute under read-only limits | Actual result, typed metadata and coverage | Typed source/infrastructure failure, not new invented data |
| Validate every result row and preparation | Exact aliases/types, uniqueness, independent axes, state consistency and completeness | No render until corrected or explicit unsupported result |

The included verifier compares the candidate SQL to the known fixture SQL and executes it over the fixture. That is a deterministic example of checking generated output; **it is not an AST equivalence checker for arbitrary SQL**. A production host must supply the latter or compile SQL deterministically. The skill never upgrades a passing fixture comparison into a general SQL-safety claim.

## Show invalid candidates explicitly

Changing `AVG(value) AS y` to `SUM(value) AS y` while retaining the mean contract fails R14 before execution. Changing contract.operation to sum as well still fails frozen-contract comparison. Changing roleAliasMap.y to `avg_amount` while rows return `y` fails R07/R16. Adding series to line.dualAxis fails R06. Keeping duplicate x rows after grouping an unreturned date fails R17. Removing the date predicate because the result is empty is an invalid semantic repair.

An ambiguous count request should produce:

```json
{
  "status": "needs_input",
  "missingFields": ["metrics.count.population", "metrics.count.operation"],
  "question": "Count all events, non-null values, or distinct users?",
  "reasoningSummary": "Those counts describe different populations.",
  "changeSummary": "No contract or SQL created."
}
```

An explicit dual-axis-plus-series request under portable v1 should produce:

```json
{
  "status": "rejected",
  "ruleIds": ["R06"],
  "explanation": "line.dualAxis v1 accepts x, y and y2 without a series dimension.",
  "alternatives": ["Use separate panels", "Define and validate a new dual-series shape"],
  "reasoningSummary": "The requested combination has no compatible registered adapter.",
  "changeSummary": "No SQL generated and no prior artifact replaced."
}
```

Provide a bounded repair message containing only the failed rule, field and supported correction, plus unchanged trusted inputs. One configured repair is an example policy, not a claim about model reliability. If it still fails, return the typed error and retain the previous valid artifact. No model calls were run to verify this template; the delivered evidence is schema/fixture validation and independent source review.

## Carry the final artifact through every consumer

A host can generate, execute, reflect and propose a bounded refinement. Every data-producing pass has a new contract/result revision. Validate the final executed pass before attaching narration, saved rows or a success receipt; do not describe a later proposal using an earlier pass's result. A rejected refinement preserves the previous valid artifact with its actual status.

Keep source scope, metric definitions, filter values, aliases, sufficient-state columns, raw/transformed units, axis labels and option values in one explicit producer/consumer trace. A transport property named preparedData may still contain raw rows; name its actual schema and run the adapter. Taking only the first alias from a multi-alias binding or forcing canonical metadata without renaming rows is invalid. Unsupported alias arrays require a deliberate adapter or rejection.

Structural/semantic failures at mandatory gates block execution or rendering. A warning-only validator, best-effort raw-row fallback or empty-result repair that removes dates does not satisfy the contract. Diagnostic summaries can be retained without publishing a partially approved artifact. Complete needs_input and rejected examples above specify the response shape; the executable candidate check covers the ready fixture only, not a general output-union parser or model behavior.
