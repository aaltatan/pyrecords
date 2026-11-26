# Installation

pyrecords needs **Python 3.12 or newer**.

=== "uv"

    ```bash
    uv add pyrecords
    ```

=== "pip"

    ```bash
    pip install pyrecords
    ```

It installs three dependencies:

| Package | Used for |
| --- | --- |
| [openpyxl](https://pypi.org/project/openpyxl/) | reading `.xlsx` workbooks |
| [pyordering](https://pypi.org/project/pyordering/) | sorting by several keys, with empty values last |
| [pyspecification](https://pypi.org/project/pyspecification/) | the filter rules and the JSON filter compiler |

The package is typed (it ships `py.typed`).

## Check it works

```python
from pyrecords import OrderByKey, order_by_data

data = [{"name": "b"}, {"name": "a"}]

assert order_by_data(data, [OrderByKey("name")]) == [{"name": "a"}, {"name": "b"}]
```
