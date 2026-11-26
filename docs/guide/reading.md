# Reading files

Two registries map a file extension to a read function:

| Registry | Returns | Extensions |
| --- | --- | --- |
| `readers` | `Data`, a list of records | `xlsx`, `json` |
| `object_readers` | `DataItem`, a single record | `json` |

Look a reader up by extension (without the dot, case-insensitive) and call it with a
`Path`:

```python
import json
from pathlib import Path

from pyrecords import object_readers, readers

Path("people.json").write_text(json.dumps([{"name": "Rama"}]), encoding="utf-8")
Path("company.json").write_text(json.dumps({"company": "Tawazon"}), encoding="utf-8")

assert readers["json"](Path("people.json")) == [{"name": "Rama"}]
assert object_readers["JSON"](Path("company.json")) == {"company": "Tawazon"}
```

Pick the reader from the file name with `Path.suffix`:

```python
path = Path("people.json")

data = readers[path.suffix.removeprefix(".")](path)
```

Check support first with `in`, or catch `ExtensionNotSupportedError`:

```python
from pyrecords import ExtensionNotSupportedError

assert "xlsx" in readers
assert "XLSX" in readers
assert "csv" not in readers

try:
    readers["csv"]
except ExtensionNotSupportedError as error:
    assert str(error) == "Extension 'csv' is not supported for being a data file"
```

## Excel (`xlsx`)

The reader opens the **active sheet** of the workbook:

- the **first row** holds the column names (a number header becomes a `str` key);
- each following row is one record;
- **fully blank rows are skipped**;
- formula cells give their **last calculated value** (the value Excel saved), not the formula.

```python
from datetime import datetime

import openpyxl

wb = openpyxl.Workbook()
sheet = wb.active
sheet.append(["name", "hired", "salary"])
sheet.append(["Rama", datetime(2021, 3, 1), 1200])
sheet.append([None, None, None])  # skipped
sheet.append(["Omar", datetime(2019, 9, 15), 1500])
wb.save("staff.xlsx")

assert readers["xlsx"](Path("staff.xlsx")) == [
    {"name": "Rama", "hired": datetime(2021, 3, 1), "salary": 1200},
    {"name": "Omar", "hired": datetime(2019, 9, 15), "salary": 1500},
]
```

Values keep the types openpyxl gives them: numbers, `str`, `datetime`, `bool`, and `None`
for empty cells.

!!! note "Formulas need a saved value"
    A workbook written by a program (not saved by Excel or LibreOffice) has no cached
    results, so its formula cells read as `None`. Open and save it once in a spreadsheet app.

## JSON (`json`)

Files are read as UTF-8.

- `readers["json"]` expects a **list of objects** and raises `ValueError` otherwise.
- `object_readers["json"]` expects **one object** and raises `ValueError` otherwise.

```python
Path("not-a-list.json").write_text('{"name": "Rama"}', encoding="utf-8")

try:
    readers["json"](Path("not-a-list.json"))
except ValueError as error:
    assert str(error) == "JSON data must be a list of objects"
```

JSON has no date type, so dates stay strings. The `date__*` filter rules accept ISO strings,
see [Filtering](filtering.md#dates).

To read another format, see [Extending](extending.md#add-a-reader).
