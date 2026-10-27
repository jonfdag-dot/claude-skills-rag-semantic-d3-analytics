import copy
import hashlib
import json
import math
import sqlite3
from datetime import date, datetime, timezone
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from zoneinfo import ZoneInfo

try:
    from jsonschema import Draft202012Validator, ValidationError
except ImportError as error:
    raise SystemExit('Required verifier dependency missing: jsonschema; no installation was attempted') from error

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = json.loads((ROOT / 'assets/events.json').read_text())
EXAMPLES = json.loads((ROOT / 'assets/checked-examples.json').read_text())['examples']
SCHEMA = json.loads((ROOT / 'assets/chart-contract.schema.json').read_text())
Draft202012Validator.check_schema(SCHEMA)
VALIDATOR = Draft202012Validator(SCHEMA)
VARIANTS = {
    'line.single': ('single', {'x', 'y'}, ['x']),
    'line.multi': ('long', {'x', 'y', 'series'}, ['x', 'series']),
    'line.dualAxis': ('dual', {'x', 'y', 'y2'}, ['x']),
    'line.stackedArea': ('long', {'x', 'y', 'series'}, ['x', 'series']),
    'bar.standard': ('single', {'x', 'y'}, ['x']),
    'bar.grouped': ('long', {'x', 'y', 'series'}, ['x', 'series']),
    'bar.stacked': ('long', {'x', 'y', 'series'}, ['x', 'series']),
    'bar.race': ('category-time', {'x', 'y', 'time'}, ['time', 'x']),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def equal(actual, expected):
    if isinstance(expected, dict):
        require(isinstance(actual, dict) and actual.keys() == expected.keys(), 'row keys differ')
        for key in expected:
            equal(actual[key], expected[key])
    elif isinstance(expected, list):
        require(isinstance(actual, list) and len(actual) == len(expected), 'row count differs')
        for left, right in zip(actual, expected):
            equal(left, right)
    elif isinstance(expected, (int, float)) and not isinstance(expected, bool):
        require(isinstance(actual, (int, float)) and not isinstance(actual, bool), 'numeric type differs')
        if isinstance(actual, int) or isinstance(expected, int):
            require(actual == expected, f'{actual} != {expected}')
        else:
            require(math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12), f'{actual} != {expected}')
    else:
        require(actual == expected, f'{actual!r} != {expected!r}')


