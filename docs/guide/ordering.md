# Ordering

`order_by_data(data, keys)` returns the records sorted by a list of `OrderByKey`. The first
key has the highest priority; later keys break ties.

```python
from pyrecords import OrderByKey, order_by_data

data = [
    {"name": "Rama", "city": "Homs", "age": 28},
    {"name": "Omar", "city": "Damascus", "age": 41},
    {"name": "Rawaa", "city": "Homs", "age": 35},
]

ordered = order_by_data(data, [OrderByKey("city"), OrderByKey("-age")])

assert [row["name"] for row in ordered] == ["Omar", "Rawaa", "Rama"]
```

## `OrderByKey`

`OrderByKey` parses the same string a user would type on a command line: `"column"` is
ascending, `"-column"` is descending.

```python
key = OrderByKey("-age")

assert (key.name, key.order) == ("age", "desc")
assert (OrderByKey("age").name, OrderByKey("age").order) == ("age", "asc")
```

Turning a `--order-by city,-age` option into keys is one line:

```python
keys = [OrderByKey(part) for part in "city,-age".split(",")]
```

## Empty values sort last

`None` values go to the end **in both directions**, so blank cells never come first:

```python
data = [{"name": "a", "age": None}, {"name": "b", "age": 2}, {"name": "c", "age": 1}]

assert [r["name"] for r in order_by_data(data, [OrderByKey("age")])] == ["c", "b", "a"]
assert [r["name"] for r in order_by_data(data, [OrderByKey("-age")])] == ["b", "c", "a"]
```

## Details

- With no keys, `order_by_data` returns `data` unchanged.
- The input list is not mutated; a new list is returned.
- A key missing from a record raises `KeyError`, naming the available keys:

```python
try:
    order_by_data([{"name": "Rama"}], [OrderByKey("salary")])
except KeyError as error:
    assert "Key 'salary' not found in data, Available keys: name" in str(error)
```

- Values in one column must be comparable with each other (for example, all numbers or all
  strings), as with Python's `sorted`.
