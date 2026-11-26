# Exceptions

pyrecords defines one exception of its own and otherwise raises built-in exceptions or
those of [pyspecification](https://github.com/aaltatan/pyspecification).

## `ExtensionNotSupportedError`

```python
from pyrecords import ExtensionNotSupportedError
```

Subclass of `Exception`, raised by `registry[extension]` when no reader is registered for
`extension`.

```python
from pyrecords import readers

try:
    readers["csv"]
except ExtensionNotSupportedError as error:
    assert str(error) == "Extension 'csv' is not supported for being a data file"
```

## By function

| Function | Exception | When |
| --- | --- | --- |
| `readers[ext]`, `object_readers[ext]` | `ExtensionNotSupportedError` | no reader for `ext` |
| `readers["xlsx"](path)` | `ValueError` | the workbook has no active sheet |
| `readers["json"](path)` | `ValueError` | not a list of objects (or invalid JSON, `json.JSONDecodeError`, a `ValueError` subclass) |
| `object_readers["json"](path)` | `ValueError` | not an object (or invalid JSON) |
| any reader | `OSError` (`FileNotFoundError`, ...) | the file can not be opened |
| `order_by_data` | `KeyError` | a key is missing from a record |
| `order_by_data` | `TypeError` | a column mixes values that can not be compared |
| `group_by_data` | `KeyError` | a key is missing from a record |
| `group_by_data` | `ValueError` | `items_key` is one of the keys |
| `group_by_data` | `TypeError` | a key holds an unhashable value |
| `filter_data` | `TypeError` | the schema is neither a predicate nor a wrapper |
| `filter_data` | `pyspecification.RuleDoesNotExistError` | unknown rule name |
| `filter_data` | `pyspecification.ProcessArgumentError` | a filter value can not be converted (`"five"` for `int__eq`) |
| `filter_data` | `pyspecification.RuleKeyDoesNotExistError` | the column is missing from a record |
| `filter_data` | `TypeError` | the column holds a value the rule can not compare, like `None` for `int__gt` |

All pyspecification exceptions derive from `pyspecification.PySpecificationError`:

```python
from pyspecification import PySpecificationError

from pyrecords import filter_data, get_compiler

try:
    filter_data([], get_compiler(), {"name": "nope", "args": [], "kwargs": {}, "inverse": False})
except PySpecificationError as error:
    assert str(error).startswith("Rule 'nope' does not exist.")
```