def validate_contract(contract):
    VALIDATOR.validate(contract)
    shape, roles, grain = VARIANTS[contract['capability']]
    require(contract['shape'] == shape and set(contract['roles']) == roles, 'R06 shape/roles')
    aliases = [binding['alias'] for binding in contract['roles'].values()]
    require(len(set(aliases)) == len(aliases), 'R07 duplicate role aliases')
    require(contract['resultGrain'] == [contract['roles'][r]['alias'] for r in grain], 'R06 grain')
    require(contract['source']['id'] == FIXTURE['sourceId'], 'R01 source ID')
    require(contract['source']['relation'] == 'events' and contract['source']['snapshot'] == FIXTURE['snapshot'], 'R01 source identity')
    require(contract['source']['rowGrain'] == ['event_id'], 'R03 source grain')
    expected_x_type = 'temporal' if contract['capability'].startswith('line.') else 'category'
    require(contract['roles']['x']['type'] == expected_x_type, 'R06 x type')
    used_metrics = set()
    for role, binding in contract['roles'].items():
        if role in {'y', 'y2'}:
            require(binding['type'] == 'number' and binding['ref'] in contract['metrics'], 'R02 metric binding')
            used_metrics.add(binding['ref'])
        else:
            require(binding['ref'] in FIXTURE['fields'], 'R01 dimension')
    require(used_metrics == set(contract['metrics']), 'R02 unused metric')
    for metric in contract['metrics'].values():
        require(set(metric['inputs']) <= set(FIXTURE['fields']), 'R01 metric input')
        operation = metric['operation']
        merge = {'sum': 'sum', 'avg': 'sum-count', 'min': 'min', 'max': 'max', 'count_rows': 'sum', 'count_nonnull': 'sum', 'count_distinct': 'requery', 'ratio': 'ratio-components'}[operation]
        states = {'sum': {'sum', 'count'}, 'avg': {'sum', 'count'}, 'min': {'min'}, 'max': {'max'}, 'count_rows': {'count'}, 'count_nonnull': {'count'}, 'count_distinct': set(), 'ratio': {'numerator', 'denominator'}}[operation]
        require(metric['merge'] == merge and set(metric['state']) == states, 'R09 merge/state')
        require(len(metric['inputs']) == (0 if operation == 'count_rows' else 2 if operation == 'ratio' else 1), 'R02 metric arity')
        require(metric['population'] == 'filtered-events', 'R02 population')
        require(metric['nullPolicy'] == ('include-rows' if operation == 'count_rows' else 'ignore-input-nulls'), 'R09 null policy')
    for predicate in contract['filters']:
        require(predicate['field'] in FIXTURE['fields'], 'R01 filter input')
        require(predicate['parameter'] <= len(contract['parameterTypes']), 'R14 parameter position')
    temporal = [r for r, b in contract['roles'].items() if b['type'] == 'temporal']
    require(bool(temporal) == (contract['time'] is not None), 'R08 time declaration')
    if temporal:
        require(temporal == [contract['time']['role']], 'R08 time role')
        require(contract['time']['sourceField'] == contract['roles'][temporal[0]]['ref'], 'R08 time field')
        require(contract['time']['zone'] == 'UTC' and contract['time']['grain'] == 'day', 'fixture only supports UTC days')
    options = contract['options']
    permitted = {'stackMode', 'labels', 'curveType' if contract['capability'].startswith('line.') else 'orientation'}
    require(set(options) <= permitted, 'R10 option family')
    stacked = contract['capability'] in {'bar.stacked', 'line.stackedArea'}
    require((options['stackMode'] != 'none') == stacked, 'R10 stack option')
    if stacked:
        require(all(m['operation'] in {'sum', 'count_rows', 'count_nonnull'} for m in contract['metrics'].values()), 'R11 non-additive stack')


def validate_result(contract, rows, complete):
    validate_contract(contract)
    require(complete is True, 'R18 incomplete analytical scope')
    columns = {b['alias'] for b in contract['roles'].values()}
    for metric in contract['metrics'].values():
        columns.update(metric['state'].values())
    require(len(rows) <= contract['resultPolicy']['maxRows'], 'R15 rows')
    require(len(rows) * len(columns) <= contract['resultPolicy']['maxCells'], 'R15 cells')
    identities = set()
    for row in rows:
        require(set(row) == columns, 'R16 returned aliases')
        key = tuple(row[alias] for alias in contract['resultGrain'])
        require(key not in identities, 'R17 duplicate grain')
        identities.add(key)
        dimensions = set()
        for role, binding in contract['roles'].items():
            if role in {'y', 'y2'}:
                continue
            alias = binding['alias']
            dimensions.add(alias)
            value = row[alias]
            require(value is not None and not isinstance(value, bool), 'R16 invalid dimension')
            if binding['type'] == 'temporal':
                require(isinstance(value, str), 'R16 timestamp transport')
                instant = datetime.fromisoformat(value.replace('Z', '+00:00'))
                require(instant.tzinfo is not None and instant.utcoffset().total_seconds() == 0, 'R08 timestamp zone')
                require((instant.hour, instant.minute, instant.second, instant.microsecond) == (0, 0, 0, 0), 'R08 day boundary')
        for alias in columns - dimensions:
            value = row[alias]
            require(value is None or (type(value) in {int, float} and math.isfinite(value)), 'R16 invalid numeric')
        for role in {'y', 'y2'} & set(contract['roles']):
            binding = contract['roles'][role]
            metric = contract['metrics'][binding['ref']]
            value = row[binding['alias']]
            state = {k: row[v] for k, v in metric['state'].items()}
            if 'count' in state:
                require(type(state['count']) is int and state['count'] >= 0, 'R17 invalid count state')
            if metric['operation'] == 'avg':
                expected = state['sum'] / state['count'] if state['count'] else None
                equal(value, expected)
            elif metric['operation'] == 'sum':
                require((value is None) == (state['count'] == 0), 'R17 sum null/count')
            elif metric['operation'] == 'ratio':
                factor = 100 if metric['unit'] == 'percent' else 1
                expected = factor * state['numerator'] / state['denominator'] if state['denominator'] else None
                equal(value, expected)
            elif metric['operation'].startswith('count'):
                require(type(value) is int and value >= 0, 'R17 count value')
    require(rows == sorted(rows, key=lambda row: tuple(row[item['alias']] for item in contract['order'])), 'R16 fixture ascending order')


