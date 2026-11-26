# pyrecords

**Read records from Excel or JSON, then order, filter and group them.**

A record is a plain `dict` (one row), and a data set is a `list` of them. pyrecords reads
those lists from `.xlsx` and `.json` files, sorts them by columns, keeps the rows matching a
filter written as JSON, and groups rows that share column values. It was extracted from
[templify](https://github.com/aaltatan/templify) so other command-line tools can share it.

## A first taste

```python
import json
from pathlib import Path

from pyrecords import OrderByKey, filter_data, get_compiler, group_by_data, order_by_data, readers

Path("people.json").write_text(
    json.dumps(
        [
            {"name": "Rama", "city": "Homs", "age": 28},
            {"name": "Omar", "city": "Damascus", "age": 41},
            {"name": "Rawaa", "city": "Homs", "age": 35},
            {"name": "Abdullah", "city": "Damascus", "age": 30},
        ]
    ),
    encoding="utf-8",
)

data = readers["json"](Path("people.json"))

data = order_by_data(data, [OrderByKey("city"), OrderByKey("-age")])  # "-" = descending

over_30 = {"name": "int__gt", "args": ["age", 30], "kwargs": {}, "inverse": False}
data = filter_data(data, get_compiler(), over_30)

groups = group_by_data(data, ["city"])

assert groups == [
    {"city": "Damascus", "items": [{"name": "Omar", "city": "Damascus", "age": 41}]},
    {"city": "Homs", "items": [{"name": "Rawaa", "city": "Homs", "age": 35}]},
]
```

Every step takes a list of records and returns a new one, so you can chain them in any
order. The filter is plain data: it can come from a config file, a command-line option or
a database column.

## What is inside

| Module | What it does |
| --- | --- |
| `readers` | `readers` (`xlsx`, `json` → list of records) and `object_readers` (`json` → one record), picked by file extension |
| `transformers` | `order_by_data` (via [pyordering](https://github.com/aaltatan/pyordering), empty values last), `filter_data`, `group_by_data` |
| `filter_rules` | `rules`: a [pyspecification](https://github.com/aaltatan/pyspecification) registry of `int__gt`, `string__icontains`, `date__ge`, ... and `get_compiler()` for `all` / `any` filters |

## Where it fits

- **Command-line tools** that render templates, reports or documents from a spreadsheet.
- **Mail merges and bulk generation**: one output per row, or per group of rows.
- **Small data jobs** where pandas is too heavy and the data fits in memory.
- **User-defined filters**: let users write `{"name": "string__icontains", ...}` instead
  of Python.

## Where to next

<div class="grid cards" markdown>

- [**Installation**](install.md): one command.
- [**User guide**](guide/index.md): reading, ordering, filtering, grouping, extending.
- [**Recipes**](recipes.md): complete small programs.
- [**Filter format and rules**](reference/filters.md): the JSON shapes and every rule.

</div>
