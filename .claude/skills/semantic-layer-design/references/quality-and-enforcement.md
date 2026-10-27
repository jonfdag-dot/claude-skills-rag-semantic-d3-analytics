# Verify structure and consumer outcomes with explicit evidence

Read this when selecting checks for a semantic design or reviewing a produced artifact. Start from the named consumer/failure/receipt in [the framework](00-consumers-and-evidence.md), then check the affected contract. A prose instruction guides behavior; structural enforcement belongs in deterministic validators, storage, authorization and execution boundaries.

## Enforce the query and storage boundaries

Generate against an admitted typed query contract. Keep one canonical base-query composer with parameter preservation, immutable input hashes and SQL-aware handling of delimiters/comments/nested CTEs/reserved aliases. Independent read-only defenses can include a real parser/allowed-operation check, a separate forbidden-side-effect check and a runtime restricted role/statement deadline/row-cell guard. Maintain shared declared invariants and adversarial examples so defenses do not drift, while avoiding one shared parser becoming every layer's only defense.

Allow legitimate read-only set operations. Reject writes, side-effect functions, multiple statements, unauthorized relations/fields and predicate loss. Do not describe “starts with SELECT” as sufficient validation. Runtime budget measures and units must be explicit; a returned-row limit does not bound aggregate input work. Any accepted top-k/time/grain reduction preserves user meaning or is disclosed and recorded; never silently narrow dates to make a query fit.

Use storage constraints for finite lifecycle states, scoped uniqueness, referenced keys and paired hash/content/byte invariants where required. Conditional uniqueness and atomic compare-and-swap publication prevent duplicate current artifacts. Enforce tenancy at the data boundary from the creation of the surface; application-only filters are insufficient. Claim/start/heartbeat/complete transitions must actually compare the attempt fence on the server. Credential references, host admission, sensitive-data suppression, bound query values and escaped untrusted prompt data remain independent controls.

The workbook's in-memory SQLite authorizer demonstrates blocked mutation and parameterized reads on synthetic data. It is not a general SQL validator, production credential policy or cross-backend security implementation.

## Define five quality dimensions

| Dimension | Useful definition/denominator | Failure example |
| --- | --- | --- |
| Coverage | Required field/artifact IDs observed and valid divided by explicitly expected applicable IDs | Old generation has the label, new payload missing |
| Grounding/provenance | Claims with admissible evidence and valid references; unknown/inferred explicitly separated | Currency assigned from name alone |
| Discriminability | Confusable sibling descriptors distinguished on their intended requests | Site label and site code share aliases without use/anti-trigger rules |
| Structural compliance | Shared schema/enums/types/limits and artifact/reference integrity | Wrapped scalar enters string-only consumer; array parsed as object |
| Consumer usability | The named consumer can perform the supported task with the provided contract | Rows lack sum/count needed to merge means |

Select thresholds according to workload and risk. Protected correctness invariants such as authorized scope, valid field references, metric algebra and required readiness are explicit pass/fail requirements. Ranking overlap, sample size, context budgets and calibrated statistical quality need selection rationale and relevant evidence; no universal confidence formula or numeric floor applies to every system.

When a scorer disagrees with known valid behavior, investigate its formula, denominator and ordering. Do not lower an acceptance condition merely to hide a failure, and do not declare every inherited threshold sacred without evidence. Empty expectations cannot yield a meaningful PASS. Duplicate facets from one raw response are not independent evidence sources.

## Make failures reconstructable

Record selected input identities, expected/actual output, effective reviewed revision, validation error and resulting disposition. Separate raw output, parsed candidate and merged effective state. A deterministic reuse receipt differs from failed model output. A required missing receipt is unavailable evidence, never assumed success. Avoid retaining secret or unnecessary sensitive text in logs.

Representative counterexamples belong beside their affected contract: numeric ID versus measure; category as dimension/filter; temporal role versus bucket; all-null versus missing; mean-of-means; distinct-count overlap; fanout; mixed units; stale generation; scalar/array/edit projection; incompatible spaces of equal dimension; unresolved entity; authorization intersection; partial job and missing serving bridge. The supplied verifier checks controlled examples for these seams with fixed inputs. Broader model or product evaluation requires its own explicit scope, authorization and finite budget; ordinary package checks do not imply it.

Publication requires actual results for every required check, not headings, file counts or a scanner pass alone. Design review, source-to-public preservation, package closure, controlled examples and independent reconstruction each answer a different question. Passing these examples does not demonstrate production behavior, equivalent future model output, privacy anonymization or efficiency gains.
