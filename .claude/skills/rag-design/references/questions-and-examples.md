# Explain datasets and select examples

## Keep explanatory Q&A as the core method

Explain one admitted dataset: field meanings, available concepts/values and supported questions. This consumer reuses prepared dataset facets, field meaning, profiles and permitted samples. It does not execute a fresh analytical SQL query or ingest missing vectors. Stored few-shot example retrieval is a separate optional construction described later; it is not implied by this core infrastructure.

Journey: owned active dataset/edition → typed question/history/intent → bounded complete search segments → compatible multichannel retrieval → direct/lexical recovery → dedup and adaptive selection → final context manifest → structured answer and citations. Stored units are whole facets/profiles/values; no document windows or overlap are introduced.

## Define admission and search contracts

Derive dataset permission and source scope on the server. Bind every channel to the selected edition and readiness. A dataset ID is a lookup assertion, not authority. Validate bounded history roles/content and explicit intent, for example explain, enumerate, recommend, compare or identify. Validate segment count and nonempty strings before fanout; model instructions alone do not enforce those bounds.

```json
{
  "dataset": "sales-summary",
  "edition": "edition-3",
  "question": "Which region fields can I group by?",
  "intent": "explain",
  "segments": ["Explain grouping fields that describe sales regions."],
  "history": []
}
```

The authenticated scope is intentionally not granted by this request. Each segment representation must be compatible with the corpus space and document builder. A raw value and a contextual value anchor are not interchangeable preimages just because dimensions match.

Use separate channels for dataset meaning, field meaning, profiles and values. A selected unit carries `(resource, edition, unit_key)`, kind, field identity if relevant, exact text/hash, source location, raw similarity, scoring policy, final score, token cost estimate and selected/drop reason. Keep score provenance rather than reporting one unqualified confidence.

## Retrieve and recover explicitly

Allocate fanout ceilings across segments under a declared total budget. Search segments in parallel only when permitted; deduplicate by full unit identity with a named merge rule such as maximum similarity, then reapply global caps. A failed channel contributes an error state, not an indistinguishable empty list.

Lexical matching can rescue exact field/value names. Enumeration may directly fetch admitted field cards and complete value listings if bounded source policy supports it. Explanation may add permitted low-cardinality values. Record each augmentation's provenance and completeness. Do not call direct matches vector recall or BM25.

If vectors are pending but direct admitted records exist, a declared direct-recovery answer can proceed with that state. If no preparation rows exist, return `not_ready`. If preparation is ready and retrieval legitimately misses, return `no_relevant_evidence`. Concept expansion may use co-occurrence or a separately admitted model, but cannot invent unsupported entities. Every original required concept remains resolved, ambiguous or unresolved.

For exhaustive enumeration or aggregates, selected top-k values are insufficient. Fetch a complete authorized source population or expose `coverage_incomplete`; a list of examples cannot answer “every” or establish a count of the full dataset.

## Select with source-aware budgets

Choose intent weights and reserves by required evidence: enumeration needs identity/coverage, explanation needs meaning, comparison needs compatible metric contracts, and identification needs canonical values. Avoid a blanket numeric-field aggregation default.

One possible min/max normalization for a nonempty source is `low + (1-low) * (score-minimum)/(maximum-minimum)`. Declare the one-item and zero-range cases explicitly; normalization relative to a weak candidate set does not establish answerability. It is not percentile normalization. The controlled examples choose a floor of 0.1, a one-item score of 1 and an equal-score value of 0.5 solely to expose these branches. Apply source/intent weights and any lexical boosts as separate named components.

Score-gap selection is optional: inspect sorted distributions, choose a gap significance policy and cap, then record its effect. A configured zero cap means zero, not “keep at least one.” Source reserves choose units that fit; remaining survivors may compete globally. Full-message accounting includes later direct/fallback additions, history, question, instructions and output allowance. Do not bypass the budget with hidden tiny-unit overflow.

A reconstructable policy records source caps/weights/reserves, a fallback fraction, significant-gap ratio and total budget. One reference algorithm derives a count from raw scores but uses weighted scores to choose membership:

