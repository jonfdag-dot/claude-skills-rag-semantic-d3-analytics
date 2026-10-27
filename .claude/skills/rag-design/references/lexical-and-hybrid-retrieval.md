# Build lexical and hybrid selection

## Choose an algorithm deliberately

BM25 is lexical relevance over a declared corpus using term frequency, document frequency and document-length normalization. A substring union, keyword bonus, full-text rank or authorization filter is a different mechanism. Embeddings are not used by BM25. Add a dense channel for a stated semantic/paraphrase need rather than to satisfy a label.

The journey is authorized corpus admission → attributable units supplied by their producer → versioned lexical statistics and optional vectors → independently filtered candidates → explicit fusion/dedup → bounded evidence for a named consumer. This method does not parse documents or execute an answer model.

## Define units, tokenizer and statistics

Use one attributable fact, paragraph, field facet or reviewed example as a document unit. Keep `(resource, edition, unit_key)` through every channel. Do not concatenate unrelated resources or permission domains into one opaque searchable document. Extraction and chunking belong to the corpus producer; this selector introduces no extra windows unless its unit contract explicitly requires them.

Store unit text/hash, scope, current edition, tokenizer revision, token counts and optional vector identity. For each index snapshot retain document count N, each document's length, term frequencies, document frequencies and average document length. Corpus additions, removals, changed tokenization or current-edition changes invalidate the relevant statistics. Decide whether statistics are local to an authorization partition or global: shared statistics can leak corpus characteristics, so document the security tradeoff separately from candidate filtering.

Tokenizer choices include Unicode normalization, casing, punctuation, stop words, stemming and synonyms. Version the actual choices and use identical build/query rules. Short tokens may carry important product codes; stripping all short terms is a workload choice. Handle an empty corpus or an all-empty-token corpus explicitly. Query-term repetition may be ignored or weighted; specify which, rather than inheriting it accidentally.

## Calculate BM25

For unique query terms, one common positive-IDF variant is:

```text
idf(t) = ln(1 + (N - df(t) + 0.5) / (df(t) + 0.5))
length_factor(d) = k1 * (1 - b + b * dl(d) / average_length)
score(q,d) = sum(idf(t) * tf(t,d) * (k1 + 1)
                 / (tf(t,d) + length_factor(d)))
```

Require `k1 > 0`, `0 <= b <= 1`, valid frequencies and positive average length for nonempty scored corpora. An absent term contributes zero. This is one named variant; a different library's scores need not be numerically equivalent. Choose k1/b using length and term-frequency behavior in the adopting workload, then version them with tokenizer/statistics identity. They are tuning parameters, not learned confidence probabilities.

Synthetic example: two documents have tokens `renewal notice` and `contract deadline`; both lengths are two. For query `renewal`, the first document scores `ln(2)` and the other zero under this variant. Repeating `renewal` leaves the score unchanged when query terms are a set. C3 executes this arithmetic independently of any external index.

## Retrieve candidates before fusion

Every channel applies current scope, selected edition, readiness and tombstone predicates before returning neighbor IDs or text. Do not fetch a foreign neighbor and rely on a later score penalty to hide it. Keep a valid no-hit distinct from unavailable or stale channels.

A dense-first keyword bonus can reorder only its dense shortlist. If an exact lexical fact is outside that shortlist or lacks a vector, boosting cannot recover it. If lexical rescue is required, retrieve lexical and dense lists independently over the same eligible unit universe, then union them. Record per-channel candidate limits and truncation/drop causes. A null-vector record can remain eligible for lexical retrieval if the consumer's degraded-mode contract permits it.

The dense channel requires a compatible embedding space and document construction identity, as defined in [the entrypoint](../SKILL.md). Equal dimensions do not prove compatibility. Approximate-neighbor index parameters affect recall and must be selected and validated for the actual filtered workload; index existence is not recall evidence.

## Fuse, deduplicate and pack

Reciprocal rank fusion is one proposed portable choice when score scales differ:

```text
fused(unit) = sum over channels containing unit: 1 / (c + rank_in_channel)
```

Use ranks starting at one, finite positive c, one occurrence per unit per channel, and stable identity ties. Missing channels contribute no rank, but their unavailable state must remain visible. Select c and candidate-list sizes for the desired top-rank sensitivity and recall; no universal optimal value is implied. Alternatively, use calibrated score fusion with documented normalization and calibration data. Adding raw BM25 to raw cosine without scale analysis is unjustified.

Deduplicate by source/edition/unit identity, not text alone: identical wording may have different provenance or permissions. Source diversity and coverage quotas are explicit policies that may lower relevance; record that tradeoff. Pack within a full-message budget including trusted instructions, titles, citations, history, question and output allowance. Use the target tokenizer or a versioned conservative estimator; report estimation uncertainty.

The selected-evidence contract contains unit identity, exact text/digest, source location, per-channel rank/score, fused score, selected/drop reason and policy/index versions. An aggregate request must use a complete authorized source query rather than treating these selected units as the population.

## Failure and verification contract

Distinguish `empty_corpus`, `no_relevant_evidence`, `stale_index`, `forbidden`, `channel_unavailable`, `coverage_incomplete` and `retrieved`. A declared lexical-only fallback may be useful, but cannot be reported as successful full hybrid retrieval. Deletion/current-edition changes invalidate every channel and derived cache.

C3 in `../scripts/verify_contracts.py` computes BM25, verifies duplicate-query semantics and stable RRF ordering, and demonstrates a lexical hit absent from the dense-only result. C4 verifies candidate eligibility. Further implementation checks should cover Unicode tokenization, synonyms, short identifiers, near-duplicate units and filtered approximate-neighbor misses. Candidate recall, postselection coverage and answer support require separate assessment; no measured quality, speed or cost improvement is claimed.
