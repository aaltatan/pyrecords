# Grouping

`group_by_data(data, keys, items_key="items")` groups records sharing the same values for
`keys`. Each group is itself a record: the key values, plus the matching records under
`items_key`.

```python
from pyrecords import group_by_data

employees = [
    {"name": "Abdullah", "city": "Homs", "team": "a"},
    {"name": "Rawaa", "city": "Damascus", "team": "a"},
    {"name": "Rama", "city": "Homs", "team": "b"},
    {"name": "Omar", "city": "Homs", "team": "a"},
]

groups = group_by_data(employees, ["city"])

assert [g["city"] for g in groups] == ["Homs", "Damascus"]
assert [e["name"] for e in groups[0]["items"]] == ["Abdullah", "Rama", "Omar"]
assert set(groups[0]) == {"city", "items"}
```

Groups keep their **first-appearance order**, and records inside a group keep their order
too. To control the order, call [`order_by_data`](ordering.md) first.

## Several keys

```python
groups = group_by_data(employees, ["city", "team"])

assert [(g["city"], g["team"], len(g["items"])) for g in groups] == [
    ("Homs", "a", 2),
    ("Damascus", "a", 1),
    ("Homs", "b", 1),
]
```

## Rename `items`

Pass `items_key` when a record already has an `items` column, or when your template expects
another name:

```python
groups = group_by_data(employees, ["team"], items_key="members")

assert [m["name"] for m in groups[1]["members"]] == ["Rama"]
```

## Groups are records

The result is a `Data` again, so you can order or filter the groups themselves, or group
the items of each group a second time:

```python
from pyrecords import OrderByKey, order_by_data

by_city = order_by_data(group_by_data(employees, ["city"]), [OrderByKey("city")])

assert [g["city"] for g in by_city] == ["Damascus", "Homs"]
```

## Errors

| When | Raised |
| --- | --- |
| a key is missing from a record | `KeyError` |
| `items_key` is one of `keys` | `ValueError` |
| a key holds an unhashable value, like a list | `TypeError` |

```python
try:
    group_by_data(employees, ["items"])
except ValueError as error:
    assert str(error) == "Items key 'items' can not be one of the group by keys"
```
