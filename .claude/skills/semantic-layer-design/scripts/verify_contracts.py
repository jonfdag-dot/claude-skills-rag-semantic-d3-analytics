import copy
import hashlib
import json
import re
import sqlite3
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from fractions import Fraction
from pathlib import Path, PurePosixPath


class ContractError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ContractError(message)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def expect_rejected(label, operation, errors=(ContractError,)):
    try:
        operation()
    except errors as error:
        require(bool(str(error)), f"{label}: missing rejection diagnostic")
    else:
        raise ContractError(f"{label}: invalid input was accepted")


def typed_value(value, field):
    if value is None:
        require(field["nullable"], "null in nonnullable field")
        return None
    logical_type = field["logical_type"]
    if logical_type == "integer":
        require(type(value) is int, "integer field requires integer")
        return value
    if logical_type == "decimal":
        require(isinstance(value, str), "decimal fixture uses lossless strings")
        result = Decimal(value)
        require(result.is_finite(), "nonfinite decimal")
        return result
    if logical_type == "timestamp":
        require(isinstance(value, str), "timestamp requires text representation")
        result = datetime.fromisoformat(value)
        require(result.tzinfo is not None, "timestamp timezone missing")
        return result.astimezone(timezone.utc)
    require(logical_type == "string" and isinstance(value, str), "unsupported fixture value type")
    return value


def validate_workbook(workbook, schema):
    require(workbook["contract_version"] == 1, "unsupported contract version")
    require(set(workbook) == set(schema["required"]), "workbook top-level contract mismatch")
    fields = workbook["fields"]
    identifiers = [field["field_id"] for field in fields]
    require(len(identifiers) == len(set(identifiers)), "duplicate field IDs")
    field_schema = schema["$defs"]["field"]
    for field in fields:
        require(set(field) == set(field_schema["required"]), "field shape mismatch")
        require(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", field["field_id"]), "invalid field ID")
        for property_name in ("logical_type", "meaning", "missing_value_policy"):
            allowed = field_schema["properties"][property_name]["enum"]
            require(field[property_name] in allowed, f"invalid {property_name}")
        allowed_roles = field_schema["properties"]["roles"]["items"]["enum"]
        require(bool(field["roles"]) and set(field["roles"]) <= set(allowed_roles), "invalid roles")
        if field["meaning"] == "entity_identifier":
            require("measure" not in field["roles"], "identifier cannot become measure")
            require(not set(field["operations"]["aggregate"]) & {"sum", "avg"}, "identifier arithmetic")
    for row in workbook["rows"]:
        require(set(row) == set(identifiers), "row/field inventory mismatch")
        for field in fields:
            typed_value(row[field["field_id"]], field)
    require(len({row["visit_id"] for row in workbook["rows"]}) == len(workbook["rows"]), "duplicate visit key")
    metric_ids = [metric["metric_id"] for metric in workbook["metrics"]]
    require(len(metric_ids) == len(set(metric_ids)), "duplicate metric IDs")
    by_id = {field["field_id"]: field for field in fields}
    for metric in workbook["metrics"]:
        require(metric["field_id"] in by_id, "unknown metric field")
        require(metric["aggregation"] in by_id[metric["field_id"]]["operations"]["aggregate"], "metric operation mismatch")
        require(bool(metric["merge_state"]), "missing merge state")


def fixture_connection(workbook):
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.execute(
        "CREATE TABLE service_visits (visit_id TEXT PRIMARY KEY, site_code INTEGER NOT NULL, "
        "site_name TEXT NOT NULL, zone TEXT NOT NULL, started_at TEXT NOT NULL, "
        "billed_amount NUMERIC NOT NULL, feedback_score INTEGER, outcome TEXT NOT NULL)"
    )
    connection.executemany(
        "INSERT INTO service_visits VALUES (:visit_id, :site_code, :site_name, :zone, "
        ":started_at, :billed_amount, :feedback_score, :outcome)", workbook["rows"]
    )
    connection.commit()
    permitted = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION, sqlite3.SQLITE_RECURSIVE}
    connection.set_authorizer(lambda action, first, second, database, trigger: sqlite3.SQLITE_OK if action in permitted else sqlite3.SQLITE_DENY)
    return connection


def admitted_binding(definition, supplied):
    require(set(supplied) <= {definition["name"]}, "undeclared parameter")
    if definition["name"] in supplied:
        value = supplied[definition["name"]]
    else:
        require(bool(definition.get("approval_id")), "default lacks approval receipt")
        value = definition.get("approved_default")
    require(value is not None or definition["nullable"], "missing required parameter")
    require(isinstance(value, str) and value in definition["allowed_values"], "invalid parameter value")
    return {definition["name"]: value}


def checked_aliases(cursor):
    aliases = [column[0] for column in cursor.description]
    require(len(aliases) == len(set(aliases)), "duplicate result alias")
    return aliases


