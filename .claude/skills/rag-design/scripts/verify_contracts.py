import hashlib
import json
import math
from collections import Counter
from pathlib import Path, PurePosixPath


class ContractError(ValueError):
    pass


def require(condition, code):
    if not condition:
        raise ContractError(code)


def text_digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_digest(value):
    text = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return text_digest(text)


def check_chunks(case):
    source = case["source"]
    bounds = case["bounds"]
    minimum, target, maximum = (bounds[key] for key in ("minimum", "target", "maximum"))
    require(0 < minimum <= target <= maximum and 0 <= bounds["overlap"] < maximum, "invalid_bounds")
    require(bool(source) and bool(case["units"]), "missing_units")
    covered_to = 0
    previous_start = -1
    for unit in case["units"]:
        start, end = unit["start"], unit["end"]
        require(type(start) is int and type(end) is int and 0 <= start < end <= len(source), "invalid_span")
        require(start >= previous_start and end > covered_to, "unordered_span")
        require(start <= covered_to, "coverage_gap")
        require(unit["text"] == source[start:end], "span_mismatch")
        require(end - start <= maximum, "oversized_unit")
        covered_to = end
        previous_start = start
    require(covered_to == len(source), "coverage_gap")


def check_embedding(case):
    expected, actual = case["expected_space"], case["actual_space"]
    fields = {"model", "revision", "document_encoder", "query_encoder", "document_preprocess", "query_preprocess", "dimensions", "metric", "normalization"}
    require(set(expected) == fields and set(actual) == fields, "invalid_space")
    require(expected == actual, "incompatible_space")
    require(type(actual["dimensions"]) is int and actual["dimensions"] > 0, "invalid_space")
    require(actual["metric"] in {"cosine", "dot", "euclidean"} and actual["normalization"] in {"none", "l2"}, "invalid_space")
    require(all(isinstance(actual[key], str) and actual[key] for key in fields - {"dimensions"}), "invalid_space")
    require(case["actual_builder"] == case["expected_builder"], "incompatible_builder")
    inputs, outputs = case["inputs"], case["outputs"]
    require(len({item["key"] for item in inputs}) == len(inputs), "duplicate_input")
    require(len(inputs) == len(outputs), "output_count")
    for ordinal, (item, output) in enumerate(zip(inputs, outputs)):
        require(output["key"] == item["key"] and output["index"] == ordinal, "output_order")
        require(output["text_digest"] == text_digest(item["text"]), "text_digest")
        vector = output["vector"]
        require(len(vector) == actual["dimensions"], "vector_dimension")
        require(all(type(value) in {int, float} and math.isfinite(value) for value in vector), "nonfinite_vector")
        norm = math.sqrt(sum(value * value for value in vector))
        require(actual["metric"] != "cosine" or norm > 0, "zero_vector")
        require(actual["normalization"] != "l2" or math.isclose(norm, 1, abs_tol=1e-9), "normalization")


def check_scope(case):
    policy, unit = case["server_policy"], case["unit"]
    predicate = case.get("user_predicate")
    if predicate is not None:
        require(set(predicate) <= {"field", "operator", "value", "purpose"}, "scope_override")
        require(predicate.get("purpose") == "analytical", "scope_override")
    require(unit["resource"] in policy["resources"], "forbidden")
    require(unit["edition"] == policy["selected_edition"], "stale")
    require(not unit["deletion_started"], "revoked")
    require(unit["state"] == "ready", "not_ready")


def check_field(case):
    field = case["field"]
    require(field["logical_type"] in {"string", "integer", "decimal", "boolean", "date", "timestamp", "duration"}, "logical_type")
    require(field["meaning"] in {"identifier", "nominal_category", "ordered_category", "instant", "calendar_date", "duration", "currency", "quantity", "ratio", "free_text"}, "meaning")
    require(set(field["roles"]) <= {"entity_key", "dimension", "time_dimension", "measure"}, "role")
    operations = field["operations"]
    require(set(operations) == {"filter", "group", "order", "aggregate"}, "operations")
    require(type(operations["group"]) is bool, "operations")
    require(set(operations["filter"]) <= {"eq", "in", "lt", "le", "gt", "ge", "is_null"}, "operations")
    require(set(operations["aggregate"]) <= {"sum", "mean", "weighted_mean", "min", "max", "row_count", "non_null_count", "distinct_count"}, "operations")
    if field["meaning"] == "identifier":
        require(not set(operations["aggregate"]) & {"sum", "mean", "weighted_mean"}, "identifier_metric")
    if "measure" in field["roles"]:
        metric = field.get("metric", {})
        require({"population", "input_grain", "output_grain", "unit", "null_policy", "aggregation"} <= set(metric), "missing_metric_contract")
        require(metric["aggregation"] in operations["aggregate"], "metric_operation")
        require(bool(metric["population"]) and bool(metric["input_grain"]), "missing_metric_contract")
    if field["meaning"] in {"instant", "calendar_date", "duration"}:
        temporal = field.get("temporal", {})
        require(bool(temporal.get("unit")), "temporal_contract")
        if field["meaning"] in {"instant", "calendar_date"}:
            require(bool(temporal.get("calendar")) and bool(temporal.get("timezone")), "temporal_contract")
    require(field["provenance"]["resource"] and field["provenance"]["edition"], "provenance")


