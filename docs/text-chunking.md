# Text Chunking

The `llm-data-utils` library provides deterministic, fixed-width character-based text chunking with source-offset metadata designed for context segmentation and downstream document preparation.

---

## Public API

```python
from llm_data_utils.models import TextChunk
from llm_data_utils.text import chunk_text
```

---

## The TextChunk Model

Each chunk produced by `chunk_text()` is returned as an immutable [`TextChunk`](../src/llm_data_utils/models/text.py) dataclass instance:

| Field | Type | Description |
| :--- | :--- | :--- |
| `text` | `str` | The exact character slice from the source text. |
| `start` | `int` | Inclusive start character offset in the source string. |
| `end` | `int` | Exclusive end character offset in the source string. |
| `index` | `int` | Zero-based sequence index of the chunk in the returned list. |

### Invariant Guarantee

For every generated `TextChunk`, the exact slice invariant holds:

```python
source[chunk.start:chunk.end] == chunk.text
```

---

## Chunking Semantics

### Character-Based Sizing

`chunk_size` sets the maximum number of Python string characters per chunk. Chunking operates strictly on character indices—no automatic word, sentence, paragraph, or token boundaries are imposed.

```python
chunks = chunk_text("abcdefghij", chunk_size=4)
# Chunk 0: 'abcd' (0:4)
# Chunk 1: 'efgh' (4:8)
# Chunk 2: 'ij'   (8:10)
```

### Overlap & Step

When `overlap` is specified (where `0 <= overlap < chunk_size`), the advance step between consecutive chunks is:

$$\text{step} = \text{chunk\_size} - \text{overlap}$$

Example with `chunk_size=4, overlap=1` (`step=3`):

```python
chunks = chunk_text("abcdefghij", chunk_size=4, overlap=1)
# Chunk 0: 'abcd' (0:4, index=0)
# Chunk 1: 'defg' (3:7, index=1)
# Chunk 2: 'ghij' (6:10, index=2)
```

### Redundant Trailing-Chunk Prevention

Once a generated chunk reaches the end of the source string (`chunk.end == len(text)`), chunking completes immediately. No redundant or duplicate partial trailing slices are emitted.

### Empty Text

Providing an empty string returns an empty list without raising an error:

```python
chunk_text("", chunk_size=100)  # []
```

---

## Validation & Error Handling

All invalid arguments raise [`ValidationError`](../src/llm_data_utils/exceptions.py):

* **`text`**: Must be a `str`. Non-string values (e.g. `None`, `int`, `list`) raise `ValidationError`.
* **`chunk_size`**: Must be a positive integer (`> 0`). Non-integers, `<= 0` values, and boolean types (`True`/`False`) raise `ValidationError`.
* **`overlap`**: Must be a non-negative integer (`>= 0`) and strictly less than `chunk_size`. Values `< 0`, `>= chunk_size`, non-integers, and booleans raise `ValidationError`.

---

## Scope & Non-Goals

Fixed-width character chunking is designed as a fast, dependency-free foundational primitive:

* **Not Token-Aware**: `chunk_size` specifies character counts, not BPE, WordPiece, or LLM token counts.
* **Not Sentence/Paragraph-Aware**: Does not split along punctuation or newline boundaries.
* **No Preprocessing**: Does not implicitly normalize whitespace, trim, or alter Unicode forms. Callers compose normalization primitives explicitly if desired.