def profile(values, field):
    parsed = [typed_value(value, field) for value in values]
    observed = [value for value in parsed if value is not None]
    total = len(parsed)
    nonnull = len(observed)
    distinct = len(set(observed))
    require(0 <= distinct <= nonnull <= total, "invalid exact counts")
    text = [value for value in observed if isinstance(value, str)]
    return {
        "rows": total, "nonnull": nonnull, "distinct": distinct,
        "null_fraction": Fraction(total - nonnull, total) if total else None,
        "min": min(observed) if observed else None, "max": max(observed) if observed else None,
        "average_length": Fraction(sum(map(len, text)), len(text)) if text else None,
        "examples": sorted(set(observed), key=str)[:3], "method": "exact_fixture_population"
    }


def project_scalar(payload, expected_type, nullable=False):
    require(isinstance(payload, dict) and set(payload) == {"value"}, "invalid scalar wrapper")
    value = payload["value"]
    require((nullable and value is None) or type(value) is expected_type, "scalar type mismatch")
    return value


def effective_meaning(candidate, edits, identity, authority):
    require(candidate["generation_id"] == identity["generation_id"], "stale candidate generation")
    result = copy.deepcopy(candidate)
    result["description"] = project_scalar(candidate["description"], str)
    result["unit"] = project_scalar(candidate["unit"], str)
    for edit in edits:
        receipt = authority.get(edit["review_id"])
        require(receipt is not None, "unadmitted review receipt")
        require(receipt["scope_id"] == identity["scope_id"], "review scope mismatch")
        require(receipt["query_revision"] == identity["query_revision"], "review revision mismatch")
        require(receipt["field_id"] == edit["field_id"] == candidate["field_id"], "review field mismatch")
        require(edit["generation_id"] == identity["generation_id"], "stale edit applicability")
        require(edit["operation"] == "replace", "unsupported edit operation")
        require(edit["path"] in {"description", "guidance"}, "unsupported edit path")
        value = edit["value"]
        if edit["path"] == "description":
            require(isinstance(value, str), "reviewed description requires string")
        else:
            require(isinstance(value, list) and all(isinstance(item, str) for item in value), "reviewed guidance requires array")
        result[edit["path"]] = copy.deepcopy(value)
    result["effective_revision"] = digest(result)
    return result


def meaning_facets(meaning):
    return [
        {"path": "description", "kind": "scalar", "payload": {"value": meaning["description"]}},
        {"path": "unit", "kind": "scalar", "payload": {"value": meaning["unit"]}},
        {"path": "guidance", "kind": "array", "payload": meaning["guidance"]}
    ]


def consumer_projection(facets):
    result = {}
    for facet in facets:
        path = facet["path"]
        require(path not in result, "duplicate semantic path")
        if path in {"description", "unit"}:
            require(facet["kind"] == "scalar", "scalar kind mismatch")
            result[path] = project_scalar(facet["payload"], str)
        elif path == "guidance":
            require(facet["kind"] == "array" and isinstance(facet["payload"], list), "guidance shape mismatch")
            require(all(isinstance(item, str) for item in facet["payload"]), "guidance member mismatch")
            result[path] = list(facet["payload"])
        else:
            raise ContractError("unsupported semantic path")
    require(set(result) == {"description", "unit", "guidance"}, "missing semantic path")
    return result


def coherent_hint(hint):
    result = dict(hint)
    if result["unit"] == "percent":
        result["behavior"] = "rate"
    require(result["behavior"] in {"flow", "level", "rate"}, "unknown metric behavior")
    require(not (result["behavior"] in {"rate", "level"} and result["additive"] is True), "contradictory additivity")
    return result


def value_admission(field, facts, policy):
    if not field.get("meaning"):
        return "missing_meaning"
    if field["meaning"] not in {"nominal_category", "ordinal_category"}:
        return "meaning_excluded"
    if facts["nonnull"] == 0:
        return "all_null"
    if field["logical_type"] != "string":
        return "type_excluded"
    if "entity_key" in field["roles"]:
        return "key_excluded"
    if facts["average_length"] is None:
        return "length_unknown"
    if facts["average_length"] > policy["max_average_length"]:
        return "long_text"
    if facts["distinct"] == 1 or facts["distinct"] / facts["rows"] > policy["max_unique_fraction"]:
        return "uniqueness_excluded"
    if facts["distinct"] > policy["max_distinct"]:
        return "distinct_ceiling"
    return "eligible"


def ranked_values(rows, field_id, limit):
    frequencies = Counter(row[field_id] for row in rows if row[field_id] is not None)
    return sorted(frequencies.items(), key=lambda item: (-item[1], str(item[0])))[:limit]


def companions(rows, anchor_field, anchor_value):
    matched = [row for row in rows if row[anchor_field] == anchor_value]
    require(bool(matched), "unknown anchor")
    categoricals = []
    for field_id in ("zone", "outcome"):
        values = sorted({row[field_id] for row in matched})
        categoricals.append({"field_id": field_id, "values": values, "returned_distinct": len(values), "complete": True})
    instants = [datetime.fromisoformat(row["started_at"]).astimezone(timezone.utc) for row in matched]
    amounts = [Decimal(row["billed_amount"]) for row in matched]
    return {
        "anchor_field": anchor_field, "anchor_value": anchor_value, "row_frequency": len(matched),
        "categoricals": categoricals,
        "temporals": [{"field_id": "started_at", "min": min(instants).isoformat(), "max": max(instants).isoformat(), "bounds": "closed", "precision": "second"}],
        "metrics": [{"field_id": "billed_amount", "min": str(min(amounts)), "max": str(max(amounts))}],
        "status": "complete_fixture_population"
    }


