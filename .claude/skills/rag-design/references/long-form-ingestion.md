# Preserve long-form evidence

## Contract and construction boundary

Turn an authorized document into attributable sections and bounded evidence units. The output is a validated corpus edition with exact source locations and representation identities. This method specifies a writer and the contracts an answering reader still needs. A searchable index, query encoder, answer generator and citation renderer must be implemented separately; the fixture script supplies none of those services.

Admission → source extraction → canonical tree → bounded chunks → immutable storage → compatible representations → proposed retrieval reader → proposed answer/citations. Metadata summaries accompany the corpus; they do not replace source text.

## Admit the source and revision

Derive the principal and permitted resource from authenticated policy. Bind any external-provider token to that identity without treating a caller's resource identifier as authorization. Enumerate every selected page of a source listing; a page token is unfinished selection rather than a successful complete import. Record the provider revision, local content digest and processing edition separately.

Select a parser with declared supported formats and version. A document parser does not imply PDF OCR, spreadsheet semantics or archive support. Reject unsupported content or route it to a separately admitted adapter. Validate input options: either consume a requested parser/chunk policy or reject it rather than accepting an inert knob.

## Extract a canonical tree

Represent headings as paths and content as ordered blocks. Preserve paragraphs, tables, lists and unpunctuated tails; tables may need row/column labels repeated in their evidence text. Keep source-native locators alongside offsets in the canonical rendered text. A parser that stores tables but omits them from chunk input has lost evidence before retrieval begins.

An illustrative block is `{key, kind, heading_path, text, source_locator, start, end}`. Offsets are half-open and refer to one explicitly named representation, such as Unicode code points in canonical text; do not mix byte, character and token offsets. Store the renderer revision. Avoid adding a paragraph twice when a heading extractor also returns it as content.

Derived summaries, dates and keywords must record their input coverage. A summary produced from a prefix cannot establish that a later fact is absent. A failed optional summary may remain unavailable while text ingestion continues; the manifest must retain the distinction.

## Select bounded units

Choose unit size from the reader's context budget, answer granularity, tokenizer and source structure. Require positive ordered bounds `minimum <= target <= maximum`, overlap smaller than the maximum, and a hard final maximum after every merge. Token estimates need a named estimator/revision and an explicitly acknowledged fit error; a character limit is not a token guarantee.

```text
for each ordered block group:
    extend toward target while preserving attributable structure
    prefer a sentence or row boundary within permitted bounds
    split an oversized block with stable source offsets
    retain short leading and trailing units
    apply overlap without advancing past uncovered source text
validate coverage and maximum after merges
assign contiguous unit ordinals within the edition
hash exact final UTF-8 text
```

Sentence punctuation is a preference, not a prerequisite for preserving text. Never overwrite several leading short fragments in a single pending slot. Merging may cross a heading only if the resulting unit retains both source ranges and remains interpretable. Overlap duplicates content intentionally; source coverage checks should accept overlap and reject gaps. Tiny documents still yield a unit.

## Store a complete candidate edition

A minimal pedagogical schema has a document resource, edition, blocks and units. The edition belongs to one resource; each unit belongs to one edition and references one or more block ranges. Uniqueness is `(resource, edition, unit_key)`. The resource's current pointer selects one validated edition; it is not overwritten by a provider checksum.

```json
{
  "resource": "manual-a",
  "edition": "edition-2",
  "unit_key": "passage-4",
  "kind": "passage",
  "text": "Renewal notice: 2032-03-04.",
  "location": {"heading_path": ["Terms"], "start": 120, "end": 147},
  "builder": "structured-text-v1",
  "text_digest": "computed SHA-256 of exact UTF-8 text",
  "state": "pending_representation"
}
```

This is an illustrative projection, not a complete insert or an executable digest. A writer's response should expose resource/edition, expected and persisted blocks/units, pending/failed representations, optional-metadata state and publication state. Validate that response at its consumer. A loop returning normally or a processed flag does not prove completeness.

Use idempotent unit identity and a resumable cursor based on acknowledged items. After a smaller retry batch, advance only by the successfully acknowledged subset. Store text even when embedding is unavailable if policy permits, but report `pending_representation`; do not silently skip the text-writing branch because a vector credential is missing. Publish the current pointer with an expected revision only after required counts, hashes and readiness validate.

## Construct representations compatibly

Bind vectors to an embedding-space contract: model/revision, document/query encoders and preprocessing, dimensions, metric and normalization. Bind each unit additionally to its builder revision and exact text digest. Prefix slicing, provider-requested shortening and learned projection are different constructions unless their compatibility is explicitly established. Equal vector length is insufficient.

Cache identity must use the same text-equivalence contract as the embedding request. If the key collapses whitespace while the request embeds original text, distinct preimages can incorrectly share a vector. A safe baseline hashes exact requested text plus the complete representation contract. Section centroids are optional routing hints; averaging vectors does not create a faithful citation unit or prove fine-grained recall.

Track per-item outcome and retain failed or deferred items for resume. Choose batch size from provider limits, input-token distribution and bounded retry behavior; choose concurrency from admitted capacity. No fixed number is universally correct.

## Implement the missing reader explicitly

The proposed search request is `{authenticated_scope, resource_set, selected_editions, question, representation_contract, selection_policy}`. The server derives scope and validates editions, then constructs a compatible query vector and independently authorized lexical/dense candidates if both are needed. Name the fusion function and channel failure policy. See [lexical/hybrid retrieval](lexical-and-hybrid-retrieval.md).

The proposed selected-evidence response carries unit identity, source edition, location, exact text/digest, score provenance and readiness. An answer prompt receives bounded evidence in a labeled data block under trusted instructions. A citation resolves to `{resource, edition, unit_key, source_locator, text_digest}`; rendering uses that edition rather than today's changed document. Validate citation membership against the final actual prompt set, including fallback additions.

Return `not_ready` when required vectors or the reader are absent; `no_relevant_evidence` for a valid miss; `dependency_failed` for provider/index errors; and `coverage_incomplete` when the requested completeness cannot be supplied. Never turn top-k passages into a complete population for counting or aggregation.

## Refresh, revoke and check

Build refreshes as new immutable editions and retain the old pointer until the candidate validates. Revoke serving immediately when permission is lost, then remove source text, summaries, vectors, caches and retained derived copies according to policy. Track deletion receipts; elapsed time is not proof of deletion.

C1 in `../scripts/verify_contracts.py` validates synthetic span coverage, tables, Unicode, tiny text, bound ordering and missing tails. C2 checks compatible representation/custody; C4 checks edition/readiness and scope. These validate supplied records rather than a general parser or tokenizer. A real adapter also needs fixtures for every supported source format, pagination, contradiction refresh, partial write/retry and deletion. Retrieval recall and factual/citation correctness require separate evidence.
