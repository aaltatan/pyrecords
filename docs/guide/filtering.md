# Filtering

`filter_data(data, compiler, schema)` keeps the records matching a filter **schema**, a
plain dict you can load from JSON. `get_compiler()` returns the compiler that knows every
built-in rule.

```python
from pyrecords import filter_data, get_compiler

data = [
    {"name": "Rama", "city": "Homs", "age": 28},
    {"name": "Omar", "city": "Damascus", "age": 41},
    {"name": "Rawaa", "city": "Homs", "age": 35},
]

over_30 = {"name": "int__gt", "args": ["age", 30], "kwargs": {}, "inverse": False}

assert [r["name"] for r in filter_data(data, get_compiler(), over_30)] == ["Omar", "Rawaa"]
```

## One rule

A single rule is a **predicate** with four keys, all required:

| Key | Meaning |
| --- | --- |
| `name` | the rule, like `int__gt` or `string__icontains` (see [all rules](../reference/filters.md#rules)) |
| `args` | the column first, then the rule's values |
| `kwargs` | the same arguments by name, usually `{}` |
| `inverse` | `true` keeps the records that do **not** match |

```python
not_homs = {"name": "string__eq", "args": ["city", "Homs"], "kwargs": {}, "inverse": True}

assert [r["name"] for r in filter_data(data, get_compiler(), not_homs)] == ["Omar"]
```

Arguments can also go by name (`key`, `value`, or `pattern` for `string__regex`):

```python
by_name = {"name": "string__icontains", "args": [], "kwargs": {"key": "name", "value": "RA"}, "inverse": False}

assert [r["name"] for r in filter_data(data, get_compiler(), by_name)] == ["Rama", "Rawaa"]
```

## Combine rules with `all` / `any`

Wrap predicates in `{"operator": "all" | "any", "expressions": [...]}`. Wrappers nest, so
you can build any `and` / `or` tree.

```python
young_or_damascus = {
    "operator": "any",
    "expressions": [
        {"name": "int__lt", "args": ["age", 30], "kwargs": {}, "inverse": False},
        {"name": "string__eq", "args": ["city", "Damascus"], "kwargs": {}, "inverse": False},
    ],
}

assert [r["name"] for r in filter_data(data, get_compiler(), young_or_damascus)] == ["Rama", "Omar"]

homs_over_30 = {
    "operator": "all",
    "expressions": [
        {"name": "string__eq", "args": ["city", "Homs"], "kwargs": {}, "inverse": False},
        {"name": "int__gt", "args": ["age", 30], "kwargs": {}, "inverse": False},
    ],
}

assert [r["name"] for r in filter_data(data, get_compiler(), homs_over_30)] == ["Rawaa"]
```

## Values are converted for you

Filter JSON often holds strings (from a command line or a form). The numeric, date, datetime,
decimal and UUID rules convert their value to the rule type before comparing, so
`"30"` works like `30`:

```python
over_30_text = {"name": "int__gt", "args": ["age", "30"], "kwargs": {}, "inverse": False}

assert filter_data(data, get_compiler(), over_30_text) == filter_data(data, get_compiler(), over_30)
```

A value that can not be converted raises `pyspecification.ProcessArgumentError` when the
filter is compiled.

Only the **filter value** is converted, never the record's value: `int__gt` compares the
column as it is, so the column must already hold numbers.

### Decimals

`decimal__*` accepts strings and ints exactly (`"10.50"`, `10`), and rounds floats to cents
(`10.5` → `Decimal("10.50")`). Use it on columns holding `Decimal` values.

### Dates

`date__*` rules compare **the day only**. The filter value is an ISO date or datetime string,
and the record's value may be a `date`, a `datetime` (as Excel cells give) or an ISO string
(as JSON gives):

```python
from datetime import datetime

hires = [
    {"name": "Rama", "hired": datetime(2021, 3, 1, 9, 30)},
    {"name": "Omar", "hired": "2019-09-15"},
]

since_2020 = {"name": "date__ge", "args": ["hired", "2020-01-01"], "kwargs": {}, "inverse": False}

assert [r["name"] for r in filter_data(hires, get_compiler(), since_2020)] == ["Rama"]
```

`datetime__*` rules compare full datetimes and do no conversion of the record's value.

## Errors

| When | Raised |
| --- | --- |
| unknown rule `name` | `pyspecification.RuleDoesNotExistError` (lists the available rules) |
| schema of the wrong shape | `TypeError` (shows the expected JSON schemas) |
| filter value can not be converted | `pyspecification.ProcessArgumentError` |
| the column is missing from a record | `pyspecification.RuleKeyDoesNotExistError` |

```python
from pyspecification import RuleKeyDoesNotExistError

salary_filter = {"name": "int__gt", "args": ["salary", 1000], "kwargs": {}, "inverse": False}

try:
    filter_data(data, get_compiler(), salary_filter)
except RuleKeyDoesNotExistError as error:
    assert str(error) == "Key 'salary' does not exist in the object of rule 'int__gt'"
```

## Validate filters with JSON Schema

pyspecification can describe every rule as JSON Schema, useful to validate a filter file or
to drive a filter editor:

```python
from pyspecification import get_expression_json_schema

from pyrecords import rules

schema = get_expression_json_schema(rules.rules)

assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
```
