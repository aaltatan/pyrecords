# pyrecords

Read records (`list[dict]`) from Excel or JSON, then order, filter and group them. Extracted
from [templify](https://github.com/aaltatan/templify) so other CLIs can share it.

```bash
uv add pyrecords
```

```python
from pathlib import Path
from pyrecords import OrderByKey, filter_data, get_compiler, group_by_data, order_by_data, readers

data = readers["xlsx"](Path("people.xlsx"))  # first row = column names

data = order_by_data(data, [OrderByKey("city"), OrderByKey("-age")])  # "-" = descending

data = filter_data(data, get_compiler(), {"name": "int__gt", "args": ["age", "30"]})

groups = group_by_data(data, ["city"])  # [{"city": "Homs", "items": [...]}, ...]
```

| Module | What it does |
| --- | --- |
| `readers` | `readers` (`xlsx`, `json` → list of records) and `object_readers` (`json` → one record), picked by extension |
| `transformers` | `order_by_data` (via [pyordering](https://github.com/aaltatan/pyordering); empty values last), `filter_data`, `group_by_data` |
| `filter_rules` | `rules`: a [pyspecification](https://github.com/aaltatan/pyspecification) registry of `int__gt`, `string__icontains`, `date__ge`, ... and `get_compiler()` for `all` / `any` filter schemas |

Add a reader for another extension:

```python
@readers.reader("csv")
def read_csv(filepath: Path) -> Data: ...
```