def contextual_text(evidence):
    pieces = [f"{item['field_id']}: {', '.join(item['values'])}" for item in evidence["categoricals"]]
    pieces.extend(f"{item['field_id']}: {item['min']} to {item['max']} ({item['bounds']})" for item in evidence["temporals"])
    return f"{evidence['anchor_field']}: {evidence['anchor_value']}; " + "; ".join(pieces)


def encoder_record(contract, role):
    return {
        "space_id": contract["space_id"], "space_revision": contract["revision"],
        "dimensions": contract["dimensions"], "distance": contract["distance"],
        "normalization": contract["normalization"], "role": role,
        "encoder": copy.deepcopy(contract[f"{role}_encoder"])
    }


def compatible_encoders(document, query, contract):
    require(document == encoder_record(contract, "document"), "document encoding mismatch")
    require(query == encoder_record(contract, "query"), "query encoding mismatch")
    return True


def select_candidate(token_id, selection, candidates, identity, allowed_fields):
    require(selection["token_id"] == token_id, "unknown original token")
    if selection["status"] == "unresolved":
        require(selection["candidate_id"] is None, "unresolved selection has candidate")
        return {"status": "unresolved"}
    require(selection["status"] == "resolved", "explicit ambiguity requires clarification")
    matches = [candidate for candidate in candidates if candidate["candidate_id"] == selection["candidate_id"]]
    require(len(matches) == 1, "candidate membership mismatch")
    candidate = matches[0]
    require(candidate["identity"] == identity, "candidate scope/generation mismatch")
    require(candidate["field_id"] in allowed_fields, "candidate field mismatch")
    return {"status": "resolved", "field_id": candidate["field_id"], "value": candidate["value"]}


def project_filter(field, operator, values):
    require(operator in field["operations"]["filter"], "operator not admitted")
    counts = {"eq": 1, "between": 2, "is_null": 0}
    require(bool(values) if operator == "in" else len(values) == counts[operator], "filter arity mismatch")
    for value in values:
        typed_value(value, field)
    if operator == "between":
        require(typed_value(values[0], field) <= typed_value(values[1], field), "reversed filter interval")
    return {"field_id": field["field_id"], "operator": operator, "values": list(values)}


def admitted_aggregation(field, metric, requested):
    require(metric["field_id"] == field["field_id"], "metric field mismatch")
    require(metric["behavior"] != "unknown", "unknown aggregation contract")
    require(requested == metric["aggregation"] and requested in field["operations"]["aggregate"], "aggregation not admitted")
    return requested


def merge_mean(groups):
    require(all("sum" in group and group.get("nonnull_count", 0) > 0 for group in groups), "mean needs sum/count state")
    return Fraction(sum(group["sum"] for group in groups), sum(group["nonnull_count"] for group in groups))


def merge_metric_states(states, operation):
    require(bool(states), "missing metric state")
    signature = ("identity", "metric_id", "unit", "input_grain")
    require(all(all(state[key] == states[0][key] for key in signature) for state in states), "incompatible population/unit/grain")
    if operation == "avg":
        return merge_mean(states)
    require(operation in {"sum", "min", "max"}, "unsupported merge operation")
    require(all(operation in state for state in states), "insufficient merge state")
    values = [state[operation] for state in states]
    return {"sum": sum, "min": min, "max": max}[operation](values)


def joined_artifacts(records, identity):
    require(all(record["identity"] == identity for record in records), "mixed artifact generation")
    keys = [record["field_id"] for record in records]
    require(len(keys) == len(set(keys)), "ambiguous field identity")
    return {record["field_id"]: record["payload"] for record in records}


def cache_key(identity, effective_revision, serializer):
    return digest({"identity": identity, "effective_revision": effective_revision, "serializer": serializer})


def project_consumer_payload(rows, bindings, metrics, identity):
    projected = copy.deepcopy(bindings)
    for binding in projected.values():
        if "metric_id" in binding:
            require(binding["metric_id"] in metrics, "unknown consumer metric")
            binding["unit"] = metrics[binding["metric_id"]]["unit"]
    return {"identity": copy.deepcopy(identity), "rows": copy.deepcopy(rows), "bindings": projected}


