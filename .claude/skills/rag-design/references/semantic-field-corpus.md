# Represent field meaning as evidence

## Define the searchable units

Make structured data understandable without embedding a whole database as one text document. Keep deterministic profiles, generated/reviewed meaning, dataset-level intent and permitted value samples distinct. Their consumers differ: exact-ID loading, explanation, entity resolution, dataset recommendation and compilation.

The journey is admitted read-only source/dataset → deterministic statistics → validated meaning → eligible value extraction/co-occurrence → versioned whole-unit storage → compatible representations → consumer-specific retrieval → explicit final context. No paragraph windows or overlap are used for profiles/facets; each coherent typed fact is a unit.

## Separate identities and generations

Source access identifies where a server may execute reads. A dataset identifies a reviewed query or declared table/view population. A processing edition identifies one coherent preparation run. A field key identifies dataset plus physical source path, never a display name alone. Keep these typed identities through profiles, meaning, samples and vectors.

A minimal pedagogical store has `Dataset`, `Edition`, `Field`, `Profile`, `Meaning`, `ValueSample` and `InclusionDecision` entities. A dataset has many editions; an edition has fields and their evidence records. Profiles and meaning bind the full field key and edition. Samples bind an included field, canonical typed value, rank/frequency and coverage. The current edition pointer changes only after required records validate. Null/unknown statistics are nullable facts rather than zeroes.

```json
{
  "field": "sales.region",
  "edition": "edition-3",
  "logical_type": "string",
  "meaning": "nominal_category",
  "roles": ["dimension"],
  "operations": {"filter": ["eq", "in"], "group": true, "order": "lexical", "aggregate": []},
  "profile": {"rows": 120, "non_null": 118, "distinct": 4},
  "provenance": {"kind": "observed", "resource": "sales"}
}
```

This example shows independent axes rather than a complete storage insert. A numeric customer code remains an identifier; a currency field needs a metric contract; a date may both group and filter. Temporal meaning must distinguish instant/date/duration and state relevant timezone/calendar/unit. A descriptor such as unit, cadence, source, encoding, currency, status, geography, methodology or classification refines meaning; it does not automatically become a series metric.

## Observe, enrich and protect edits

Compute row/non-null/distinct counts, null fraction, ranges, lengths, key relationships and authorized bounded samples through a read-only adapter. Group related statistics queries where practical, but preserve hard failures rather than replacing missing facts with optimistic defaults. Record the population and whether counts are exact or estimated.

Define null fraction as `(rows - non_null) / rows` when rows is positive, and unknown or an explicitly named empty-population result otherwise. Distinctness ratio uses a declared denominator, commonly non-null rows. Record that denominator; different ratios can change eligibility. Compute ranges with typed source semantics rather than lexical string order. Profile samples and ranges describe their observed population, not every future edition.

Meaning may describe business definition, synonyms, stewardship, privacy, relationships, valid operations, metric/time behavior, quality advice and bounded do/don't guidance. Validate generated structure, confidence/provenance and references to actual fields. Model-produced quality scores are hypotheses, not observed quality. Preserve human-reviewed overrides using explicit precedence and expected edition/revision checks; an older generated result cannot overwrite a newer edit.

A metric contract states population, input/output grain, unit, null handling, permitted aggregation and sufficient state. Nonadditivity does not by itself justify AVG. Means may require sum/count or weighted state; distinct counts cannot generally be summed across overlapping groups. If additivity or population is unknown, carry unknown and require clarification or new source computation.

## Select safe value samples

Value samples are a deliberately bounded evidence corpus, not arbitrary cell export. Choose eligibility from semantic meaning, sensitivity, cardinality, uniqueness, average length, source size and consumer need. Record include/exclude reason and route high-uniqueness identifiers to authorized deterministic lookup when appropriate. Numeric/temporal fields may be useful as companion ranges even when not embedded as categorical values.

Extract non-null canonical values with explicit frequency/order and coverage. A frequency-ranked subset is not an exhaustive universe; derive coverage from verified persisted counts and declared extraction policy. Do not report complete coverage after partial inserts. Store the immutable sample row identity so vector updates cannot touch another field/edition with the same value.

For an already admitted server-resolved relation, an illustrative extraction is `SELECT region, COUNT(*) AS frequency FROM admitted_sales WHERE region IS NOT NULL GROUP BY region ORDER BY frequency DESC, region ASC LIMIT :sample_limit`. Bind values/limits through the adapter and resolve identifiers from the admitted catalog rather than interpolating caller text. Preserve the source collation/equality contract used to canonicalize values. A capture limit smaller than the true distinct count produces partial value coverage even if every returned row persists.

Co-occurrence may attach categorical companions, temporal bounds and metric envelopes to a value. These explain context; they are not automatically valid filters or independent statistical populations. Example: a plan name appears with cadence `monthly` and a timestamp range. That evidence does not authorize adding the timestamp range to every later query.

Authorize processor/classification/residency before values reach embedding or synonym services. Identifier exclusions are not a complete privacy policy. Field names, free text and combinations can also be sensitive. Revoke/delete derived samples, vectors, cached contexts and exports according to the owning policy.

## Render and embed deliberately

Render a stable profile or meaning facet into text from typed data. Include physical identity, observed facts and justified usage; represent unknown explicitly. Keep observed facts and generated interpretation distinguishable. One useful profile text is `Region is a nominal grouping field in the sales dataset; 4 distinct values among 118 non-null rows in this edition.`

Store builder revision and exact text digest. A bare value, a value with its field/business context, and a canonical JSON observation are different preimages. Contextual anchors can reduce value ambiguity but require rebuilding/versioning rather than silently overwriting indistinguishable vectors.

The embedding-space contract binds model/revision, document/query encoder pair and preprocessing, dimensions, metric and normalization. Record pending/failed representations separately from statistical/semantic readiness. Await required vector completion or publish an explicitly partial consumer capability; asynchronous launch is not embedding completeness.

## Retrieve for the actual consumer

Exact-ID consumers load selected-edition records and do not need embeddings. Vector consumers filter current admitted resource/edition/readiness and use compatible query encoding. Choose channel sizes, similarity thresholds and field-role ranking for the consumer's needs rather than applying one global top-k. Keep a consistent current pointer in caches and all reader channels.

Optional general/SQL/business views of a field can be separate representation units, but each needs its own builder identity and an actual vector/reader if advertised. A text builder alone does not create a search system.

Return persisted IDs/counts, exclusion decisions, sample coverage, pending/failed representation counts and readiness. Readers distinguish no rows, pending representations, valid no-match, stale generation and dependency failure. Bind final contexts to selected evidence so explanations cannot silently mix editions.

## Build and check in order

Implement identities/permissions → deterministic statistics → validated meaning/edit precedence → whole-unit renderer → embedding jobs/readiness → sample eligibility/coverage → co-occurrence anchors → coherent publication → consumer-specific retrieval → revocation/deletion. Each step returns an explicit receipt before dependents proceed.

C2/C4/C5 in `../scripts/verify_contracts.py` check representation compatibility, scope/readiness and independent field axes. C6 checks value-resolution constraints. Additional adapter tests should cover same-named fields in two datasets, a numeric ID, a nonadditive rate, cadence/unit descriptors, unknown null counts, sensitive exclusions, partial sample writes and changed builder/model. These are construction requirements, not measured semantic or retrieval quality.
