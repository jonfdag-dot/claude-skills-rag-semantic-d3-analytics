# Resolve entities from source evidence

## Contract and journey

Convert user phrases into canonical source values, effective fields and an analytical filter contract. Inputs are an admitted resource/dataset/edition, prepared profiles/meaning/value samples, typed question intent and optional frozen prior choices. Output is resolved, ambiguous or unresolved status for every required token, with provenance and any source-probe receipt. Plausible synonyms are insufficient.

Admission → reuse prepared semantic/value units → deterministic field hints → lexical candidates → optional per-token dense fallback → bounded candidate union → constrained selection/ambiguity → bounded source probes → final entity/filter contract. No new document extraction, windowing or corpus writes are used here. Preparation is described in [semantic field corpus](semantic-field-corpus.md).

## Preserve identity and role

Candidates bind resource, edition, full field key, typed canonical value, source unit and match path. Same-named fields in two datasets are different. Column/role hints may use exact identity, synonyms and declared analytical roles; numeric proximity cannot override a metric contract. Cadence, currency and origin descriptors can be filters or dimensions without becoming the series axis.

```json
{
  "token": "ARS",
  "status": "ambiguous",
  "field": "reports.title",
  "candidates": [
    {"key": "title-a", "value": "Annual Revenue Statement", "confidence": 0.86},
    {"key": "title-b", "value": "Annual Review Schedule", "confidence": 0.84}
  ],
  "resource": "reports",
  "edition": "edition-1",
  "match_paths": ["acronym"]
}
```

The confidence values are illustrative, uncalibrated model or heuristic outputs. A small lead is not a reliable unique choice. Preserve enough alternatives to clarify rather than guessing.

## Build deterministic candidates first

Normalize comparison text under a versioned policy while retaining exact canonical values for output. Search exact equality, whole-word/substring and acronym forms deliberately. A pure-letter acronym matcher may accept case variation and reject punctuation; disclose those rules. Reverse substring matches are especially weak and should not silently outrank exact evidence.

A frequency prior may help ranking, but common names can be ambiguous. One possible prior is `log(1 + frequency) / log(1 + maximum_frequency)` when the denominator is positive; missing frequency remains unknown or a documented neutral prior. Match weights and prior influence are configurable policies. Keep bounded alternatives instead of turning popularity into identity truth.

Strip generic nouns only when intent shows they are not literal entities. If all tokens disappear, preserve an unresolved intent rather than selecting arbitrary data. Entity-free ranking strategies may obtain values through source ranking, but a user naming a required entity cannot silently fall back to a broad unrelated aggregate.

## Add compatible dense evidence without losing domains

Embed distinct entity tokens separately when one query names multiple domains. A single averaged question vector may suppress one requested entity. Dense retrieval uses the prepared corpus's compatible space and exact field/edition/scope. A model/dimension match alone does not establish bare-value versus contextual-anchor compatibility.

Specify whether literal and dense lists are independently retrieved, their bounds and stable union order. Literal-first truncation can discard a correct later dense hit. Record cap/drop reasons and test a candidate just beyond the cap. An alternate-field fallback must return the effective field used; otherwise correct value selection can still generate the wrong SQL predicate.

Distinguish allowed fallback after an unavailable dense channel from full retrieval success. Wrong field, intentional sample exclusion, threshold loss, stale edition, transport failure and missing vectors are separate causes of zero candidates.

## Validate selection and ambiguity

A constrained resolver sees only bounded candidates and the original tokens as data. Validate output shape, every original token's status and candidate membership deterministically. Nonmember values are invalid even if assigned high confidence. Exact canonical spelling must survive serialization; display escaping that changes a value is unsuitable for later equality binding.

Choose an acceptance threshold and ambiguity margin for the workload's error cost and observed candidate distributions. Require a unique sufficiently supported candidate; weak or close alternatives yield unresolved/ambiguous and clarification. Exact top-score ties remain ambiguous even when the configured margin is zero; a stable key orders alternatives without making either uniquely supported. These thresholds are not probabilities until separately calibrated. A dropped token needs an explicit unresolved result, not an invented completion.

For updates, frozen prior entity/value/field bindings persist unless the user's request explicitly changes them. Retry hints cannot broaden required entities or source scope. Keep optional failed choices from leaking into the final contract after a soft failure.

## Probe source facts safely

Candidates guide source probes; similarity does not prove a row exists or that the final analytical query is correct. Use server-admitted source access, parameter-bound values, read-only validation, correct query wrapping and bounded execution. Choose limits/time budgets under source policy without treating a retrieval recipe as permission to execute.

Probe receipts may establish existence, actual distributions, distinct counts, extrema or top-k. A collapse guard for a requested top-k must establish that the restricting predicate is actually the series filter, cardinality evidence is present and frozen entities are absent. The specific analytical strategy defines whether failure requires clarification, refusal or an explicit optional-entity removal.

The final contract carries original token, status, canonical value, effective field, comparison operator, source/edition, match path, confidence/ambiguity evidence and probe identity. Co-occurrence time/metric ranges remain evidence unless an independently justified analytical predicate is requested. User filters never grant authority.

## Check the failure boundaries

C6 in `../scripts/verify_contracts.py` exercises unique, ambiguous, weak, foreign-field, invented-candidate and frozen-update results. C4 checks admission/readiness. Further reconstruction checks should cover mixed-domain requests, alternate fields, cadence without accidental dates, generic nouns, exact acronym behavior, required lookup failure and candidate cap loss. Keep candidate recall, resolver choice and final filter/SQL correctness as separate assessments; the fixture script performs no model or SQL execution.