def validate_consumer_payload(payload, expected_bindings, metrics, identity):
    require(set(payload) == {"identity", "rows", "bindings"}, "consumer payload shape mismatch")
    require(payload["identity"] == identity, "consumer identity mismatch")
    require(set(payload["bindings"]) == set(expected_bindings), "consumer binding coverage mismatch")
    aliases = []
    for role, declaration in expected_bindings.items():
        expected = dict(declaration)
        require(bool(expected["alias"]) and bool(expected["label"]), "consumer alias/label missing")
        if "metric_id" in expected:
            require(expected["metric_id"] in metrics, "unknown declared consumer metric")
            expected["unit"] = metrics[expected["metric_id"]]["unit"]
            require(isinstance(expected["unit"], str) and bool(expected["unit"].strip()), "required consumer unit missing")
        require(payload["bindings"][role] == expected, "consumer alias/label/metric/unit mismatch")
        aliases.append(expected["alias"])
    require(len(aliases) == len(set(aliases)), "duplicate consumer alias")
    require(bool(payload["rows"]) and all(set(row) == set(aliases) for row in payload["rows"]), "consumer row/alias mismatch")


def publish(previous, expected_fields, artifacts, identity, claim, current_claim, required_vectors, ready_vectors):
    fence = ("job_id", "generation_id", "attempt", "holder", "input_hash")
    require(all(claim[key] == current_claim[key] for key in fence), "stale attempt fence")
    require(claim["state"] == current_claim["state"] == "running", "claim not running")
    require(claim["delivery"] == "acknowledged", "delivery unknown")
    require(claim["generation_id"] == identity["generation_id"], "claim generation mismatch")
    require(claim["input_hash"] == digest(identity), "claim input mismatch")
    joined = joined_artifacts(artifacts, identity)
    require(set(joined) == set(expected_fields), "incomplete required coverage")
    require(all(record["status"] == "ready" for record in artifacts), "partial artifact")
    require(set(required_vectors) <= set(ready_vectors), "required vectors pending")
    return {"generation_id": identity["generation_id"], "input_hash": digest(identity), "previous": previous["generation_id"]}


def require_reviewed_rule(kind, definition, projected_fields, reviewed_components=None):
    require(definition["status"] == "reviewed", "definition not reviewed")
    if kind == "preaggregate":
        keys = definition["grain_keys"]
        require(bool(keys) and set(keys) <= set(projected_fields), "unknown or unavailable grain key")
    elif kind == "ratio":
        components = definition["components"]
        require(len(components) == 2 and len(set(components)) == 2, "ratio needs distinct reviewed components")
        require(reviewed_components is not None and set(components) <= set(reviewed_components), "ratio component unavailable")
        require(all(reviewed_components[name]["status"] == "reviewed" for name in components), "ratio component not reviewed")
        require(all(set(reviewed_components[name]["fields"]) <= set(projected_fields) for name in components), "ratio component outside footprint")
    elif kind == "snapshot":
        require(definition.get("aggregation") == "latest" and bool(definition.get("time_field")), "snapshot needs latest semantics")
        require(definition["time_field"] in projected_fields, "snapshot time outside footprint")
        keys = definition.get("entity_keys")
        require(isinstance(keys, list) and bool(keys) and all(isinstance(key, str) for key in keys), "snapshot entity keys missing")
        require(len(keys) == len(set(keys)) and set(keys) <= set(projected_fields), "snapshot entity keys outside footprint or duplicated")
        require(definition.get("time_order") == "descending", "snapshot latest time order missing or invalid")
        ties = definition.get("tie_breakers")
        require(isinstance(ties, list) and bool(ties), "snapshot tie rule missing")
        tie_fields = []
        for tie in ties:
            require(isinstance(tie, dict) and set(tie) == {"field_id", "direction"}, "snapshot tie declaration invalid")
            require(tie["field_id"] in projected_fields and tie["field_id"] not in set(keys) | {definition["time_field"]}, "snapshot tie field unavailable or ineffective")
            require(tie["direction"] in {"ascending", "descending"}, "snapshot tie order missing or invalid")
            tie_fields.append(tie["field_id"])
        require(len(tie_fields) == len(set(tie_fields)), "duplicate snapshot tie fields")
    else:
        raise ContractError("supported rule unavailable")


def file_manifest(files, identity):
    entries = []
    for name, content in sorted(files.items()):
        path = PurePosixPath(name)
        require(not path.is_absolute() and ".." not in path.parts, "unsafe manifest path")
        encoded = content.encode("utf-8")
        entries.append({"path": name, "sha256": hashlib.sha256(encoded).hexdigest(), "bytes": len(encoded)})
    return {"identity": identity, "files": entries, "input_hash": digest(identity)}


def verify_manifest(files, manifest):
    require(manifest == file_manifest(files, manifest["identity"]), "manifest content drift")


