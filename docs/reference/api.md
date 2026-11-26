# API

## Types

`pyrecords.models`

```python
type DataItem = dict[str, Any]  # one record (a row), column name → value
type Data = list[dict[str, Any]]  # a list of records, as returned by a reader
```

## Readers

`pyrecords.readers`

### `ReaderRegistry[T]`

Maps file extensions (without the dot, case-insensitive) to read functions
`Callable[[Path], T]`.

| Member | Description |
| --- | --- |
| `ReaderRegistry[T]()` | create an empty registry |
| `extension in registry` | whether a reader is registered for `extension` |
| `registry[extension]` | the reader for `extension`; raises `ExtensionNotSupportedError` if none |
| `@registry.reader(extension)` | decorator registering the function as the reader for `extension` |
| `registry.add_reader(fn, extension)` | register `fn` for `extension`, replacing any existing one |

### `readers: ReaderRegistry[Data]`

Readers returning a list of records.

| Extension | Function | Behaviour |
| --- | --- | --- |
| `xlsx` | `read_excel(filepath)` | active sheet; first row = column names; blank rows skipped; formula cells give their cached value. Raises `ValueError` if the workbook has no active sheet. |
| `json` | `read_json(filepath)` | UTF-8 file holding a list of objects. Raises `ValueError` otherwise. |

### `object_readers: ReaderRegistry[DataItem]`

Readers returning a single record.

| Extension | Function | Behaviour |
| --- | --- | --- |
| `json` | `read_json_object(filepath)` | UTF-8 file holding one object. Raises `ValueError` otherwise. |

### `ExtensionNotSupportedError(extension)`

Subclass of `Exception`. Message: `Extension '<extension>' is not supported for being a data file`.

## Transformers

`pyrecords.transformers`

### `OrderByKey(string)`

Dataclass parsed from `"column"` (ascending) or `"-column"` (descending).

| Attribute | Type |
| --- | --- |
| `name` | `str`, the column without the `-` prefix |
| `order` | `Literal["asc", "desc"]` |

### `order_by_data(data, keys) -> Data`

```python
def order_by_data(data: Data, keys: list[OrderByKey]) -> Data
```

Return a new list sorted by `keys`, the first key having the highest priority. `None` values
sort last in both directions. Returns `data` itself when `keys` is empty. Raises `KeyError`
when a key is missing from a record.

### `filter_data(data, compiler, schema) -> Data`

```python
def filter_data(
    data: Data,
    compiler: PredicateCompiler[DataItem, bool],
    schema: ExpressionWrapperDict | PredicateDict,
) -> Data
```

Return the records matching `schema`, a single predicate or an `all` / `any` wrapper
(see [Filter format](filters.md)). `compiler` is usually `get_compiler()`.

### `group_by_data(data, keys, items_key="items") -> Data`

```python
def group_by_data(data: Data, keys: list[str], items_key: str = "items") -> Data
```

Group records sharing the same `keys` values, in first-appearance order. Each group holds
the `keys` values plus its records under `items_key`. Raises `KeyError` (missing key),
`ValueError` (`items_key` in `keys`) or `TypeError` (unhashable key value).

## Filter rules

`pyrecords.filter_rules`

### `rules`

```python
rules = SubscriptableRulesRegistry[dict[str, Any], str, bool](
    operator="logical",
    check_key_existence=True,
)
```

The pyspecification registry holding every [built-in rule](filters.md#rules). `rules.rules`
is the `dict` of rule name → rule. Add rules with `@rules.rule()` (see
[Extending](../guide/extending.md#add-a-filter-rule)).

### `get_compiler() -> PredicateCompiler[dict[str, Any], bool]`

Return a compiler built from the rules registered at call time, resolving `all` / `any`
wrappers by their `operator`. Pass it to `filter_data`, or call `.compile(schema)` yourself
to get a predicate:

```python
from pyrecords import get_compiler

predicate = get_compiler().compile({"name": "is_true", "args": ["active"], "kwargs": {}, "inverse": False})

assert predicate({"active": True}) is True
```
