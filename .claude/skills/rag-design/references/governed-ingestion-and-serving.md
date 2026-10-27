# Govern ingestion and serving

## State the design boundary

Bind evidence to current authority, source policy, immutable identity and explicit lifecycle. The design covers structured transfer, derived copies, embedding custody, complete authorized context and reviewed publication. It supplies no ready document adapter, distributed worker, storage/index service, query encoder or relevance-ranked answering runtime. Those integrations require their own implementation and acceptance; a category label or injected interface is insufficient.

Journey: current identity/grant/source-policy admission → certified adapter/placement → full or incremental transfer → validated snapshot/copy receipts → optional compatible embedding/capture → explicit reader or deterministic enumeration → reviewed publication/use → revocation/deletion. Transfer pages and typed observations are units; canonical capture uses no paragraph splitting/overlap. Deterministic enumeration itself uses neither lexical indexing nor embeddings.

## Derive authority and immutable knowledge identity

Derive authenticated principal, current membership/grant, permitted source and policy revision. Caller organization/source identifiers are equality assertions against that authority. Recheck immediately before external use and publication. A digest proves byte identity, not continued access, approval or truth.

A minimal neutral model has a source policy, snapshot, evidence edition, copy registry, operation attempt, immutable publication and mutable current pointer. Source policy defines permitted processors/regions/classes and lifecycle. Snapshot binds policy/source revision and transfer evidence. A publication binds exact evidence/query contracts and complete artifact tree. Current pointer uses expected revision rather than last-writer-wins replacement.

Knowledge identity includes authenticated scope, sources/editions, query-definition and parameter/result-contract versions, workflow/builder revisions, processor policy and representation identity where used. Canonicalization must specify accepted types, Unicode/number treatment, object-key order and ordered versus set-like arrays. Hash exact bytes under a named canonicalizer. Exclude only explicitly nonidentity fields such as creation time; do not silently omit authority or source bindings.

The controlled file-tree example sorts file entries by path, represents each as path plus content digest, sorts object keys, emits compact JSON with literal Unicode, excludes a trailing newline and hashes UTF-8 bytes. It contains strings/arrays/objects only. This is a bounded tree-digest contract, not a general cross-language canonical JSON standard. Extending identity to decimals or arbitrary observations requires a declared number/Unicode contract and compatibility tests rather than assuming every serializer agrees.

Context-bound and query-capability-bound knowledge may have different source cardinalities. Document that schema distinction and adapter preconditions rather than coercing an empty source array into unbound execution authority. Reads bind immutable identity/digest and return staleness separately.

## Enumerate complete authorized context

For a policy-context consumer, deterministic enumeration is valid without question relevance:

```text
derive current scope and selected source
sort candidate bindings by stable identity
resolve each binding's current authority and ready option
exclude refused/revoked/nonmatching bindings
fail explicitly on required infrastructure uncertainty
if complete eligible coverage exceeds the caller's admitted bound:
    return coverage_incomplete
return the entire eligible set and its coverage receipt
```

Two eligible records with a maximum of one produce incomplete coverage, not a silent top-one answer. An unrelated question with the same scope may return the same set because no relevance ranking occurs. Name that property. If the product requires question-ranked retrieval, implement an authorized corpus/index/query/selection/prompt path separately. Never label eligibility order as semantic relevance.

Bind cached context to current grant/source/policy/edition and a finite expiry. Expiry limits reuse but does not prove current permission; reauthorization may still be required. Unsupported sections return unavailable rather than an invented empty success.

## Admit a transfer strictly

Require an actually supported adapter/profile and certified placement for the requested operation. A request binds source, policy revision, input digest, idempotency identity, attempt fence, bounds and cursor. Full refresh has no incremental fields. Incremental mode binds previous/next watermark, dedup keys and certification; validate transition against stored source state.

```json
{
  "source": "ledger-a",
  "policy_revision": 3,
  "operation": "snapshot-read",
  "idempotency": "request-7",
  "attempt": {"key": "attempt-2", "fence": 2},
  "cursor": {"mode": "incremental", "previous": "mark-4", "next": "mark-5", "dedup_keys": ["event_key"]},
  "limits": {"pages": 4, "bytes": 4096}
}
```