def check_resolution(case):
    candidates = case["candidates"]
    for candidate in candidates:
        require(all(candidate[key] == case[key] for key in ("resource", "edition", "field")), "candidate_scope")
        require(type(candidate["confidence"]) in {int, float} and 0 <= candidate["confidence"] <= 1, "confidence")
    require(len({item["key"] for item in candidates}) == len(candidates), "duplicate_candidate")
    ordered = sorted(candidates, key=lambda item: (-item["confidence"], item["key"]))
    threshold, margin = case["policy"]["threshold"], case["policy"]["ambiguity_margin"]
    require(0 <= threshold <= 1 and 0 <= margin <= 1, "resolution_policy")
    status = "unresolved"
    if ordered and ordered[0]["confidence"] >= threshold:
        tied = len(ordered) > 1 and ordered[0]["confidence"] == ordered[1]["confidence"]
        close = len(ordered) > 1 and ordered[0]["confidence"] - ordered[1]["confidence"] < margin
        status = "ambiguous" if tied or close else "resolved"
    selection = case["selection"]
    if "candidate" in selection:
        require(selection["candidate"] in {item["key"] for item in candidates}, "invented_candidate")
    require(selection["status"] == status, "resolution_status")
    if status == "resolved":
        require(selection.get("candidate") == ordered[0]["key"], "wrong_winner")
        if case.get("frozen"):
            require({"field": case["field"], "value": ordered[0]["value"]} in case["frozen"], "frozen_changed")
    else:
        require("candidate" not in selection, "guessed_entity")


def unit_identity(reference):
    fields = ("resource", "edition", "unit_key")
    require(isinstance(reference, dict), "incomplete_unit_reference")
    require(all(isinstance(reference.get(field), str) and reference[field] for field in fields), "incomplete_unit_reference")
    return tuple(reference[field] for field in fields)


def check_context(case):
    if "normalization" in case:
        policy = case["normalization"]
        raw = policy["raw"]
        require(bool(raw) and all(type(value) in {int, float} and math.isfinite(value) for value in raw), "normalization_input")
        require(0 <= policy["low"] <= 1 and type(policy["cap"]) is int and policy["cap"] >= 0, "normalization_policy")
        spread = max(raw) - min(raw)
        normalized = [policy["single"]] if len(raw) == 1 else [policy["flat"]] * len(raw) if spread == 0 else [policy["low"] + (1 - policy["low"]) * (value - min(raw)) / spread for value in raw]
        require(len(normalized) == len(policy["expected_scores"]) and all(math.isclose(actual, expected, abs_tol=1e-12) for actual, expected in zip(normalized, policy["expected_scores"])), "normalization_arithmetic")
        selected = sorted(range(len(raw)), key=lambda index: (-normalized[index], index))[:policy["cap"]]
        require(selected == policy["expected_selected_indices"], "selection_cap")
        return
    units = case["units"]
    identities = [unit_identity(unit) for unit in units]
    require(len(set(identities)) == len(identities), "duplicate_unit")
    by_identity = dict(zip(identities, units))
    selected = [unit_identity(reference) for reference in case["selected"]]
    require(len(set(selected)) == len(selected) and set(selected) <= set(by_identity), "invalid_selection")
    required = {unit_identity(reference) for reference in case["required_context"]}
    require(required <= set(selected), "missing_final_context")
    total = case["overhead_cost"] + case["output_allowance"]
    for identity in selected:
        unit = by_identity[identity]
        require(unit["text_digest"] == text_digest(unit["text"]), "text_digest")
        require(type(unit["token_cost"]) is int and unit["token_cost"] >= 0, "token_cost")
        total += unit["token_cost"]
    require(total <= case["budget"], "context_budget")
    cited = set()
    for citation in case["citations"]:
        identity = unit_identity(citation)
        require(identity in by_identity, "citation_identity")
        require(identity in selected, "citation_outside_context")
        require(citation["text_digest"] == by_identity[identity]["text_digest"], "citation_identity")
        cited.add(identity)
    used = {unit_identity(reference) for reference in case["used_units"]}
    require(used <= cited, "missing_citation")


def bm25_scores(documents, query, k1, b):
    require(k1 > 0 and 0 <= b <= 1, "bm25_policy")
    frequencies = [Counter(document["tokens"]) for document in documents]
    lengths = [sum(frequency.values()) for frequency in frequencies]
    count = len(documents)
    average = sum(lengths) / count if count else 0
    if average == 0:
        return {document["key"]: 0.0 for document in documents}
    df = Counter(term for frequency in frequencies for term in frequency)
    result = {}
    for document, frequency, length in zip(documents, frequencies, lengths):
        length_factor = k1 * (1 - b + b * length / average)
        score = 0.0
        for term in set(query):
            tf = frequency[term]
            if tf:
                idf = math.log(1 + (count - df[term] + 0.5) / (df[term] + 0.5))
                score += idf * tf * (k1 + 1) / (tf + length_factor)
        result[document["key"]] = score
    return result


