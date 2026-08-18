# llm-data-utils

A lightweight, extensible Python utility library for data processing, advanced string manipulation, and computation.

## Project Status

> **Notice:** This project is currently under active foundational development (Day 1 of 30).

The current scope is focused on repository layout, package scaffolding, and build system configuration. Advanced modules (such as data manipulation, compute utilities, and future integrations) will be progressively introduced in upcoming development phases.

## Installation

Install in editable mode for local development:

```bash
python -m pip install -e .
```

## Quick Start

Verify the installation and check the package version:

```python
import llm_data_utils
from llm_data_utils import __version__

print(f"llm-data-utils version: {__version__}")
```

### Data Normalization

Normalize Python data structures into predictable JSON-friendly formats:

```python
from llm_data_utils.core import normalize_data

data = {"items": (1, 2, 3), "unique": {"b", "a"}}
normalized = normalize_data(data)
print(normalized)  # {'items': [1, 2, 3], 'unique': ['a', 'b']}
```

For full documentation, see [docs/data-normalization.md](docs/data-normalization.md).

### Structured Data Transformation

Traverse, update, and remove nested values with copy-on-write path operations:

```python
from llm_data_utils.core import set_path

data = {"user": {"name": "Jona"}}
updated = set_path(data, ("user", "name"), "Naufal")
print(updated)  # {'user': {'name': 'Naufal'}}
```

For full documentation, see [docs/data-transformation.md](docs/data-transformation.md).

### Text Normalization

Normalize whitespace, trim text, standardize Unicode, and convert case with composable primitives:

```python
from llm_data_utils.text import normalize_whitespace, trim_text

cleaned = trim_text(normalize_whitespace("  hello   world  "))
print(cleaned)  # "hello world"
```

For full documentation, see [docs/text-normalization.md](docs/text-normalization.md).

### Text Transformation

Perform literal and regular-expression string transformations with controlled boundaries:

```python
from llm_data_utils.text import replace_pattern

masked = replace_pattern("Order 12345", r"\d+", "<id>")
print(masked)  # "Order <id>"
```

For full documentation, see [docs/text-transformation.md](docs/text-transformation.md).

### Text Chunking

Deterministically split text into fixed-width character chunks with source offsets:

```python
from llm_data_utils.text import chunk_text

chunks = chunk_text("abcdefghij", chunk_size=4, overlap=1)
for chunk in chunks:
    print(f"[{chunk.start}:{chunk.end}] {chunk.text!r}")
```

For full documentation, see [docs/text-chunking.md](docs/text-chunking.md).

### Text Matching

Search for substring occurrences and extract matched source offsets:

```python
from llm_data_utils.text import find_matches

matches = find_matches("Python PYTHON python", "python", case_sensitive=False)
for match in matches:
    print(f"[{match.start}:{match.end}] {match.text!r}")
```

For full documentation, see [docs/text-matching.md](docs/text-matching.md).

## Requirements

- Python >= 3.11

## Development

Development follows a structured GitHub Flow workflow:
- Work is completed on short-lived branches (`feat/*`, `fix/*`, `chore/*`, etc.).
- Commits adhere to [Conventional Commits](https://www.conventionalcommits.org/).
- Changes are integrated into `main` via reviewed Pull Requests.

To install development dependencies (`pytest`, `ruff`, `mypy`):

```bash
python -m pip install -e ".[dev]"
```

For complete development guidelines and environment configuration, see:
- [docs/environment.md](docs/environment.md) (Environment setup & dependency guide)
- [docs/development-workflow.md](docs/development-workflow.md) (Branching & PR workflow)
- [docs/engineering-standards.md](docs/engineering-standards.md) (Type hints, exceptions, mypy, Ruff & logging standards)

## Architecture

The library is organized into modular packages with strict separation of concerns:

- `core`: Shared processing abstractions and internal orchestration.
- `models`: Shared data models and type contracts.
- `text`: String and text processing algorithms.
- `compute`: Provider-independent computational routines.

*LLM abstraction layers (`llm`) and provider bindings (`adapters`) are planned for future development phases.*

For full architectural principles and dependency guidelines, see [docs/architecture.md](docs/architecture.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