def reject(label, operation):
    try:
        operation()
    except (ValueError, ValidationError):
        print('REJECT', label)
        return
    raise AssertionError('invalid candidate accepted: ' + label)


connection = sqlite3.connect(':memory:')
connection.row_factory = sqlite3.Row
connection.execute('CREATE TABLE events (event_id TEXT PRIMARY KEY, user_id TEXT, ts_utc TEXT, channel TEXT, value REAL, converted INTEGER, eligible INTEGER)')
connection.executemany('INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?)', [tuple(row[k] for k in FIXTURE['fields']) for row in FIXTURE['rows']])
original = json.dumps(EXAMPLES, sort_keys=True)
results = {}
for example in EXAMPLES:
    bindings = {str(index + 1): value for index, value in enumerate(example['params'])}
    rows = [dict(row) for row in connection.execute(example['sql'], bindings)]
    equal(rows, example['expectedRows'])
    validate_result(example['contract'], rows, example['complete'])
    require(example['roleAliasMap'] == {r: b['alias'] for r, b in example['contract']['roles'].items()}, 'R07 roleAliasMap')
    results[example['id']] = rows
    print('QUERY', example['id'], 'PASS', len(rows), 'rows')

avg_rows = results['category-avg']
pooled = sum(r['s_y'] for r in avg_rows) / sum(r['n_y'] for r in avg_rows)
equal(pooled, 40)
require(pooled != sum(r['y'] for r in avg_rows) / len(avg_rows), 'unequal average counterexample missing')
equal(float(Fraction(100 + 90, 10 + 1)), 190 / 11)
print('MATH AVG=40 versus mean-of-means=52.5; 190/11=', float(Fraction(190, 11)))
totals = dict(connection.execute('SELECT COUNT(*) AS rows, COUNT(value) AS nonnull, AVG(value) AS mean, MIN(value) AS minimum, MAX(value) AS maximum, COUNT(DISTINCT user_id) AS users FROM events WHERE ts_utc < ?', ('2026-01-02',)).fetchone())
equal(totals, {'rows': 4, 'nonnull': 3, 'mean': 40, 'minimum': 10, 'maximum': 90, 'users': 3})
require(sum(r['y'] for r in results['category-count_distinct']) == 4 and totals['users'] == 3, 'distinct overlap')
require(len(avg_rows) == 2 and totals['rows'] == 4, 'marks versus rows')
for predicate, expected_counts in [('ts_utc >= ?', (1, 0)), ('ts_utc > ?', (0, 0))]:
    threshold = '2026-01-03' if predicate.startswith('ts_utc >=') else '2027'
    row = tuple(connection.execute('SELECT COUNT(*), COUNT(value), AVG(value), MIN(value), MAX(value), SUM(value) FROM events WHERE ' + predicate, (threshold,)).fetchone())
    require(row == (*expected_counts, None, None, None, None), 'all-null or empty semantics')
