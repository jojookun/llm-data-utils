# Data Normalization

The `llm-data-utils` library provides a robust, provider-independent recursive data normalization API designed to sanitize and transform standard Python data structures into predictable, JSON-friendly formats.

---

## Public API

```python
from llm_data_utils.core import normalize_data
from llm_data_utils.models import NormalizedData, ScalarValue
```

### Signature

```python
def normalize_data(value: object) -> NormalizedData:
    ...
```

---

## Supported Types & Transformations

| Source Type | Output Type | Transformation Behavior |
| :--- | :--- | :--- |
| `None` | `None` | Preserved unchanged |
| `bool` | `bool` | Preserved unchanged |
| `int` | `int` | Preserved unchanged |
| `float` | `float` | Preserved (finite values only) |
| `str` | `str` | Preserved unchanged |
| `Mapping` / `dict` | `dict[str, NormalizedData]` | New dictionary with string keys and recursively normalized values |
| `list` | `list[NormalizedData]` | New list with recursively normalized items |
| `tuple` | `list[NormalizedData]` | Converted into a new list with recursively normalized items |
| `set` / `frozenset` | `list[NormalizedData]` | Converted into a deterministically sorted list of normalized items |

---

## Validation & Error Handling

All validation failures raise [`ValidationError`](../src/llm_data_utils/exceptions.py) with descriptive path context (e.g. `$['users'][0]['age']`):

1. **String-Only Mapping Keys**: Mappings with non-string keys (e.g. `{1: "value"}`) are rejected.
2. **Finite Floats Only**: Special floating-point values (`nan`, `inf`, `-inf`) are rejected.
3. **Unsupported Types**: Arbitrary objects (e.g. custom instances, raw bytes) raise `ValidationError` rather than undergoing silent lossy conversion.
4. **Circular References**: Recursive container self-references are detected and rejected to prevent infinite loops. Repeated shared instances across non-circular branches normalize safely.

---

## Mutation Safety

`normalize_data` is strictly side-effect free:
* Source container instances are never mutated.
* Modifying the returned normalized structure has no effect on the input structures.

---

## Usage Example

```python
from llm_data_utils.core import normalize_data

input_payload = {
    "title": "Document Title",
    "tags": {"python", "ai", "data"},  # Set -> sorted list
    "coordinates": (10.5, 20.25),       # Tuple -> list
    "metadata": {
        "active": True,
        "count": 42,
        "rating": 4.8,
        "notes": None,
    },
}

normalized = normalize_data(input_payload)

print(normalized)
# {
#     "title": "Document Title",
#     "tags": ["ai", "data", "python"],
#     "coordinates": [10.5, 20.25],
#     "metadata": {
#         "active": True,
#         "count": 42,
#         "rating": 4.8,
#         "notes": None,
#     },
# }
```