Numbers and identities here are illustrative, not protocol defaults. Choose finite limits from admitted capacity, source semantics and retention policy. Validate strict keys, types, nonempty stable keys, sorted unique set fields and coherent policy/source identities. If an operation requires priced processing or a budget ledger, missing configuration is unavailable rather than free work; this reference grants no paid execution authority.

Recheck authorization immediately before the external start. A fenced attempt owns one dispatch. If start/outcome is ambiguous, record `outcome_unknown` and reconcile that original attempt; do not automatically retransmit or create a new idempotency key. Cancellation and retained partial results still need explicit custody/deletion treatment.

## Validate transfer and eligible use

Worker output contains ordered page ordinals/counts/hashes, byte/row totals, schema/content identity, classes/region, observation time, watermark, copy attestations and accounting. It need not contain raw rows. Require contiguous complete pages, expected schema, bounded size, permitted region/classes, matching snapshot copy and nonfuture observation time. Incremental completion validates the expected watermark and dedup/row accounting.

Be explicit about trust: verifying attested metadata is not recomputing raw page bytes. If raw fixture bytes are available, a local checksum check can validate them; production worker integrity remains a separate boundary. Failed/partial/unknown transfers stay unpublished with their copy evidence intact.

Use gates reread snapshot/policy and require eligible state, current exact source/policy binding, acceptable staleness, no deletion and compatible processor/placement. A local-residency requirement cannot be satisfied by an arbitrary external embedding adapter. Passing a callback gate does not itself load bytes, query an index or assemble a prompt.

## Bind embedding and capture custody

An embedding job binds ordered unique input IDs, exact UTF-8 texts/hashes, source/evidence edition, model/revision/encoder contract and dimensions. Validate response encoding/JSON, exact model/space, input count/order/IDs, finite coordinates and required dimension. For cosine consumers, require nonzero vectors and specified normalization policy. Preserve raw response and parsed result under the original attempt; response-retention ambiguity is not permission to resend.

The full embedding space includes compatible document/query encoders and preprocessing, metric and normalization. A canonical JSON observation and a prose-rendered profile are different document builders/preimages. Bind builder/text/vector hashes and source/edition/producer attempt. Equal dimensions, declared model metadata or a null representation hash do not prove indexed vectors exist.

Evidence capture may be pure validation/canonicalization/hashing over supplied observations rather than a database reader or index writer. Require coherent generation/epoch, query footprint, policy, required coverage and compatible representation. A valid capture still needs explicit storage, knowledge, index, reader and compiler joins. If a downstream component does not support that capture type, return unavailable rather than weakening the contract.

Imported semantic documents create draft meaning with provenance. Source hints remain unbound until server authority resolves them; accepting draft meaning does not make it reviewed or executable. Parsing definitions is not document-vector retrieval.

## Publish, revoke and delete

Publication rechecks current authority, source/evidence identity, scope, representation compatibility, reviewed disposition and complete candidate tree/digest. A selector binds role/kind/native target. Expected-revision compare-and-swap distinguishes exact replay from competing publication. A current pointer alone does not establish client reload compatibility or reauthorization.

Register every staged/snapshot/cache/index/vector/export copy, including region and deletion state. Block use when deletion begins, then complete only after inventory reconciliation and explicit copy receipts. A missing response, absent timer or elapsed deadline is not deletion proof. Pending unresolved copies keep deletion pending. Retention and audit evidence follow policy without retaining prohibited source bodies indefinitely.

## Build and verify

Implement authority/policy → strict schemas/canonicalization → immutable identities → complete enumeration → certified transfer/copy lifecycle → eligible-use gate → embedding custody → capture/storage/index/reader joins → reviewed publication → revocation/deletion. Each absent adapter or join stays explicitly unavailable until built. Relevance ranking and answering remain separate consumers with their own contracts.

C2/C4/C8 in `../scripts/verify_contracts.py` check synthetic identity/readiness, exact representation custody, incomplete pages, complete coverage, expected-revision conflict, ambiguous retry and unresolved deletion. This finite receipt checker is not a distributed service or deployment proof. A real implementation additionally needs race/cancellation, processor custody, live revocation and deletion integration checks under its operational authorization.