require(list(connection.execute('SELECT channel, AVG(value) FROM events WHERE ts_utc > ? GROUP BY channel', ('2027',))) == [], 'empty grouped result')
dual = results['daily-dual']
equal(sum(r['y'] for r in dual if r['n_y']), 270)
pooled_rate = 100 * sum(r['num_y2'] for r in dual) / sum(r['den_y2'] for r in dual)
equal(pooled_rate, 400 / 7)
require(not math.isclose(pooled_rate, (dual[0]['y2'] + dual[1]['y2']) / 2), 'ratio counterexample')
print('MATH counts=4 rows/3 nonnull/3 distinct; rollup SUM=270; rate=', pooled_rate)
filtered = connection.execute('SELECT AVG(value) FROM events WHERE ts_utc < ? AND value >= 20', ('2026-01-02',)).fetchone()[0]
equal(filtered, 55)
require([r['y'] for r in avg_rows if r['y'] >= 20] == [90], 'WHERE versus aggregate filtering')
monthly = [dict(r) for r in connection.execute('SELECT channel AS x, SUM(value) AS y FROM events GROUP BY channel ORDER BY x')]
equal(monthly, [{'x': 'A', 'y': 60}, {'x': 'B', 'y': 210}])
require(sum([0, 20]) / 2 == sum([10, 10]) / 2 and [0, 20] != [10, 10], 'coarse result cannot reconstruct fine values')
left, right = {'a': 120, 'b': 150}, {'b': 4, 'c': 5}
aligned = [{'x': key, 'y': left.get(key), 'y2': right.get(key)} for key in sorted(left.keys() | right.keys())]
equal(aligned, [{'x': 'a', 'y': 120, 'y2': None}, {'x': 'b', 'y': 150, 'y2': 4}, {'x': 'c', 'y': None, 'y2': 5}])
secondary_only = [{'x': '2026-01-01T00:00:00Z', 'y': None, 'n_y': 0, 'y2': 4, 'num_y2': 4, 'den_y2': 100}]
validate_result(EXAMPLES[2]['contract'], secondary_only, True)
require(secondary_only[0]['y2'] == 4, 'independent secondary lost')
require(Decimal('0.00004') != Decimal('0') and int(float(2**53 + 1)) != 2**53 + 1, 'precision boundaries')
equal(9007199254740993, 9007199254740993)
equal(15.0, 15)
equal(1.0 + 1e-13, 1.0)
reject('unequal large integers', lambda: equal(9007199254740992, 9007199254740993))
reject('rounded float for integer expectation', lambda: equal(9007199254740992.0, 9007199254740993))
reject('integer versus rounded float expectation', lambda: equal(9007199254740993, 9007199254740992.0))
zone = ZoneInfo('America/New_York')
for start, end, hours in [('2026-03-08', '2026-03-09', 23), ('2026-11-01', '2026-11-02', 25)]:
    instants = [datetime.fromisoformat(day).replace(tzinfo=zone).astimezone(timezone.utc) for day in [start, end]]
    equal((instants[1] - instants[0]).total_seconds() / 3600, hours)
print('TIME New York calendar days=23h/25h; UTC fixture buckets and half-open filters PASS')
component_observations = {'A': [10, 20], 'B': [30, 20]}
component_baselines = {name: values[0] for name, values in component_observations.items()}
normalize_then_sum = [sum(values[index] / component_baselines[name] for name, values in component_observations.items()) for index in range(2)]
component_totals = [sum(values[index] for values in component_observations.values()) for index in range(2)]
sum_then_index = [value / component_totals[0] for value in component_totals]
equal(normalize_then_sum, [2, 8 / 3])
equal(component_totals, [40, 40])
equal(sum_then_index, [1, 1])
require(normalize_then_sum != sum_then_index, 'normalization and aggregation do not commute')
print('TRANSFORM A=[10,20], B=[30,20], baselines=10/30; normalize-then-sum=', normalize_then_sum, 'versus sum-then-index=', sum_then_index)
require(sum([0, 100, 100]) / 3 != sum([0]) / 1, 'display sample is not population')
changed = copy.deepcopy(avg_rows)
changed[1]['y'] = 91
digest = lambda rows: hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()
require(len(changed) == len(avg_rows) and changed[0] == avg_rows[0] and digest(changed) != digest(avg_rows), 'full revision identity')

