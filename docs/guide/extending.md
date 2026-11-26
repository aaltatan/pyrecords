# Extending

Both registries are open: you can read new file types and add filter rules. Registration
changes the shared `readers`, `object_readers` and `rules` objects, so do it once at import
time of your own module.

## Add a reader

Decorate a function taking a `Path` with `readers.reader(extension)`:

```python
import csv
from pathlib import Path

from pyrecords import Data, readers


@readers.reader("csv")
def read_csv(filepath: Path) -> Data:
    with filepath.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


Path("people.csv").write_text("name,city\nRama,Homs\n", encoding="utf-8")

assert readers["CSV"](Path("people.csv")) == [{"name": "Rama", "city": "Homs"}]
```

Or register an existing function with `add_reader(fn, extension)`. Both replace any reader
already registered for that extension, so you can also override `xlsx` or `json`:

```python
readers.add_reader(read_csv, "tsv-as-csv")

assert "tsv-as-csv" in readers
```

Single-record readers work the same way on `object_readers`:

```python
import tomllib

from pyrecords import DataItem, object_readers


@object_readers.reader("toml")
def read_toml(filepath: Path) -> DataItem:
    with filepath.open("rb") as f:
        return tomllib.load(f)
```

### Your own registry

`ReaderRegistry` is generic in what a reader returns. Create one when you need readers that
are not shared with the rest of the program:

```python
from pyrecords import ReaderRegistry

text_readers = ReaderRegistry[str]()


@text_readers.reader("txt")
def read_text(filepath: Path) -> str:
    return filepath.read_text(encoding="utf-8")
```

## Add a filter rule

`rules` is a pyspecification `SubscriptableRulesRegistry`. A rule takes the record, the
column `key`, then its own values, and returns a `bool`. The registry checks that the key
exists before calling your rule.

```python
from typing import Any

from pyrecords import filter_data, get_compiler, rules


@rules.rule()
def int__between(d: dict[str, Any], key: str, low: int, high: int) -> bool:
    """Keep records where `key` is between `low` and `high`, inclusive."""
    return low <= d[key] <= high


data = [{"age": 25}, {"age": 45}]

schema = {"name": "int__between", "args": ["age", 20, 30], "kwargs": {}, "inverse": False}

assert filter_data(data, get_compiler(), schema) == [{"age": 25}]
```

Call `get_compiler()` **after** registering: it builds the compiler from the rules
registered at that moment.

To convert string values from the filter JSON, annotate the parameter with a
pyspecification `Process` marker, the way the built-in rules do:

```python
from typing import Annotated

from pyspecification import Process


@rules.rule()
def int__divisible_by(d: dict[str, Any], key: str, value: Annotated[int, Process(int)]) -> bool:
    """Keep records where `key` is divisible by `value`."""
    return d[key] % value == 0


schema = {"name": "int__divisible_by", "args": ["age", "5"], "kwargs": {}, "inverse": False}

assert filter_data(data, get_compiler(), schema) == [{"age": 25}, {"age": 45}]
```

`rules.rule()` also takes `name=`, `description=`, `hidden=` and more; see the
[pyspecification](https://github.com/aaltatan/pyspecification) documentation.
