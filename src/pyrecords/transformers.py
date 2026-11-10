"""Data transformers: order, filter and group by."""

import operator
from dataclasses import InitVar, dataclass, field
from functools import reduce
from typing import Any, Literal

from pyordering import key as sort_key
from pyspecification import ExpressionWrapperDict, PredicateCompiler, PredicateDict

from .models import Data, DataItem

# -----------------------
# order
# -----------------------


@dataclass
class OrderByKey:
    """A column to order by, parsed from `"column"` (ascending) or `"-column"` (descending).

    Example:
    ```python
    OrderByKey("-salary")  # OrderByKey(name="salary", order="desc")
    ```

    """

    string: InitVar[str]

    name: str = field(init=False)
    order: Literal["asc", "desc"] = field(init=False)

    def __post_init__(self, key_string: str) -> None:
        self.name = key_string.removeprefix("-")
        self.order = "desc" if key_string.startswith("-") else "asc"


def order_by_data(data: Data, keys: list[OrderByKey]) -> Data:
    """Return `data` sorted by `keys`, the first key having the highest priority.

    Empty values (`None`) sort last, in both directions.

    Raises:
        KeyError: A key is missing from a record.

    """
    if not keys:
        return data

    ordering = reduce(
        operator.rshift,
        (~_column(k.name) if k.order == "desc" else _column(k.name) for k in keys),
    )

    return ordering(data)


@sort_key
def _column(item: DataItem, name: str) -> Any:
    return _get_value(item, name)


def _get_value(item: DataItem, key: str) -> Any:
    if key not in item:
        msg = f"Key '{key}' not found in data, Available keys: {', '.join(item.keys())}"
        raise KeyError(msg)

    return item[key]


# -----------------------
# filter
# -----------------------


def filter_data(
    data: Data,
    compiler: PredicateCompiler[DataItem, bool],
    schema: ExpressionWrapperDict | PredicateDict,
) -> Data:
    """Return the records of `data` matching the filter `schema`.

    Args:
        data: The records to filter.
        compiler: Compiles `schema` into a predicate using the filter rules.
        schema: A single rule (`PredicateDict`), or rules combined with
            `all` / `any` (`ExpressionWrapperDict`).

    """
    predicate = compiler.compile(schema)
    return [row for row in data if predicate(row)]


# -----------------------
# group by
# -----------------------


def group_by_data(data: Data, keys: list[str], items_key: str = "items") -> Data:
    """Group rows sharing the same `keys` values, keeping their first-appearance order.

    Each group is a row holding the `keys` values plus its rows under `items_key`:

    [{"city": "Homs", "items": [{"name": "Rama", "city": "Homs"}, ...]}, ...]

    Raises:
        KeyError: A key is missing from a record.
        ValueError: `items_key` is one of `keys`.
        TypeError: A key holds an unhashable value, like a list.

    """
    if items_key in keys:
        msg = f"Items key '{items_key}' can not be one of the group by keys"
        raise ValueError(msg)

    groups: dict[tuple[Any, ...], DataItem] = {}

    for item in data:
        values = tuple(_get_value(item, key) for key in keys)

        if values not in groups:
            groups[values] = {**dict(zip(keys, values, strict=True)), items_key: []}

        groups[values][items_key].append(item)

    return list(groups.values())