def validate_candidate(candidate, golden):
    require(set(candidate) == {'status', 'contract', 'sql', 'params', 'roleAliasMap', 'reasoningSummary', 'changeSummary'}, 'R13 ready fields')
    require(candidate['status'] == 'ready', 'R13 ready status')
    require(all(isinstance(candidate[k], str) and candidate[k] for k in ['sql', 'reasoningSummary', 'changeSummary']), 'R13 text fields')
    validate_contract(candidate['contract'])
    require(candidate['contract'] == golden['contract'], 'R04 frozen contract')
    require(candidate['params'] == golden['params'], 'R14 parameter values')
    require(candidate['roleAliasMap'] == golden['roleAliasMap'], 'R07 candidate mapping')
    require(' '.join(candidate['sql'].split()) == ' '.join(golden['sql'].split()), 'R14 golden SQL mismatch; not a general SQL validator')
    bindings = {str(index + 1): value for index, value in enumerate(candidate['params'])}
    rows = [dict(row) for row in connection.execute(candidate['sql'], bindings)]
    validate_result(candidate['contract'], rows, True)
    equal(rows, golden['expectedRows'])

candidate = json.loads((ROOT / 'assets/prompt-output.json').read_text())
validate_candidate(candidate, EXAMPLES[0])
reject('duplicate grain', lambda: validate_result(EXAMPLES[0]['contract'], avg_rows + avg_rows[:1], True))
reject('incomplete result', lambda: validate_result(EXAMPLES[0]['contract'], avg_rows, False))
for bad in ['', False, float('inf')]:
    invalid_rows = copy.deepcopy(avg_rows)
    invalid_rows[0]['y'] = bad
    reject('invalid numeric ' + repr(bad), lambda: validate_result(EXAMPLES[0]['contract'], invalid_rows, True))
invalid_rows = copy.deepcopy(avg_rows)
invalid_rows[0]['y'] = 105
reject('AVG inconsistent with state', lambda: validate_result(EXAMPLES[0]['contract'], invalid_rows, True))
bad_contract = copy.deepcopy(EXAMPLES[2]['contract'])
bad_contract['roles']['series'] = {'alias': 'series', 'type': 'category', 'ref': 'channel', 'label': 'Channel'}
reject('dual plus series', lambda: validate_contract(bad_contract))
bad_stack = copy.deepcopy(EXAMPLES[0]['contract'])
bad_stack.update(capability='bar.stacked', shape='long', resultGrain=['x', 'series'])
bad_stack['roles']['series'] = {'alias': 'series', 'type': 'category', 'ref': 'user_id', 'label': 'User'}
bad_stack['options']['stackMode'] = 'stacked'
reject('stacked means', lambda: validate_contract(bad_stack))
for field, value in [('sql', candidate['sql'].replace('AVG(value)', 'SUM(value)')), ('roleAliasMap', {'x': 'x', 'y': 'avg_amount'}), ('params', ['2026-01-01', '2026-02-01'])]:
    invalid_candidate = copy.deepcopy(candidate)
    invalid_candidate[field] = value
    reject('candidate ' + field, lambda: validate_candidate(invalid_candidate, EXAMPLES[0]))
unknown_field = copy.deepcopy(candidate['contract'])
unknown_field['unregistered'] = True
reject('unknown contract field', lambda: validate_contract(unknown_field))
FIELD_SCHEMA = json.loads((ROOT / 'assets/field-contract.schema.json').read_text())
FIELD_EXAMPLES = json.loads((ROOT / 'assets/field-examples.json').read_text())
Draft202012Validator.check_schema(FIELD_SCHEMA)
FIELD_VALIDATOR = Draft202012Validator(FIELD_SCHEMA)
PREDICATE_VALIDATOR = Draft202012Validator({'$ref': '#/$defs/predicate', '$defs': FIELD_SCHEMA['$defs']})
field_original = json.dumps(FIELD_EXAMPLES, sort_keys=True)