def main():
    package = Path(__file__).resolve().parents[1]
    workbook_path = package / "assets/reconstruction-workbook.json"
    schema_path = package / "assets/semantic-contract.schema.json"
    workbook = json.loads(workbook_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validate_workbook(workbook, schema)
    fields = {field["field_id"]: field for field in workbook["fields"]}
    metrics = {metric["metric_id"]: metric for metric in workbook["metrics"]}
    expected = workbook["expected"]
    identity = workbook["identity"]
    rows = workbook["rows"]
    with fixture_connection(workbook) as connection:
        binding = admitted_binding(workbook["query"]["parameter"], {})
        wrapped = "WITH base AS (" + workbook["query"]["parameterized_sql"] + ") SELECT COUNT(*) AS n, SUM(billed_amount) AS total FROM base"
        result = dict(connection.execute(wrapped, binding).fetchone())
        require(result == {"n": expected["closed_rows"], "total": expected["closed_billed"]}, "bound wrapper population changed")
        population_input = {"query_revision": identity["query_revision"], "sql": workbook["query"]["parameterized_sql"], "parameter_schema": workbook["query"]["parameter"], "bindings": binding, "source_policy_revision": "fixture_policy_1"}
        require(digest(population_input) != digest(dict(population_input, bindings={"outcome": "open"})), "binding population identity collapsed")
        require(digest(population_input) != digest(dict(population_input, source_policy_revision="fixture_policy_2")), "source policy identity collapsed")
        expect_rejected("missing values", lambda: connection.execute(wrapped), (sqlite3.Error,))
        unapproved = dict(workbook["query"]["parameter"], approval_id="")
        expect_rejected("unapproved default", lambda: admitted_binding(unapproved, {}))
        expect_rejected("undeclared parameter", lambda: admitted_binding(workbook["query"]["parameter"], {"other": "closed"}))
        expect_rejected("duplicate alias", lambda: checked_aliases(connection.execute("SELECT site_name AS value, zone AS value FROM service_visits")))
        require(len(checked_aliases(connection.execute(workbook["query"]["sql"] + " WHERE 0"))) == len(fields), "empty output names lost")
        expect_rejected("mutation", lambda: connection.execute("DELETE FROM service_visits"), (sqlite3.Error,))
        require(len(connection.execute("SELECT 1 UNION ALL SELECT 2").fetchall()) == 2, "read-only set operation blocked")
        print("PASS S01 SQL bindings, empty/duplicate aliases and read-only fixture guard")

        facts = {name: profile([row[name] for row in rows], field) for name, field in fields.items()}
        require(facts["feedback_score"]["nonnull"] == expected["feedback_nonnull"], "nonnull count mismatch")
        require(facts["feedback_score"]["distinct"] == expected["feedback_distinct"], "distinct count mismatch")
        require(facts["billed_amount"]["distinct"] == facts["started_at"]["distinct"] == expected["rows"], "unique observation lost")
        require(profile([None] * 3, fields["feedback_score"])["distinct"] == 0, "all-null count fabricated")
        empty = profile([], fields["feedback_score"])
        require(empty["distinct"] == 0 and empty["null_fraction"] is None, "empty observation misrepresented")
        require(facts["site_code"]["distinct"] == expected["site_distinct"] and "measure" not in fields["site_code"]["roles"], "numeric identifier became measure")
        print("PASS S02 exact facts, zero/empty/null states and numeric identifier meaning")

        meaning = effective_meaning(workbook["candidate_meaning"], workbook["reviewed_edits"], identity, workbook["review_authority"])
        runtime = consumer_projection(meaning_facets(meaning))
        exported = consumer_projection(meaning_facets(meaning))
        retrieval = f"{meaning['field_id']}: {runtime['description']}; unit {runtime['unit']}; " + "; ".join(runtime["guidance"])
        require(runtime == exported and runtime["description"] == expected["reviewed_description"], "reviewed scalar lost")
        require(runtime["guidance"] == expected["reviewed_guidance"] and runtime["description"] in retrieval, "reviewed array/retrieval lost")
        require(project_scalar({"value": False}, bool) is False, "false lost")
        require(project_scalar({"value": 0}, int) == 0, "zero lost")
        require(project_scalar({"value": None}, str, nullable=True) is None, "explicit null lost")
        expect_rejected("blind unwrap", lambda: project_scalar({"value": {"nested": "object"}}, str))
        stale = copy.deepcopy(workbook["candidate_meaning"])
        stale["generation_id"] = "g0"
        expect_rejected("stale meaning", lambda: effective_meaning(stale, [], identity, workbook["review_authority"]))
        expect_rejected("unadmitted review", lambda: effective_meaning(workbook["candidate_meaning"], workbook["reviewed_edits"], identity, {}))
        print("PASS S03 scalar/array/null projections, reviewed precedence and stale rejection")

        expect_rejected("rate/additive contradiction", lambda: coherent_hint({"unit": "percent", "behavior": "flow", "additive": True}))
        require(coherent_hint({"unit": "percent", "behavior": "flow", "additive": False})["behavior"] == "rate", "normalization failed")
        unknown_metric = dict(metrics["billed_mean"], behavior="unknown")
        expect_rejected("unknown AVG", lambda: admitted_aggregation(fields["billed_amount"], unknown_metric, "avg"))
        bad_identifier_metric = dict(metrics["billed_mean"], field_id="site_code")
        expect_rejected("identifier AVG", lambda: admitted_aggregation(fields["site_code"], bad_identifier_metric, "avg"))
        require(admitted_aggregation(fields["billed_amount"], metrics["billed_mean"], "avg") == "avg", "justified AVG rejected")
        print("PASS S04 coherence and explicitly justified aggregation")

        policy = workbook["value_policy"]
        decisions = {name: value_admission(field, facts[name], policy) for name, field in fields.items()}
        require({name for name, status in decisions.items() if status == "eligible"} == {"site_name", "zone", "outcome"}, "value admission differs")
        ranked = ranked_values(rows, "outcome", policy["max_values"])
        require(dict(ranked) == expected["outcome_frequencies"], "frequency mismatch")
        selected = ranked_values(rows, "site_name", policy["max_values"])
        persisted = selected[:-1]
        require(Fraction(len(persisted), facts["site_name"]["distinct"]) < 1, "partial persistence claimed exhaustive")
        evidence = companions(rows, "site_name", "Birch Point")
        require(evidence["row_frequency"] == 6 and evidence["categoricals"][0]["returned_distinct"] == 2, "companion count confused with frequency")
        text = contextual_text(evidence)
        require("Birch Point" in text and "Harbor" in text and "80" not in text, "contextual text policy changed")
        boundary = dict(facts["outcome"], distinct=policy["max_distinct"], rows=100)
        require(value_admission(fields["outcome"], boundary, policy) == "eligible", "distinct equality rejected")
        require(value_admission(fields["outcome"], dict(boundary, distinct=policy["max_distinct"] + 1), policy) == "distinct_ceiling", "distinct ceiling not enforced")
        print("PASS S05 ordered value admission, actual coverage and conditional companions")

        contract = workbook["embedding_contract"]
        document = encoder_record(contract, "document")
        query = encoder_record(contract, "query")
        require(compatible_encoders(document, query, contract), "compatible asymmetric pair rejected")
        require(document["encoder"] != query["encoder"], "fixture does not exercise distinct roles")
        incompatible = copy.deepcopy(query)
        incompatible["encoder"]["revision"] = "other"
        expect_rejected("same dimension/different recipe", lambda: compatible_encoders(document, incompatible, contract))
        print("PASS S06 encoder-pair identity; no embeddings or providers used")

        long_value = "Birch Point Service Center With Extended Name"
        candidates = [{"candidate_id": "value_1", "field_id": "site_name", "value": long_value, "identity": identity}]
        selection = {"token_id": "token_1", "candidate_id": "value_1", "status": "resolved"}
        resolved = select_candidate("token_1", selection, candidates, identity, {"site_name"})
        require(resolved["value"] == long_value, "long value round-trip lost")
        expect_rejected("wrong field", lambda: select_candidate("token_1", selection, candidates, identity, {"zone"}))
        expect_rejected("ambiguous candidate", lambda: select_candidate("token_1", dict(selection, status="ambiguous"), candidates, identity, {"site_name"}))
        require(select_candidate("token_1", dict(selection, status="unresolved", candidate_id=None), candidates, identity, {"site_name"})["status"] == "unresolved", "corpus miss fabricated resolution")
        project_filter(fields["site_name"], "in", [long_value])
        expect_rejected("empty IN", lambda: project_filter(fields["site_name"], "in", []))
        expect_rejected("BETWEEN arity", lambda: project_filter(fields["billed_amount"], "between", ["10"]))
        authorization = {101}
        analytical = {101, 202}
        admitted_sites = authorization & analytical
        require(admitted_sites == {101} and not authorization & {202}, "analytical predicate widened scope")
        print("PASS S07 candidate identity/no-match, filter arity and authorization intersection")

        groups = workbook["variants"]["mean_groups"]
        require(merge_mean(groups) == 19, "weighted mean mismatch")
        naive = sum(Fraction(group["sum"], group["nonnull_count"]) for group in groups) / len(groups)
        require(naive == 15 and naive != merge_mean(groups), "mean-of-means counterexample lost")
        expect_rejected("missing merge state", lambda: merge_mean([{"mean": 10}]))
        measured = dict(connection.execute("SELECT COUNT(*) AS rows, COUNT(feedback_score) AS nonnull, COUNT(DISTINCT feedback_score) AS distinct_values, MIN(billed_amount) AS minimum, MAX(billed_amount) AS maximum, SUM(billed_amount) AS total FROM service_visits").fetchone())
        require(measured == {"rows": 12, "nonnull": 8, "distinct_values": 3, "minimum": 75, "maximum": 200, "total": expected["total_billed"]}, "SQL aggregate semantics mismatch")
        chunks = [rows[:6], rows[6:]]
        states = [{"identity": identity, "metric_id": "billed", "unit": "USD", "input_grain": "visit", "sum": sum(int(row["billed_amount"]) for row in chunk), "nonnull_count": len(chunk), "min": min(int(row["billed_amount"]) for row in chunk), "max": max(int(row["billed_amount"]) for row in chunk)} for chunk in chunks]
        require(merge_metric_states(states, "min") == 75, "MIN rollup mismatch")
        require(merge_metric_states(states, "max") == 200, "MAX rollup mismatch")
        require(merge_metric_states(states, "sum") == expected["total_billed"], "SUM rollup mismatch")
        require(merge_metric_states(states, "avg") == Fraction(expected["total_billed"], expected["rows"]), "AVG rollup mismatch")
        distinct_groups = workbook["variants"]["overlapping_distinct"]
        require(len(set().union(*map(set, distinct_groups))) == 3 and sum(map(len, distinct_groups)) == 4, "distinct overlap counterexample lost")
        ratio_groups = workbook["variants"]["ratio_groups"]
        ratio = Fraction(sum(item["numerator"] for item in ratio_groups), sum(item["denominator"] for item in ratio_groups))
        require(ratio == Fraction(1, 5), "ratio components mismatch")
        snapshots = workbook["variants"]["snapshot_values"]
        require(max(snapshots, key=lambda item: item["at"])["value"] == 200 and max(item["value"] for item in snapshots) == 300, "MAX mistaken for latest")
        repeated_total = sum(Decimal(row["billed_amount"]) * 2 for row in rows)
        require(repeated_total == expected["total_billed"] * 2, "fanout counterexample missing")
        mixed_units = copy.deepcopy(states)
        mixed_units[1]["unit"] = "EUR"
        expect_rejected("mixed units", lambda: merge_metric_states(mixed_units, "sum"))
        instant = datetime.fromisoformat(rows[0]["started_at"])
        require(instant.date().month == 2 and instant.astimezone(timezone.utc).date().month == 3, "timezone bucket counterexample lost")
        inclusive = date(2026, 3, 6)
        exclusive = inclusive + timedelta(days=1)
        require(inclusive < exclusive and date(2026, 3, 6) < exclusive, "inclusive date endpoint lost")
        print("PASS S08 weighted/count/extrema/ratio/snapshot/fanout/unit/time algebra")

        records = [{"identity": identity, "field_id": name, "payload": {"meaning": field["meaning"]}} for name, field in fields.items()]
        require(len(joined_artifacts(records, identity)) == len(fields), "catalog lost fields")
        mixed = copy.deepcopy(records)
        mixed[0]["identity"]["generation_id"] = "g0"
        expect_rejected("mixed generation", lambda: joined_artifacts(mixed, identity))
        require(cache_key(identity, meaning["effective_revision"], "v1") == cache_key(dict(identity), meaning["effective_revision"], "v1"), "cache get/set identity mismatch")
        cursor = connection.execute("SELECT strftime('%Y-%m', started_at) AS x, SUM(billed_amount) AS y, COUNT(*) AS y2, zone AS series FROM service_visits WHERE outcome = :outcome GROUP BY x, series ORDER BY x, series", binding)
        require(checked_aliases(cursor) == ["x", "y", "y2", "series"], "result aliases changed")
        chart_rows = [dict(row) for row in cursor.fetchall()]
        require({row["series"]: row["y"] for row in chart_rows} == expected["closed_by_zone"], "consumer arithmetic mismatch")
        require(sum(row["y2"] for row in chart_rows) == expected["closed_rows"] and {row["x"] for row in chart_rows} == {"2026-03"}, "count/month delivery mismatch")
        labels = {"x": "Visit month", "y": "Billed amount", "y2": "Visits", "series": "Zone"}
        require(set(labels) == set(chart_rows[0]) and labels["y"] != "y", "display labels replaced aliases")
        require(metrics["billed_total"]["unit"] != metrics["visit_count"]["unit"], "second metric lost independent unit")
        bindings = {role: {"alias": role, "label": label} for role, label in labels.items()}
        bindings["y"]["metric_id"] = "billed_total"
        bindings["y2"]["metric_id"] = "visit_count"
        payload = project_consumer_payload(chart_rows, bindings, metrics, identity)
        validate_consumer_payload(payload, bindings, metrics, identity)
        missing_units = copy.deepcopy(payload)
        for role in ("y", "y2"):
            del missing_units["bindings"][role]["unit"]
        expect_rejected("consumer omitted axis units", lambda: validate_consumer_payload(missing_units, bindings, metrics, identity))
        for attribute in ("unit", "alias", "label", "metric_id"):
            swapped = copy.deepcopy(payload)
            swapped["bindings"]["y"][attribute], swapped["bindings"]["y2"][attribute] = swapped["bindings"]["y2"][attribute], swapped["bindings"]["y"][attribute]
            expect_rejected(f"consumer swapped {attribute}", lambda: validate_consumer_payload(swapped, bindings, metrics, identity))
        missing_label = copy.deepcopy(payload)
        del missing_label["bindings"]["y2"]["label"]
        expect_rejected("consumer omitted label", lambda: validate_consumer_payload(missing_label, bindings, metrics, identity))
        print("PASS S09 one-generation catalog/cache and validated alias/label/unit payload delivery")

        next_identity = dict(identity, generation_id="g2")
        current_claim = {"job_id": "job_demo", "generation_id": "g2", "attempt": 2, "holder": "worker_b", "input_hash": digest(next_identity), "state": "running", "delivery": "acknowledged"}
        artifacts = [{"identity": next_identity, "field_id": name, "payload": {}, "status": "ready"} for name in fields]
        previous = {"generation_id": "g1"}
        expect_rejected("partial generation", lambda: publish(previous, fields, artifacts[:-1], next_identity, current_claim, current_claim, [], []))
        require(previous == {"generation_id": "g1"}, "failed publication mutated old pointer")
        expect_rejected("stale callback", lambda: publish(previous, fields, artifacts, next_identity, dict(current_claim, attempt=1, holder="worker_a"), current_claim, [], []))
        expect_rejected("cancel requested", lambda: publish(previous, fields, artifacts, next_identity, dict(current_claim, state="cancel_requested"), current_claim, [], []))
        expect_rejected("delivery unknown", lambda: publish(previous, fields, artifacts, next_identity, dict(current_claim, delivery="unknown"), current_claim, [], []))
        expect_rejected("required vector pending", lambda: publish(previous, fields, artifacts, next_identity, current_claim, current_claim, ["value_1"], []))
        require(publish(previous, fields, artifacts, next_identity, current_claim, current_claim, [], [])["generation_id"] == "g2", "complete publication failed")
        print("PASS S10 complete coverage, old-generation protection and attempt fencing")

        definition = {"status": "reviewed", "grain_keys": workbook["query"]["grain_keys"]}
        require_reviewed_rule("preaggregate", definition, fields)
        expect_rejected("missing projected grain", lambda: require_reviewed_rule("preaggregate", definition, set(fields) - {"visit_id"}))
        component_registry = {name: {"status": "reviewed", "fields": ["visit_id"]} for name in ("closed_visits", "all_visits")}
        require_reviewed_rule("ratio", {"status": "reviewed", "components": ["closed_visits", "all_visits"]}, fields, component_registry)
        expect_rejected("unknown ratio component", lambda: require_reviewed_rule("ratio", {"status": "reviewed", "components": ["unknown_visits", "all_visits"]}, fields, component_registry))
        expect_rejected("same ratio components", lambda: require_reviewed_rule("ratio", {"status": "reviewed", "components": ["visits", "visits"]}, fields))
        snapshot_definition = {"status": "reviewed", "aggregation": "latest", "entity_keys": ["site_code"], "time_field": "started_at", "time_order": "descending", "tie_breakers": [{"field_id": "visit_id", "direction": "descending"}]}
        require_reviewed_rule("snapshot", snapshot_definition, fields)
        expect_rejected("snapshot outside footprint", lambda: require_reviewed_rule("snapshot", dict(snapshot_definition, time_field="unknown_time"), fields))
        expect_rejected("snapshot original incomplete declaration", lambda: require_reviewed_rule("snapshot", {"status": "reviewed", "aggregation": "latest", "time_field": "started_at"}, {"started_at"}))
        for prerequisite in ("entity_keys", "time_order", "tie_breakers"):
            incomplete = copy.deepcopy(snapshot_definition)
            del incomplete[prerequisite]
            expect_rejected(f"snapshot missing {prerequisite}", lambda: require_reviewed_rule("snapshot", incomplete, fields))
        expect_rejected("snapshot empty entity key", lambda: require_reviewed_rule("snapshot", dict(snapshot_definition, entity_keys=[]), fields))
        expect_rejected("snapshot unknown entity key", lambda: require_reviewed_rule("snapshot", dict(snapshot_definition, entity_keys=["unknown_key"]), fields))
        expect_rejected("snapshot wrong time order", lambda: require_reviewed_rule("snapshot", dict(snapshot_definition, time_order="ascending"), fields))
        expect_rejected("snapshot empty tie rule", lambda: require_reviewed_rule("snapshot", dict(snapshot_definition, tie_breakers=[]), fields))
        expect_rejected("snapshot unknown tie field", lambda: require_reviewed_rule("snapshot", dict(snapshot_definition, tie_breakers=[{"field_id": "unknown_key", "direction": "descending"}]), fields))
        expect_rejected("snapshot ineffective tie field", lambda: require_reviewed_rule("snapshot", dict(snapshot_definition, tie_breakers=[{"field_id": "started_at", "direction": "descending"}]), fields))
        expect_rejected("snapshot missing tie order", lambda: require_reviewed_rule("snapshot", dict(snapshot_definition, tie_breakers=[{"field_id": "visit_id"}]), fields))
        files = {"overview.md": runtime["description"], "query.sql": workbook["query"]["sql"]}
        manifest = file_manifest(files, identity)
        require(manifest == file_manifest(dict(reversed(list(files.items()))), identity), "manifest ordering drift")
        verify_manifest(files, manifest)
        expect_rejected("manifest drift", lambda: verify_manifest(dict(files, **{"overview.md": "changed"}), manifest))
        expect_rejected("manifest escape", lambda: file_manifest({"../outside": "x"}, identity))
        bridges = {"knowledge": True, "durable": True, "serving": False, "publication": False}
        disposition = "review_required" if all(bridges.values()) else "unavailable"
        require(disposition == "unavailable", "missing bridge advertised served")
        print("PASS S11 reviewed compilation prerequisites, manifests and missing-bridge refusal")

    require(workbook_path.resolve().is_relative_to(package) and schema_path.resolve().is_relative_to(package), "package resource escape")
    require(schema["$schema"] == "https://json-schema.org/draft/2020-12/schema", "unexpected schema dialect")
    print("PASS S12 package-relative standard-library fixture execution")
    print("PASS: 12 controlled seam groups; no production, model-quality or performance claim")


if __name__ == "__main__":
    main()
