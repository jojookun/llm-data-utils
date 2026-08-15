# Engineering Standards

This document establishes the coding conventions, typing requirements, error handling guidelines, and quality policies for `llm-data-utils`.

---

## Type Hints

All code in `llm-data-utils` must be fully typed and validated using `mypy` in strict mode.

### Guidelines

* **Full Signatures**: All public functions and methods must include type annotations for every parameter and the return value.
* **Modern Syntax**: Use native Python 3.11+ type syntax (e.g., `list[str]`, `dict[str, int]`, `X | None` instead of `typing.Union` / `typing.Optional`).
* **Input Interfaces**: Prefer abstract collection types from `collections.abc` (such as `Sequence[T]`, `Mapping[K, V]`, `Iterable[T]`) for parameter inputs to allow flexibility for callers.
* **Return Types**: Return precise, concrete types (such as `list[str]` or specific dataclasses) where practical.
* **Avoid `Any`**: Minimize the use of `Any`. Where dynamic data is unavoidable, use explicit `TypeVar`, generics, or bounded `object`.

---

## Public API

Public API surface area must be explicit, minimal, and predictable.

### Guidelines

* **Intentional Exports**: Package `__init__.py` files define their exported interface using `__all__`.
* **Explicit Import Paths**: Public symbols are imported from their owning subpackage (e.g. `from llm_data_utils.exceptions import ValidationError`). Root `llm_data_utils` namespace is kept minimal.
* **Internal Encapsulation**: Any module, function, or attribute prefixed with an underscore (`_`) is private and internal. Callers must not rely on internal symbols.
* **No Wildcard Imports**: `from module import *` is strictly prohibited across the entire codebase.

---

## Exceptions

The library provides a structured, provider-independent exception hierarchy:

```text
Exception
   └── LLMDataUtilsError
        ├── ValidationError
        ├── ProcessingError
        └── ConfigurationError
```

### Exception Classes

* **`LLMDataUtilsError`**: The base class for all exceptions raised directly by this library. Catching this allows callers to isolate library-specific errors.
* **`ValidationError`**: Raised when input arguments, schemas, or data structures fail validation constraints.
* **`ProcessingError`**: Raised when text transformations, chunking, or computational execution encounters an error.
* **`ConfigurationError`**: Raised when invalid options, missing settings, or misconfigured environment parameters are detected.

### Error Handling Rules

* **Exception Chaining**: When catching internal or lower-level exceptions and raising a library exception, always preserve root cause context using `from exc`:
  ```python
  try:
      result = perform_operation(data)
  except ValueError as exc:
      raise ValidationError("Invalid input format.") from exc
  ```
* **No Broad Catches**: Avoid blanket `except Exception:` unless converting unhandled errors at a clear architectural boundary.
* **Secret Safety**: **Never** include API keys, auth tokens, or sensitive user data in exception messages.

---

## Logging

`llm-data-utils` follows the standard Python library logging conventions.

### Rules for Library Modules

* **Module-Level Loggers**: Always instantiate a logger bound to the module namespace:
  ```python
  import logging

  logger = logging.getLogger(__name__)
  ```
* **No Global Configuration**: Library code must **never** call `logging.basicConfig()`, `logging.getLogger().setLevel()`, or attach default stream handlers. The consuming application controls all logging configuration, levels, formatting, and destinations.
* **Zero Secret Logging**: Never log API keys, access tokens, credentials, or sensitive user payloads.
* **Appropriate Levels**:
  * `DEBUG`: Fine-grained operational diagnostics.
  * `INFO`: High-level lifecycle events.
  * `WARNING`: Recoverable anomalies or deprecated usage.
  * `ERROR`: Failures in processing operations.

---

## Docstrings & Naming

### Docstrings

* All public modules, classes, methods, and functions must have descriptive PEP 257-compliant docstrings.
* Include descriptions of arguments, return values, and exceptions raised where non-trivial.
* Internal single-line helpers do not require verbose docstrings if their name and typing are self-explanatory.

### Naming Conventions

* **`snake_case`**: Functions, methods, variables, modules, and packages.
* **`PascalCase`**: Classes, dataclasses, and exceptions.
* **`UPPER_CASE`**: Constants and immutable configuration values.
* **`_leading_underscore`**: Private or internal implementation functions, classes, and attributes.
* **Descriptive Naming**: Avoid ambiguous names such as `utils2.py`, `helper_new.py`, `temp.py`, or generic `manager.py`.