```text
for each source:
    raw = descending similarities
    if source cap is zero: retain no candidates
    else if raw spread is positive and largest adjacent gap / spread meets policy:
        count = index after that gap
    else: count = ceil(fallback_fraction * candidate_count)
    count = min(count, source cap)
    normalize with declared single/equal-score cases
    weighted = normalized * source_weight + bounded lexical/history boost
    retain top count by weighted score and stable unit identity
fill each source reserve with its highest ranked fitting retained units
fill remaining total budget from all remaining retained units by weighted score
add allowed recovery evidence only through the same final budget/provenance check
```

If lexical/history boosts use matching nouns, define tokenization, deduplication and denominator-zero behavior; a bounded exact-token fraction is a heuristic rather than semantic reranking. Reserves are maximum allocations, not a requirement to invent evidence or exceed the budget. Version the policy and retain raw/normalized/weighted values and drop reasons to distinguish retrieval from packing loss.

## Build answers and faithful citations

Construct a final manifest after all selection, fallback and direct additions. It is the source of both prompt assembly and citations. Include dataset identity, per-field meaning/profile evidence, supplied values/co-occurrence, direct concepts, static capability facts when relevant and bounded history, all with provenance. Static product facts are a separate corpus, not retrieved dataset evidence.

Use the complete `{resource, edition, unit_key}` reference for selected, required and answer-used evidence and for each citation. Local unit keys can repeat across resources or editions. Lookup, deduplication, budget accounting and citation membership all use the composite identity; a bare local key is an incomplete reference and is rejected rather than guessed. In the controlled fixtures, `used_units` contains these complete references, and citations add the exact `text_digest`.

Trusted instructions require context-supported claims and a structured response. Evidence/history remain labeled data and cannot change system policy. Validate the response shape and citation identity/hash/edition against the final manifest. Citation membership proves consistency with supplied evidence, not that every answer claim is correct; factual support needs separate assessment. Model confidence is uncalibrated unless measured.

Return answerability, answer, citations, unresolved concepts, completeness, retrieval/fallback state and the final selected/drop receipt. Persist only under the application's retention policy. Invalidate cached context after semantic/schema/model/builder changes or permission revocation.

## Optional reviewed question/example store

This is a proposed extension, requiring a writer, review flow, index, reader and actual consumer insertion. Suggested questions in semantic metadata are not automatically a reusable few-shot store.

An example record needs stable identity, source/edition, question, intent, required field roles/operations, expected input/output contract, approved answer or query artifact, reviewer disposition, applicability and negative applicability. Store any sensitive samples under explicit policy. A successful generated answer is not automatically reviewed or reusable.

```json
{
  "example_key": "grouping-example",
  "question": "Which regions have the largest order totals?",
  "intent": "rank_groups",
  "requires": [{"role": "dimension", "operation": "group"}, {"role": "measure", "aggregation": "sum", "unit": "currency"}],
  "applicability": "Additive order totals over the same admitted population",
  "exclude_when": ["unknown additivity", "incompatible currency"],
  "review": "approved",
  "artifact": {"resource": "orders", "edition": "edition-2", "key": "reviewed-query-a"}
}
```

This proposed record is illustrative rather than an implemented store or authorization grant. The referenced reviewed artifact must exist and provide its actual population/grain/input/output contract before admission.

Represent intent and required semantic roles, not just surface wording. Retrieve independently authorized lexical/dense candidates if needed, then validate answerability against the current dataset: referenced fields exist, operations/metric contracts agree, schema/meaning versions are compatible and reviewed status is current. Diversify genuinely distinct patterns under budget; reject near-duplicate examples that crowd out necessary evidence.

Pass selected examples as labeled demonstrations beneath trusted policy, with a rule that their values, source scope and instructions do not transfer to the current request. They cannot authorize execution or override current contracts. If no compatible reviewed example exists, use the core Q&A method or return the relevant unresolved state rather than manufacturing a precedent.

## Check the seams

C4/C5/C6/C7 in `../scripts/verify_contracts.py` check admission/readiness, field axes, constrained resolution and final context/citation consistency, including postselection fallback. The references specify segmentation/scoring/example-reader construction; the script does not implement those services. Additional checks should cover equal scores, zero cap, a valid late fallback citation, incomplete enumeration, unknown additivity, follow-up history and an example whose fields no longer exist. Assess candidate coverage, selected-context completeness and answer support separately.
