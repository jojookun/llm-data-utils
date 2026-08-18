# Structured Data Transformation

The `llm-data-utils` library provides deterministic, path-based traversal and copy-on-write transformation functions for nested normalized data structures.

---

## Public API

```python
from llm_data_utils.core import get_path, remove_path, set_path
from llm_data_utils.models import DataPath, PathSegment
```

---

## Path Representation

Paths are represented as typed tuples of keys and indices:

```python
PathSegment = str | int
DataPath = tuple[PathSegment, ...]
```

* **String Segments (`str`)**: Access dictionary/mapping keys.
* **Integer Segments (`int`)**: Access list/sequence indices (zero-based, non-negative).
* **Strict Typing**: Boolean values (`True`/`False`), float numbers, and dotted string syntax (e.g. `"user.name"`) are not valid paths and raise `ValidationError`.
* **Explicit Coordinates**: Negative list indices are intentionally rejected to maintain strict structural addressing.

---

## Operations

### 1. Retrieve Value (`get_path`)

Traverses nested containers and returns the value at the specified path:

```python
data = {
    "user": {
        "name": "Jona",
        "scores": [10, 20, 30],
    }
}

get_path(data, ("user", "name"))      # "Jona"
get_path(data, ("user", "scores", 1)) # 20
get_path(data, ())                    # Returns root `data`
```

### 2. Update Value (`set_path`)

Returns a copy of the data structure with the value at the target path updated using copy-on-write semantics:

```python
data = {
    "user": {
        "name": "Jona",
        "age": 20,
    }
}

updated = set_path(data, ("user", "name"), "Naufal")

# `data` remains untouched: data["user"]["name"] == "Jona"
# `updated["user"]["name"]` == "Naufal"
```

* **Root Replacement**: Passing an empty path `()` returns `value`.
* **Path Existence**: All segments of the path must already exist. `set_path` does not automatically create intermediate dictionaries or lists.

### 3. Remove Element (`remove_path`)

Returns a copy of the data structure with the key or list element at the target path removed:

```python
data = {
    "user": {
        "name": "Jona",
        "age": 20,
    },
    "items": ["a", "b", "c"],
}

# Remove mapping key
without_age = remove_path(data, ("user", "age"))
# without_age["user"] == {"name": "Jona"}

# Remove list item (shifts subsequent elements)
without_item = remove_path(data, ("items", 1))
# without_item["items"] == ["a", "c"]
```

* **Root Deletion Disallowed**: Attempting to remove the root path `()` raises `ValidationError`.

---

## Copy-on-Write Semantics

Transformations do **not** mutate the caller's input structures. Instead:

1. Only container objects (`dict` or `list`) along the active path are shallow-copied and reconstructed.
2. Unchanged sibling branches and subtrees remain structurally shared for memory efficiency.
3. No global deep-copy is performed.

```python
source = {
    "user": {"name": "Jona"},
    "settings": {"theme": "dark"},
}

updated = set_path(source, ("user", "name"), "Naufal")

# Modified path container is newly created:
assert updated["user"] is not source["user"]

# Unmodified subtree remains shared:
assert updated["settings"] is source["settings"]
```

---

## Validation & Error Handling

All traversal or argument errors raise [`ValidationError`](../src/llm_data_utils/exceptions.py):

* **Invalid Path Type**: Paths must be `tuple` instances containing only `str` and `int` (rejecting `list`, `dict`, `bool`, `None`).
* **Container/Segment Mismatch**: Attempting to use an `int` on a `dict` or a `str` on a `list` raises `ValidationError`.
* **Missing Target**: Missing dictionary keys or out-of-bounds list indices raise `ValidationError`.
* **Negative Indices**: Negative numbers (e.g. `-1`) raise `ValidationError`.
* **Scalar Traversal**: Attempting to traverse deeper into a scalar (e.g. `int`, `str`, `None`) raises `ValidationError`.
* **Remove Root**: Calling `remove_path(data, ())` raises `ValidationError`.
