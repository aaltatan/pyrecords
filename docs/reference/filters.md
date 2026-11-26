# Filter format and rules

A filter is JSON (or the equivalent Python dict) in one of two shapes, defined by
[pyspecification](https://github.com/aaltatan/pyspecification).

## Predicate

One rule. All four keys are required.

```json
{"name": "int__gt", "args": ["age", "30"], "kwargs": {}, "inverse": false}
```

| Key | Type | Meaning |
| --- | --- | --- |
| `name` | string | a rule name from the [table below](#rules) |
| `args` | array | the column (`key`) first, then the rule's values |
| `kwargs` | object | arguments by name (`key`, `value`, `pattern`) |
| `inverse` | boolean | `true` negates the rule |

## Expression wrapper

Combines predicates or other wrappers.

```json
{
  "operator": "all",
  "expressions": [
    {"name": "string__eq", "args": ["city", "Homs"], "kwargs": {}, "inverse": false},
    {
      "operator": "any",
      "expressions": [
        {"name": "int__lt", "args": ["age", 25], "kwargs": {}, "inverse": false},
        {"name": "is_true", "args": ["manager"], "kwargs": {}, "inverse": false}
      ]
    }
  ]
}
```

| Key | Type | Meaning |
| --- | --- | --- |
| `operator` | `"all"` or `"any"` | `all` = every expression matches, `any` = at least one |
| `expressions` | array | predicates or wrappers |

## Rules

Every rule's first argument is the column, `key`. The **value** column shows the extra
argument and how a value from the JSON is converted before comparing; the record's value is
never converted (except by `date__*`).

### Bool and null

| Rule | Keeps records where |
| --- | --- |
| `is_true(key)` | `key` is `True` (not just truthy) |
| `is_null(key)` | `key` is `None` |

### Numbers

| Rules | Value | Comparison |
| --- | --- | --- |
| `int__eq`, `int__gt`, `int__ge`, `int__lt`, `int__le` | `value`, converted with `int()` | `==`, `>`, `>=`, `<`, `<=` |
| `float__eq`, `float__gt`, `float__ge`, `float__lt`, `float__le` | `value`, converted with `float()` | same |
| `decimal__eq`, `decimal__gt`, `decimal__ge`, `decimal__lt`, `decimal__le` | `value`: string or int → `Decimal` exactly, float → `Decimal` rounded to `0.01` | same |

### Strings

| Rule | Value | Keeps records where |
| --- | --- | --- |
| `string__eq` | `value: str` | `key == value` |
| `string__regex` | `pattern: str` | `re.search(pattern, key)` finds a match |
| `string__contains` | `value: str` | `value in key` |
| `string__icontains` | `value: str` | same, ignoring case |
| `string__is_in` | `value: list[str]` | `key` is in the list |
| `string__iis_in` | `value: list[str]` | same, ignoring case |
| `string__startswith` / `string__istartswith` | `value: str` | `key` starts with `value` (`i`: ignoring case) |
| `string__endswith` / `string__iendswith` | `value: str` | `key` ends with `value` (`i`: ignoring case) |
| `string__length_eq`, `_gt`, `_ge`, `_lt`, `_le` | `value: int` | `len(key)` compared with `value` |

### Dates and times

| Rules | Value | Comparison |
| --- | --- | --- |
| `datetime__eq`, `datetime__gt`, `datetime__ge`, `datetime__lt`, `datetime__le` | ISO string, converted with `datetime.fromisoformat` | full datetime |
| `date__eq`, `date__gt`, `date__ge`, `date__lt`, `date__le` | ISO date or datetime string, day kept | day only; the record's value may be a `date`, `datetime` or ISO string |

### UUIDs

| Rules | Value | Comparison |
| --- | --- | --- |
| `uuid__eq`, `uuid__gt`, `uuid__ge`, `uuid__lt`, `uuid__le` | string, converted with `uuid.UUID` | `==`, `>`, `>=`, `<`, `<=` on `UUID` values |

To list the registered rules at runtime:

```python
from pyrecords import rules

assert "string__icontains" in rules.rules
assert len(rules.rules) >= 47
```