def check_ranking(case):
    scores = bm25_scores(case["documents"], case["query"], case["k1"], case["b"])
    for key, expected in case["expected_scores"].items():
        require(math.isclose(scores[key], expected, abs_tol=1e-12), "bm25_arithmetic")
    repeated = bm25_scores(case["documents"], case["query"] * 2, case["k1"], case["b"])
    require(scores == repeated, "query_repetition")
    lexical = sorted((key for key in scores if scores[key] > 0), key=lambda key: (-scores[key], key))
    constant = case["rank_constant"]
    require(constant > 0, "fusion_policy")
    fused = Counter()
    for channel in (lexical, case["dense"]):
        require(len(set(channel)) == len(channel), "duplicate_rank")
        for rank, key in enumerate(channel, 1):
            fused[key] += 1 / (constant + rank)
    ordered = sorted(fused, key=lambda key: (-fused[key], key))
    require(ordered == case["expected_fused"], "fusion_order")
    require(case["lexical_rescue"] in lexical and case["lexical_rescue"] not in case["dense"], "missing_rescue")


def check_governance(case):
    mode = case["mode"]
    if mode == "coverage":
        require(len(case["eligible"]) <= case["maximum"], "coverage_incomplete")
        require(case["returned"] == sorted(set(case["eligible"])), "incomplete_enumeration")
    elif mode == "publication":
        require(case["current_revision"] == case["expected_revision"], "revision_conflict")
        require(case["reviewed"], "review_required")
        files = case["files"]
        paths = [item["path"] for item in files]
        require(len(set(paths)) == len(paths) and set(case["required_files"]) <= set(paths), "incomplete_tree")
        for item in files:
            path = PurePosixPath(item["path"])
            require(not path.is_absolute() and ".." not in path.parts, "invalid_path")
            require(item["digest"] == text_digest(item["content"]), "file_digest")
        tree = [{"path": item["path"], "digest": item["digest"]} for item in sorted(files, key=lambda item: item["path"])]
        require(case["tree_digest"] == canonical_digest(tree), "tree_digest")
    elif mode == "deletion":
        require(case["inventory_complete"] and all(item["state"] == "deleted" for item in case["copies"]), "deletion_pending")
    elif mode == "resume":
        require(case["state"] != "outcome_unknown" or case["action"] == "reconcile_original", "outcome_unknown")
    elif mode == "transfer":
        pages = case["pages"]
        require(len(pages) == case["expected_pages"] and [page["ordinal"] for page in pages] == list(range(1, len(pages) + 1)), "incomplete_pages")
        require(case["observed_at"] <= case["now"], "future_observation")
        require(case["schema"] == case["expected_schema"], "schema_drift")
        require(case["region"] in case["allowed_regions"] and set(case["classes"]) <= set(case["allowed_classes"]), "policy_denied")
        require(case["next_watermark"] == case["expected_watermark"], "watermark")
        total_bytes = 0
        for page in pages:
            require(page["digest"] == text_digest(page["body"]), "page_digest")
            require(page["bytes"] == len(page["body"].encode("utf-8")), "page_bytes")
            total_bytes += page["bytes"]
        require(total_bytes <= case["maximum_bytes"], "transfer_bound")
        require(case["distinct_keys"] == sum(page["rows"] for page in pages), "dedup_coverage")
    elif mode == "overlay":
        require(case["reviewed"], "review_required")
        require(case["existing_slug"] != case["requested_slug"] or case["existing_query_digest"] == case["requested_query_digest"], "slug_conflict")
    else:
        raise ContractError("unknown_lifecycle_mode")


def main():
    fixture_path = Path(__file__).resolve().parents[1] / "assets" / "contract-examples.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    require(fixture["format_version"] == 1, "fixture_version")
    validators = {"C1": check_chunks, "C2": check_embedding, "C3": check_ranking, "C4": check_scope, "C5": check_field, "C6": check_resolution, "C7": check_context, "C8": check_governance}
    counts = {}
    for group, validator in validators.items():
        cases = fixture["checks"][group]
        require(bool(cases), "empty_check_group")
        for case in cases:
            actual = "ok"
            try:
                validator(case)
            except ContractError as error:
                actual = str(error)
            if actual != case["expected"]:
                raise AssertionError(f"{group}/{case['name']}: expected {case['expected']}, got {actual}")
        counts[group] = len(cases)
    print(json.dumps({"status": "pass", "cases": sum(counts.values()), "checks": counts}, sort_keys=True))


if __name__ == "__main__":
    main()
