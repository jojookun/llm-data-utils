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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
