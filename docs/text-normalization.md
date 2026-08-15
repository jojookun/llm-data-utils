# Text Normalization

The `llm-data-utils` library provides a suite of focused, composable text normalization primitives designed to sanitize and prepare string data for downstream processing, embedding generation, and language model workflows.

Rather than providing a single opaque "clean_text" function with hidden side effects, the library offers independent building blocks that callers can explicitly compose according to their exact pipeline requirements.

---

## Public API

```python
from llm_data_utils.text import (
    CaseMode,
    UnicodeForm,
    convert_case,
    normalize_unicode,
    normalize_whitespace,
    trim_text,
)
```

---

## Composable Primitives

### 1. Trimming Text (`trim_text`)

Strips leading and trailing whitespace from a string while preserving all internal whitespace and characters.

```python
trim_text("  hello   world  ")  # "hello   world"
```

### 2. Whitespace Normalization (`normalize_whitespace`)

Collapses every sequence of one or more consecutive Unicode whitespace characters (spaces, tabs, newlines, non-breaking spaces) into a single ASCII space (`" "`).

> [!IMPORTANT]
> `normalize_whitespace()` **does not trim** the string. If leading or trailing whitespace is present, it is collapsed into a single leading/trailing space.

To both normalize whitespace and trim, compose the two functions:

```python
raw = "  hello\t\tworld\n "

# Whitespace normalization alone (preserves leading/trailing existence)
normalized = normalize_whitespace(raw)  # " hello world "

# Composed with trimming
cleaned = trim_text(normalize_whitespace(raw))  # "hello world"
```

### 3. Unicode Normalization (`normalize_unicode`)

Transforms Unicode text into a standard canonical or compatibility normalization form using the Python standard library.

Supported forms:
* `NFC` (Canonical Decomposition followed by Canonical Composition - **default**)
* `NFD` (Canonical Decomposition)
* `NFKC` (Compatibility Decomposition followed by Canonical Composition)
* `NFKD` (Compatibility Decomposition)

```python
# Composed accented character (NFC) vs decomposed character + combining mark (NFD)
decomposed = "e\u0301"  # 'é' in NFD
composed = normalize_unicode(decomposed, form="NFC")  # '\xe9' ('é')
```

### 4. Case Conversion (`convert_case`)

Converts string casing using a controlled, explicit mode:

* `"lower"`: Standard lowercase transformation (`text.lower()`).
* `"upper"`: Standard uppercase transformation (`text.upper()`).
* `"casefold"`: Aggressive Unicode casefolding (`text.casefold()`), ideal for caseless matching across non-ASCII scripts (e.g. German `"ß"` -> `"ss"`).

```python
convert_case("HELLO WORLD", mode="lower")      # "hello world"
convert_case("hello world", mode="upper")      # "HELLO WORLD"
convert_case("Fluß", mode="casefold")          # "fluss"
```

---

## Pipeline Composition Example

```python
from llm_data_utils.text import (
    convert_case,
    normalize_unicode,
    normalize_whitespace,
    trim_text,
)

raw_input = "  \u00c9cole\t\tPolytechnique \n"

# Step-by-step pipeline
text = normalize_unicode(raw_input, form="NFKC")
text = normalize_whitespace(text)
text = trim_text(text)
text = convert_case(text, mode="casefold")

print(text)  # "école polytechnique"
```

---

## Validation & Error Handling

* All functions require `str` inputs. Passing non-string types (such as `None`, `int`, `bytes`, or custom objects) raises [`ValidationError`](../src/llm_data_utils/exceptions.py).
* Invalid `UnicodeForm` or `CaseMode` values raise `ValidationError`.
