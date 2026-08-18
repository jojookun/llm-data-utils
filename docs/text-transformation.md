# Text Transformation

The `llm-data-utils` library provides controlled, provider-independent string transformation and replacement primitives designed for data sanitization, pattern redaction, and prompt preparation.

These transformation functions operate independently from normalization primitives (such as whitespace collapsing or Unicode standardization), allowing callers to compose transformations explicitly.

---

## Public API

```python
from llm_data_utils.text import (
    remove_pattern,
    replace_pattern,
    replace_text,
)
```

---

## Core Transformation Functions

### 1. Literal Replacement (`replace_text`)

Replaces occurrences of an exact substring within a text string. The search text is treated as a pure literal—special regex metacharacters (`.`, `*`, `[`, `?`, `+`) are matched literally.

```python
from llm_data_utils.text import replace_text

# Literal period replacement (not regex wildcard)
result = replace_text("version 1.0.0", ".", "-")
print(result)  # "version 1-0-0"
```

### 2. Pattern Replacement (`replace_pattern`)

Performs regular expression substitutions with support for capture groups, backreferences, and compilation flags.

```python
import re
from llm_data_utils.text import replace_pattern

# Basic pattern replacement
masked = replace_pattern("User ID: 94821", r"\d+", "<id>")
print(masked)  # "User ID: <id>"

# Capture-group reordering
reordered = replace_pattern("Doe, John", r"(\w+),\s*(\w+)", r"\2 \1")
print(reordered)  # "John Doe"

# Case-insensitive replacement using flags
cleaned = replace_pattern(
    "Warning: ERROR 404",
    r"error\s+\d+",
    "<redacted>",
    flags=re.IGNORECASE,
)
print(cleaned)  # "Warning: <redacted>"
```

### 3. Pattern Removal (`remove_pattern`)

Convenience primitive to strip all occurrences matching a regular expression pattern (equivalent to substituting with an empty string).

```python
from llm_data_utils.text import remove_pattern

# Remove HTML tags or markup artifacts
cleaned = remove_pattern("<p>Hello <b>World</b></p>", r"<[^>]+>")
print(cleaned)  # "Hello World"
```

---

## Replacement Count Semantics

All transformation functions adhere to a uniform replacement count contract:

* **`count=None`** (*default*): Replace all occurrences.
* **`count=0`**: Perform zero replacements (returns the original text unchanged after validating both the pattern and replacement template).
* **`count=N`** (*integer > 0*): Replace at most `N` occurrences.

> [!WARNING]
> Negative integers, non-integer numbers (e.g. floats), and boolean values (`True`/`False`) are invalid and raise `ValidationError`.

```python
text = "apple, apple, apple"

replace_text(text, "apple", "orange", count=1)     # "orange, apple, apple"
replace_text(text, "apple", "orange", count=0)     # "apple, apple, apple"
replace_text(text, "apple", "orange", count=None)  # "orange, orange, orange"
```

---

## Validation & Error Handling

All validation and parsing errors raise [`ValidationError`](../src/llm_data_utils/exceptions.py):

* **Type Safety**: `text`, `old`, `new`, `pattern`, and `replacement` must be `str`.
* **Count Validation**: `count` must be a non-negative integer or `None`.
* **Flag Validation**: `flags` must be an instance of `re.RegexFlag`.
* **Invalid Pattern Syntax**: Malformed regular expression patterns (e.g. unclosed brackets `[`) raise `ValidationError` with details from the parser.
* **Invalid Replacement Template**: Malformed replacement templates (such as non-existent capture groups `\9`) raise `ValidationError`.

---

## Regex Safety Boundaries

The transformation primitives validate regular expression syntax and argument types prior to execution. However:

* The library does **not** provide execution timeouts or ReDoS (Regular Expression Denial of Service) protection against pathological backtracking on untrusted user-supplied regular expressions.
* Callers should validate and control regular expressions when handling untrusted inputs.