def validate_field(field):
    FIELD_VALIDATOR.validate(field)
    meaning = field['meaning']
    logical = field['logicalType']
    operations = field['operations']
    temporal = field['temporal']
    categorical = {'entity_identifier', 'nominal_category', 'ordinal_category'}
    if meaning in categorical:
        require(set(operations['aggregate']) <= {'count_rows', 'count_nonnull', 'count_distinct'}, 'field categories are not quantitative aggregates')
        require('measure' not in field['analyticalRoles'], 'identifier/category needs a derived count metric')
    if meaning == 'ordinal_category':
        require(operations['order']['kind'] == 'declared' and len(operations['order']['values']) > 0, 'ordinal requires declared order')
    else:
        require(not operations['order']['values'], 'declared ordinal values have an explicit owner')
    if meaning == 'event_time':
        require(logical == 'timestamp' and temporal is not None and temporal['kind'] == 'instant', 'instant representation')
        require(isinstance(temporal['zone'], str) and temporal['zone'], 'instant zone')
        require(operations['order']['kind'] == 'chronological', 'instant order')
    elif meaning == 'calendar_date':
        require(logical == 'date' and temporal is not None and temporal['kind'] == 'date', 'date representation')
        require(temporal['calendar'] is not None and temporal['zone'] is None, 'date is not automatically an instant')
    elif meaning == 'elapsed_duration':
        require(logical == 'duration' and temporal is not None and temporal['kind'] == 'duration', 'duration representation')
        require(temporal['zone'] is None and temporal['calendar'] is None and field['unit'] == temporal['unit'], 'duration unit without calendar zone')
        require('time_dimension' not in field['analyticalRoles'], 'duration is not event time')
    else:
        require(temporal is None and logical not in {'date', 'timestamp', 'duration'}, 'temporal meaning is explicit')
    if meaning in {'quantity', 'currency_amount', 'ratio'}:
        require(logical in {'integer', 'decimal'} and field['unit'] is not None, 'quantitative type/unit')
    if meaning == 'boolean_flag':
        require(logical in {'integer', 'boolean'}, 'flag representation')
    if not field['nullable']:
        require(field['missingPolicy'] == 'reject', 'non-null field rejects missing input')


def display_kind(field, role, operation=None):
    validate_field(field)
    meaning = field['meaning']
    roles = set(field['analyticalRoles'])
    if role in {'y', 'y2'}:
        require(operation is not None and operation in field['operations']['aggregate'], 'undeclared measure operation')
        require('measure' in roles and meaning not in {'entity_identifier', 'nominal_category', 'ordinal_category', 'free_text'}, 'quantity binding')
        return 'number'
    if role in {'time', 'x'} and meaning in {'event_time', 'calendar_date'}:
        require(bool(roles & {'dimension', 'time_dimension'}), 'temporal dimension role')
        return 'temporal'
    require(role in {'x', 'series'} and bool(roles & {'dimension', 'entity_key'}), 'dimension binding')
    require(meaning in {'entity_identifier', 'nominal_category', 'ordinal_category'} and field['operations']['group'], 'categorical grouping')
    return 'category'


