# Text Matching

The `llm-data-utils` library provides deterministic substring search and source-offset-preserving matching primitives designed for entity locator pipelines, annotation spans, and prompt tokenization preparation.

---

## Public API

```python
from llm_data_utils.models import TextMatch
from llm_data_utils.text import find_matches
```

---

## The TextMatch Model

Each match returned by `find_matches()` is represented as an immutable [`TextMatch`](../src/llm_data_utils/models/text.py) dataclass instance:

| Field | Type | Description |
| :--- | :--- | :--- |
| `text` | `str` | The exact matched substring slice from the source text. |
| `start` | `int` | Inclusive start character offset in the source string. |
| `end` | `int` | Exclusive end character offset in the source string. |
| `index` | `int` | Zero-based sequence index of the match in the returned list. |

### Invariant Guarantee

For every generated `TextMatch`, the slice invariant holds:

```python
source[match.start:match.end] == match.text
```

---

## Matching Modes & Semantics

### 1. Exact Matching (`case_sensitive=True`)

When `case_sensitive=True` (the default), `find_matches()` performs exact character substring matching:

```python
matches = find_matches("Python python PYTHON", "python", case_sensitive=True)
# Returns 1 match: TextMatch(text='python', start=7, end=13, index=0)
```

### 2. Overlapping Matches

Matching detects all occurrences, including overlapping substring matches:

```python
matches = find_matches("aaaa", "aa", case_sensitive=True)
# Chunk 0: 'aa' (0:2, index=0)
# Chunk 1: 'aa' (1:3, index=1)
# Chunk 2: 'aa' (2:4, index=2)
```

### 3. Unicode-Aware Case-Insensitive Matching (`case_sensitive=False`)

When `case_sensitive=False`, matching uses Unicode-aware `str.casefold()` semantics.

#### Source Offset Preservation

Because Unicode casefolding can change string length (for example, German `"ß"` casefolds to `"ss"`, expanding 1 character to 2), casefolding the entire source string and searching on transformed offsets would produce corrupt source boundaries.

`find_matches()` evaluates candidate slices against original source boundaries to ensure offsets map directly to the original input text:

```python
matches = find_matches("Straße", "STRASSE", case_sensitive=False)
# Returns 1 match: TextMatch(text='Straße', start=0, end=6, index=0)
```

Notice that `match.end` is `6` (the length of `"Straße"` in the original source), accurately reflecting the slice `source[0:6]`.

---

## Validation & Error Handling

All validation failures raise [`ValidationError`](../src/llm_data_utils/exceptions.py):

* **`text`**: Must be a `str`. Non-string values raise `ValidationError`.
* **`query`**: Must be a non-empty `str`. Empty strings (`""`) and non-string values raise `ValidationError`. (Whitespace-only strings are valid queries).
* **`case_sensitive`**: Must be a boolean (`True` or `False`). Non-boolean values (e.g. `1`, `0`, `"true"`, `None`) raise `ValidationError`.

---

## Scope & Non-Goals

The `find_matches` primitive focuses purely on deterministic substring locating:

* **Not Fuzzy Search**: Does not calculate Levenshtein distance, Damerau-Levenshtein, or approximate string edit distances.
* **Not Semantic Retrieval**: Does not compute vector embeddings, semantic similarities, or BM25 rankings.
* **Not Token-Aware**: Operates on Python character boundaries without requiring tokenizers.
* **No Implicit Normalization**: Does not normalize whitespace or Unicode forms on source or query text. Callers compose normalization primitives explicitly if desired.
