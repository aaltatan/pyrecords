# Recipes

Complete small programs. Each one runs as written.

## A command-line report

Read any supported file, then apply `--order-by`, `--filter` (a JSON file) and
`--group-by` options, the way a templating CLI would.

```python
import json
from pathlib import Path

from pyrecords import (
    Data,
    ExtensionNotSupportedError,
    OrderByKey,
    filter_data,
    get_compiler,
    group_by_data,
    order_by_data,
    readers,
)


def load(
    path: Path,
    order_by: str | None = None,
    filter_path: Path | None = None,
    group_by: str | None = None,
) -> Data:
    extension = path.suffix.removeprefix(".")

    if extension not in readers:
        raise ExtensionNotSupportedError(extension)

    data = readers[extension](path)

    if order_by:
        data = order_by_data(data, [OrderByKey(part) for part in order_by.split(",")])

    if filter_path:
        schema = json.loads(filter_path.read_text(encoding="utf-8"))
        data = filter_data(data, get_compiler(), schema)

    if group_by:
        data = group_by_data(data, group_by.split(","))

    return data


Path("staff.json").write_text(
    json.dumps(
        [
            {"name": "Rama", "department": "Sales", "salary": 1200},
            {"name": "Omar", "department": "IT", "salary": 1800},
            {"name": "Rawaa", "department": "Sales", "salary": 1500},
            {"name": "Abdullah", "department": "IT", "salary": 900},
        ]
    ),
    encoding="utf-8",
)

Path("filter.json").write_text(
    json.dumps({"name": "int__ge", "args": ["salary", "1000"], "kwargs": {}, "inverse": False}),
    encoding="utf-8",
)

report = load(Path("staff.json"), order_by="-salary", filter_path=Path("filter.json"), group_by="department")

assert [(g["department"], [e["name"] for e in g["items"]]) for g in report] == [
    ("IT", ["Omar"]),
    ("Sales", ["Rawaa", "Rama"]),
]
```

## Search box: match any of several columns

Build an `any` filter from a search term typed by a user.

```python
from pyrecords import filter_data, get_compiler


def search(data: Data, term: str, columns: list[str]) -> Data:
    schema = {
        "operator": "any",
        "expressions": [
            {"name": "string__icontains", "args": [column, term], "kwargs": {}, "inverse": False}
            for column in columns
        ],
    }

    return filter_data(data, get_compiler(), schema)


contacts = [
    {"name": "Rama Haddad", "email": "rama@example.com"},
    {"name": "Omar Saleh", "email": "o.saleh@example.com"},
]

assert search(contacts, "SALEH", ["name", "email"]) == [contacts[1]]
```

## Excel rows hired this year, grouped by branch

Excel gives `datetime` cells; `date__*` rules compare the day only.

```python
from datetime import datetime

import openpyxl

wb = openpyxl.Workbook()
sheet = wb.active
sheet.append(["name", "branch", "hired"])
sheet.append(["Rama", "Homs", datetime(2026, 2, 1)])
sheet.append(["Omar", "Damascus", datetime(2024, 6, 10)])
sheet.append(["Rawaa", "Homs", datetime(2026, 7, 20, 14, 0)])
wb.save("hires.xlsx")

hires = readers["xlsx"](Path("hires.xlsx"))

this_year = {"name": "date__ge", "args": ["hired", "2026-01-01"], "kwargs": {}, "inverse": False}

by_branch = group_by_data(filter_data(hires, get_compiler(), this_year), ["branch"])

assert [(g["branch"], len(g["items"])) for g in by_branch] == [("Homs", 2)]
```

## One output per group

Group records, then hand each group to whatever renders a document (here, plain text).

```python
orders = [
    {"customer": "Rama", "item": "Lamp", "qty": 2},
    {"customer": "Omar", "item": "Cable", "qty": 5},
    {"customer": "Rama", "item": "Bulb", "qty": 10},
]

invoices = {
    group["customer"]: "\n".join(f"{line['qty']} x {line['item']}" for line in group["lines"])
    for group in group_by_data(orders, ["customer"], items_key="lines")
}

assert invoices == {"Rama": "2 x Lamp\n10 x Bulb", "Omar": "5 x Cable"}
```

## Shared values for a template

Use `object_readers` for one JSON object (company details, report title) next to the rows.

```python
from pyrecords import object_readers

Path("context.json").write_text(json.dumps({"company": "Tawazon", "year": 2026}), encoding="utf-8")

context = {**object_readers["json"](Path("context.json")), "rows": readers["json"](Path("staff.json"))}

assert context["company"] == "Tawazon"
assert len(context["rows"]) == 4
```