def typed_predicate_value(value, field):
    if value is None:
        require(field['nullable'], 'predicate nullability')
        return value
    logical = field['logicalType']
    if logical in {'integer', 'decimal', 'duration'}:
        require(type(value) in {int, float} and math.isfinite(value), 'typed numeric predicate')
        if logical == 'integer':
            require(type(value) is int, 'integer predicate')
    elif logical == 'boolean':
        require(type(value) is bool, 'boolean predicate')
    elif logical == 'timestamp':
        require(isinstance(value, str), 'timestamp predicate transport')
        instant = datetime.fromisoformat(value.replace('Z', '+00:00'))
        require(instant.tzinfo is not None, 'timestamp predicate zone')
        return instant
    elif logical == 'date':
        require(isinstance(value, str) and len(value) == 10 and value[4] == '-' and value[7] == '-', 'calendar date transport')
        return date.fromisoformat(value)
    else:
        require(isinstance(value, str), 'string predicate')
    return value


def validate_predicate(predicate, fields):
    PREDICATE_VALIDATOR.validate(predicate)
    require(predicate['field'] in fields, 'predicate field')
    field = fields[predicate['field']]
    require(predicate['op'] in field['operations']['filter'], 'predicate capability')
    if predicate['purpose'] == 'authorization':
        require(predicate['authority'] == 'server' and not predicate['editable'], 'authorization predicate is server-owned')
    else:
        require(predicate['authority'] == 'caller', 'analytical predicate authority')
    value = predicate['value']
    operation = predicate['op']
    if operation == 'is_null':
        require(type(value) is bool and field['nullable'], 'is-null predicate')
        return
    if operation in {'in', 'between'}:
        require(isinstance(value, list) and len(value) > 0, 'predicate list')
        values = [typed_predicate_value(item, field) for item in value]
        if operation == 'between':
            require(len(values) == 2 and all(item is not None for item in values) and values[0] <= values[1], 'ordered predicate range')
    else:
        require(not isinstance(value, list), 'scalar predicate')
        typed_predicate_value(value, field)


def matches_scope_fixture(row, predicate):
    require(predicate['field'] == 'channel' and predicate['op'] in {'eq', 'in'}, 'scope fixture operator')
    value = row['channel']
    return value == predicate['value'] if predicate['op'] == 'eq' else value in predicate['value']


fields = {}
for field in FIELD_EXAMPLES['fields']:
    validate_field(field)
    require(field['id'] not in fields, 'unique field identity')
    fields[field['id']] = field
require(set(FIXTURE['fields']) <= set(fields), 'fixture field catalog closure')
for binding in FIELD_EXAMPLES['bindings']:
    equal(display_kind(fields[binding['field']], binding['role'], binding.get('operation')), binding['expectedKind'])
for example in EXAMPLES:
    contract = example['contract']
    for role, binding in contract['roles'].items():
        if role not in {'y', 'y2'}:
            equal(display_kind(fields[binding['ref']], role), binding['type'])
            continue
        metric = contract['metrics'][binding['ref']]
        operation = metric['operation']
        if operation == 'count_rows':
            require(metric['inputs'] == [], 'row count derives from source population')
        elif operation in {'count_nonnull', 'count_distinct'}:
            require(operation in fields[metric['inputs'][0]]['operations']['aggregate'], 'count input eligibility')
        elif operation == 'ratio':
            require(all('sum' in fields[input_id]['operations']['aggregate'] for input_id in metric['inputs']), 'ratio component eligibility')
            require(metric['unit'] in {'fraction', 'percent'}, 'ratio output unit')
        else:
            input_field = fields[metric['inputs'][0]]
            equal(display_kind(input_field, role, operation), binding['type'])
            equal(metric['unit'], input_field['unit'])
        equal(binding['type'], 'number')

for predicate in FIELD_EXAMPLES['predicates']:
    validate_predicate(predicate, fields)
scope = FIELD_EXAMPLES['scope']
trusted_scope = scope['serverPredicate']
validate_predicate(trusted_scope, fields)
for predicate, expected in zip(scope['callerPredicates'], scope['expectedChannels']):
    validate_predicate(predicate, fields)
    channels = sorted({row['channel'] for row in FIXTURE['rows'] if matches_scope_fixture(row, trusted_scope) and matches_scope_fixture(row, predicate)})
    equal(channels, expected)
