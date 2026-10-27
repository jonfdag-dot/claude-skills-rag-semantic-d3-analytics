# Build value evidence with honest coverage

Read this when constructing a bounded corpus for entity/filter resolution. Inputs are exact population [profiles](02-column-profiles-and-enhancement.md), [meaning](03-column-semantics-and-facets.md), source/processor permission and full generation identity. Outputs are admission receipts, ranked literals, conditional companions and retrieval units. A few profile examples are a different product.

## Admit a field explicitly

Define an ordered first-failure policy. A typical order checks meaning availability, intended value-lookup role, non-null population, supported physical type, key/index restrictions, text exposure/length, uniqueness/constant behavior, distinct ceiling and workload budget. Each receipt contains field ID, evidence revision, include/exclude/pending, first reason, policy version and measured/unknown facts. Unknown values need an explicit defer/unsupported rule.

Thresholds depend on sensitivity, memory/scan cost and intended lookup quality; choose and validate them for the workload. The workbook deliberately supplies a small illustration policy and tests its equality/just-over boundaries. A numeric measure or temporal field excluded as a value-vector candidate remains available as a measure/time companion. An identifier can require a separately authorized exact lookup. A diagnostic “use deterministic lookup” hint does not implement that route.

Enumerate non-null values from the same bound query population. Group by exact raw value, count rows and order frequency descending with a stable tie-break. Keep SQL value type and exact literal separate from display normalization. Use stable value identity plus field/generation, not rank alone, for idempotent writes. Define deletion/invalidation when the source query changes.

Coverage records must distinguish observed domain size, selected values, persisted rows, embedded rows and retained source-row frequency. Derive denominators explicitly. A selected/written fraction says nothing about unobserved source values when the domain is estimated. Partial insertion, empty extraction and per-target failure need receipts; none can yield “exhaustive” merely because selection was admitted.

## Attach conditional observations

Choose anchors and targets by consumer need. Use one admitted relation for each conditional observation; do not invent joins between unrelated source tables. For each anchor value collect bounded categorical companions, time ranges and metric ranges, with target identity, population, method, cap, returned counts and status. A stable per-anchor selection avoids starving later anchors through one global limit.

The teaching companion record is `{anchor_field,anchor_value,categoricals:[{field_id,values,returned_distinct,complete}],temporals:[{field_id,min,max,bounds,precision}],metrics:[{field_id,min,max}],status}`. Returned distinct entries differ from the anchor's row frequency. Missing target data can mean not selected, no non-null observation, cap exclusion or failure; represent the reason rather than imply nonoccurrence.

Co-occurrence is conditional evidence. It is not a functional dependency, complete domain, join proof or mandatory SQL filter. An observed inclusive maximum date must be converted under a documented interval policy before using `< end`; timestamp maxima require an explicit precision policy. Preserve the user's requested range independently from stored availability. Sampling a physical table and limiting output groups are different operations; source SQL syntax and coverage require backend-specific validation.

## Serialize compatible retrieval units

Choose the corpus unit: one raw canonical value or one value plus selected context. The workbook demonstrates a deterministic contextual sentence containing field/source label, exact value, categorical companions and time interval. Metric ranges stay structured in that example; this omission is declared. A context bound applies after rendering and records truncation. This is value enumeration, not overlapping document-window chunking.

Store text preimage/hash, serializer version, exact evidence/generation identity, embedding-space contract and status. Update by exact row identity; a new context cannot overwrite an older generation's vector. Re-embed when text or encoder contract changes, and validate response count/order, finite dimensions and normalization requirements.

An embedding-space contract binds space ID/revision, dimensions, distance, normalization and both admitted encoder recipes: document and query model/revision/preprocessing/prefix. Asymmetric encoders may use different models or recipes while sharing a deliberately declared space. Equal vector length is insufficient. Query and document records must each match their role's recipe in the same admitted pair contract. Similarity is ranking evidence, never authority or calibrated semantic certainty.

Profiles, meaning facets, query facets and values are different corpora. Each unit needs its own serializer and consumer. A writer's existence does not establish a reachable retrieval reader or answering path. Track required vector readiness separately from fact/meaning readiness and make all reads select the published generation.

The verifier checks ordered admission, category frequencies, conditional companions, actual coverage, text preservation and compatible encoder-pair metadata. It creates no embeddings and claims no ranking quality. Data-egress policy must cover values and companions at every projection; excluding identifiers alone is not a privacy policy.
