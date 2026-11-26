# Reference

| Page | Contents |
| --- | --- |
| [API](api.md) | every public name exported by `pyrecords` |
| [Filter format and rules](filters.md) | the filter JSON shapes and the table of built-in rules |
| [Exceptions](exceptions.md) | what each function raises, and when |

Everything public is importable from the top-level package:

```python
from pyrecords import (
    Data,
    DataItem,
    ExtensionNotSupportedError,
    OrderByKey,
    ReaderRegistry,
    filter_data,
    get_compiler,
    group_by_data,
    object_readers,
    order_by_data,
    readers,
    rules,
)
```
