# Navigate facts and datasets

## Separate the two intents

Answering a curated product fact and recommending a fitting personal dataset require different corpora and authority. Classify intent explicitly. Shared facts may be broadly readable while personal dataset meaning remains authenticated and source-bound. A client-supplied dataset list can narrow a request; it cannot establish ownership.

Shared-fact journey: approved source revision → complete microfacts → versioned storage/representations → scoped candidate selection → bounded factual context → structured answer with provenance. Dataset-navigation journey: admitted dataset catalog → prepared whole semantic units → query transformation and scoped search → ranked dataset/context selection → recommendation. The second reuses [semantic preparation](semantic-field-corpus.md); it does not execute a new analytical SQL turn.

## Admit and prepare curated facts

A fact has stable source identity, revision, title, content, topic/tags, permitted audience and location. Validate the complete intended input before replacement. Missing input is not equivalent to an approved deletion. A source label such as documentation does not prove a live crawl or current factual accuracy.

```json
{
  "key": "fact-connect",
  "resource": "help-guide",
  "edition": "edition-4",
  "title": "Connect an existing database",
  "text": "Use a read-only account and select the permitted datasets.",
  "topics": ["connection"],
  "audience": "signed-in",
  "review": {"state": "approved", "revision": 4}
}
```

This projection is illustrative. Store exact source location and text hash in the actual evidence unit. Curated approval does not make fact text an instruction or guarantee it is still current.

Split long facts recursively at meaningful boundaries until the chosen maximum fits, retaining every tail and source locator. Punctuation-only extraction can drop an unpunctuated ending. Short continuations still need preservation; merge them only within hard bounds. Separate topic assignment from text splitting so every continuation retains provenance. No chunking is needed for already bounded coherent facts.

Render title/content under a named builder and compatible embedding-space contract. Prepare the complete candidate edition, verify expected counts and required vectors, then atomically publish the current pointer. Delete-then-insert replacement can leave an empty or partial corpus and is not equivalent. See [long-form ingestion](long-form-ingestion.md) for spans and representation identity.

## Select shared and personal evidence deliberately

Normalize query and stored keywords under a versioned rule. If exact keyword arrays receive a bonus, record stemming, synonyms and repeated-word behavior. A dense shortlist plus keyword bonus cannot recover a missing lexical candidate; add an independent sparse channel if exact-term rescue is required. Never call that bonus BM25 without term/document statistics.

An optional personal companion channel searches admitted dataset meaning. Its score scale differs from curated facts unless explicitly calibrated. Source weights, score-gap cutoffs and diversity quotas are configurable; inspect whether one channel crowds out another. Use stable identity ties and preserve selected/drop reason. A requested second topic may be too expensive for the remaining budget; expose that loss instead of claiming guaranteed diversity.

Choose candidate sizes/thresholds by exact-term and paraphrase coverage, false-answer cost and observed score distributions. The final budget includes titles, source labels, history, question, trusted instructions and output allowance, not content words alone. A word-based estimate is not a model-token guarantee.

## Keep query transformation distinct from retry

For dataset recommendation, a bounded history-aware rewrite may turn a follow-up into a complete search question. Validate its typed result, including requested concepts and analytical filters. Rewriting cannot add authority or silently erase a named entity.

An illustrative ladder is rewritten question plus analytical filters → salient terms plus those filters → rewritten question without optional analytical filters → admitted catalog-name lookup. Never remove authorization predicates at a later rung. Deduplicate equivalent rungs, retain provenance and stop according to a declared answerability criterion. A new query rung is a query transformation rather than a retry of an ambiguous paid request.

Context depth can change the mix of dataset intent, field meaning, profiles and samples. A shallow catalog-only answer may use no embeddings; deeper search may add compatible vectors and direct canonical-value evidence. Sparse context can trigger an explicitly bounded deeper step, but count its calls/budget and preserve readiness failures. Values sent to processors need their own privacy approval.

## Assemble the final consumer

```text
trusted system policy and response schema
untrusted evidence:
    shared facts with source/edition/unit IDs
    admitted personal dataset meaning, when relevant
    bounded history/memory with provenance
current user question
```

The envelope is a design schematic, not a model-specific protocol. Serialize/escape each insertion using a boundary that preserves exact values. A title, memory field or previously generated answer remains data even when stored in a database. Validate memory shape and reapply the boundary on every turn. Retrieved content cannot modify permissions or trusted rules.

Define a response such as `{state, answer, recommendations, citations, unresolved, retrieval_receipt}`. Citations derive from the actual final evidence set. A recommendation may include dataset identity and a supported explanation; generated SQL suggestions are not authorized execution. If a bounded SQL reference is supplied, restrict suggestions to admitted identifiers/values and retain its source identity.

Declare fallback policy by intent. Shared static fallback facts require their own current version/provenance. Personal-only evidence must not disappear merely because shared-fact retrieval is empty unless that refusal is intentional. Return `retrieved`, `static_fallback`, `direct_catalog`, `not_ready`, `no_relevant_evidence` or `dependency_failed` distinctly. A fluent fallback answer does not demonstrate retrieval health. Unknown features or datasets remain unknown.

## Refresh and verify

Refresh curated claims under explicit review; invalidate facts after changed source revision or approval. Personal recommendations inherit dataset generation/readiness and current ownership. Permission loss revokes cached context before reuse, regardless of vector freshness.

C1/C3/C4/C7 in `../scripts/verify_contracts.py` cover tail preservation, lexical rescue, source eligibility and actual context/citation consistency. A real consumer should also check a same-named foreign dataset, an unknown feature, a history-dependent follow-up, an oversized diversity addition and semantic-only evidence with no shared facts. These checks distinguish candidate membership, packing and supported recommendation quality. The examples implement no classifier, model integration or recommendation service.