require(len(scope['callerPredicates']) == len(scope['expectedChannels']), 'scope expectation count')
numeric_identifier = copy.deepcopy(fields['account_code'])
numeric_identifier['operations']['aggregate'].append('avg')
ordinal_without_order = copy.deepcopy(fields['priority'])
ordinal_without_order['operations']['order'] = {'kind': 'lexical', 'values': []}
naive_timestamp = copy.deepcopy(FIELD_EXAMPLES['predicates'][1])
naive_timestamp['value'] = '2026-01-01T00:00:00'
forged_scope = copy.deepcopy(trusted_scope)
forged_scope.update(authority='caller', editable=True)
boolean_measure = {'field': 'value', 'op': 'eq', 'value': True, 'purpose': 'analytical', 'authority': 'caller', 'editable': True}
null_equality = {'field': 'value', 'op': 'eq', 'value': None, 'purpose': 'analytical', 'authority': 'caller', 'editable': True}
field_rejections = [
    ('field numeric identifier AVG', lambda: validate_field(numeric_identifier)),
    ('field ordinal missing order', lambda: validate_field(ordinal_without_order)),
    ('field duration as time', lambda: display_kind(fields['elapsed_seconds'], 'time')),
    ('field identifier as measure', lambda: display_kind(fields['account_code'], 'y', 'avg')),
    ('field timestamp without zone', lambda: validate_predicate(naive_timestamp, fields)),
    ('field caller authorization forgery', lambda: validate_predicate(forged_scope, fields)),
    ('field boolean numeric predicate', lambda: validate_predicate(boolean_measure, fields)),
    ('field null equality predicate', lambda: validate_predicate(null_equality, fields)),
]
for label, operation in field_rejections:
    reject(label, operation)
require(json.dumps(FIELD_EXAMPLES, sort_keys=True) == field_original, 'field fixtures mutated')
weighted_numerator = Decimal('1') * Decimal('10') + Decimal('9') * Decimal('20')
weight_sum = Decimal('1') + Decimal('9')
require(weighted_numerator / weight_sum == Decimal('19') and (Decimal('10') + Decimal('20')) / 2 == Decimal('15'), 'weighted sufficient state')
empty_weight_sum = Decimal('0')
empty_weighted_mean = Decimal('0') / empty_weight_sum if empty_weight_sum else None
require(empty_weighted_mean is None, 'zero-weight mean is unavailable')
equal(min(row['y'] for row in results['category-min']), 10)
equal(max(row['y'] for row in results['category-max']), 90)
values = [10, 20, 30]
equal([value / values[0] for value in values], [1, 2, 3])
equal([100 * (value / values[0] - 1) for value in values], [0, 100, 200])
equal([(value - min(values)) / (max(values) - min(values)) for value in values], [0, 0.5, 1])
mean = sum(values) / len(values)
sample_deviation = math.sqrt(sum((value - mean) ** 2 for value in values) / (len(values) - 1))
equal([(value - mean) / sample_deviation for value in values], [-1, 0, 1])
print('FIELD PASS:', len(fields), 'descriptors;', len(FIELD_EXAMPLES['bindings']), 'bindings;', len(FIELD_EXAMPLES['predicates']), 'typed predicates;', len(field_rejections), 'targeted rejections; nine SQL contracts agree with field metadata; trusted scope intersection preserved')
print('MATH weighted mean=19 versus unweighted=15; MIN/MAX rollups=10/90; indexed/percent/range/sample-zscore examples PASS')

require(json.dumps(EXAMPLES, sort_keys=True) == original, 'fixtures mutated')
connection.close()
print('PASS: 9 SQL examples; contract/schema/alias/grain/state checks; 12 original invalid candidates rejected; arithmetic, filters, rollups, time, precision and independent axes verified')
print('LIMIT: fixture checker only; no arbitrary SQL AST proof, model execution, PostgreSQL server, browser, cleanup or performance measurement')
