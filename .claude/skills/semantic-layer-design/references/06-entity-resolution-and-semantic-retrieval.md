# Resolve entity words into checked filter bindings

Read this to turn a user's entity words into exact admitted values. Inputs are question/intent, selected analytical roles, authorized query scope, published generation and [value evidence](05-value-samples-and-cooccurrence.md). Outputs are per-token resolved/ambiguous/unresolved states and typed filter bindings. Candidate rank does not establish business meaning, source freshness, permission or metric algebra.

## Retrieve candidates without losing identity

Preserve immutable original token ID/text. Normalize a lookup copy while keeping display-safe text and exact raw predicate literal separate. Generic words such as “total” should not become entity values merely because token extraction emitted them; an explicit exact source value may still be legitimate under the request. Record token source and removal reason so an emptied list does not silently bypass a required route.

Key candidates by scope/source/query/population/generation/field/value identity. Retrieve deterministic exact/substring/acronym evidence with explicit pagination/order and completeness status. Add compatible dense candidates only from the admitted space and generation. Distinguish no hit, unavailable vectors, dependency error and timeout. If a database API returns errors as values, inspect them.

Choose fusion deliberately. Ordered union means deterministic candidates precede dense candidates and exact identities deduplicate; it is not reciprocal-rank fusion or a learned ranker. Per-token limits avoid one common token consuming the whole allowance. A candidate dropped at the cap is a selection-policy loss. Alternative-column retrieval must preserve original column identity and cannot imply that a literal belongs to the canonical dimension.

## Select with reversible values

A bounded model selector can receive candidate IDs, complete display text, original tokens and relevant intent. Its schema returns original token ID, selected candidate IDs, concise rationale/evidence and an explicit no-match/ambiguity state. Validate token membership, candidate membership, field/scope/generation, enum/types and policy bounds. A confidence-zero fallback cannot bypass membership validation. Truncating a long display string must not require the model to reproduce an unseen full predicate value; select by ID.

Column synonyms describe field meaning. Value aliases map alternative names to exact identities. A temporary typo/acronym pattern plan is another object: `{token_id,pattern,kind,strength,source,evidence_refs}`. Kinds can be exact/prefix/contains/word; sources raw/corrected/alias/variant. Define normalized exact match, unique prefix, bounded approximate match and acronym rules, deduplication and ambiguity behavior. Short ambiguous tokens need stricter treatment. Do not average model confidence, vector similarity, lexical score and frequency weight into a probability.

Frequency can support a tie-break under a declared policy, but it cannot decide business intent. If used, a log-normalized frequency weight can temper skew; missing frequency remains unknown rather than an invented certainty. Exact identity precedence and ambiguity rules must be explicit. Confusable site/zone strings can produce multiple candidates despite one individually exact match.

## Distinguish evidence and recovery

Stored sample receipts, bound source projections and live validation are different evidence classes. Retain original token, candidate, exact field/value and each observation's population/time/source. Cross-column companions can suggest candidates or filters; actual bound source projection is required when the contract needs current membership. Never copy the same string into another field as proof of identity.

Implement a reachable route for each unresolved required token or return unresolved/unsupported. An initial corpus miss differs from a previously resolved value demoted by fresh zero evidence. Recovery needs explicit authorization, admitted columns, bound predicates, probe/deadline budget and ambiguity acceptance. A helper with no call path is not a fallback. Define whether authoritative stored evidence can survive zero/error live evidence, and disclose that policy; it is not proof of live confirmation.

Keep availability ranges separate from the requested interval. Convert inclusive stored date bounds to explicit execution intervals when appropriate; do not silently trim the user's requested date range. Recovery and co-occurrence cannot widen authenticated scope.

## Publish typed bindings

The handoff is `{identity,field_id,operator,typed_values,candidate_ids,purpose,evidence_refs}`. Resolve identifiers from admitted field metadata, not user text. Emit separate typed bound parameters and a predicate fragment; validate parameter-name uniqueness, exact value agreement, operator arity and duplicate/conflicting bindings.

| Operator | Required values |
| --- | --- |
| eq/ne/gt/gte/lt/lte/LIKE/ILIKE | Exactly one typed value |
| IN/NOT IN | Nonempty typed list |
| BETWEEN | Exactly two ordered compatible values |
| IS NULL/IS NOT NULL | None |
| contains/starts_with | One value; wildcard construction remains in bound expression logic |

Authorization-purpose predicates are server-derived and intersect analytical predicates. Contradictory values can produce an empty set; they cannot remove authorization. Read-only validation, source policy, row/cell budget and reviewed metric contract remain independent downstream checks. Post-result series presence can detect a missing requested entity but does not certify every business decision or scope filter.

The workbook checks exact and long-value ID selection, wrong-field/stale candidate rejection, unresolved and ambiguous states, typed filter arity and scope intersection. It supplies selector decisions as fixtures, not model responses. No retrieval accuracy or deployed fallback availability is asserted.
