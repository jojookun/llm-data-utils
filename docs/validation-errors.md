# Validation and Error Handling

This document establishes the validation policies, exception boundaries, error-message hygiene guidelines, and error-handling conventions across `llm-data-utils`.

---

## Exception Hierarchy

All library-specific exceptions derive from `LLMDataUtilsError`:

```text
Exception
   └── LLMDataUtilsError
        ├── ValidationError
        ├── ProcessingError
        └── ConfigurationError
```

* **`LLMDataUtilsError`**: The base class for all exceptions raised directly by this library. Allows callers to isolate library-specific errors from standard library or third-party exceptions.
* **`ValidationError`**: Raised when caller input violates structural, typing, range, or domain-specific preconditions.
* **`ProcessingError`**: Raised when computational execution, text transformation, or external callbacks encounter an unrecoverable runtime failure despite valid inputs.
* **`ConfigurationError`**: Reserved for invalid settings, environment parameters, or options.

---

## ValidationError

`ValidationError` signals caller-contract violations before or during execution. It covers:

* **Type Violations**: Passing non-string objects to text primitives, non-boolean arguments to flag parameters, or non-numeric types to math helpers.
* **Range & Value Constraints**: Out-of-bounds numbers, invalid slice coordinates, or unsupported conversion modes (e.g. invalid `CaseMode` or `UnicodeForm`).
* **Path & Schema Failures**: Missing mapping keys, out-of-bounds list indices, negative list indices, or invalid segment types in structured data path traversal (`get_path`, `set_path`, `remove_path`).
* **Malformed Regex Inputs**: Malformed regex patterns or invalid replacement templates.
* **Precondition Failures**: Zero denominator in `safe_divide`/`percentage`, empty sequences in `mean_values`, or circular container references during `normalize_data`.
* **Pipeline Definition Errors**: Unsupported step container types (e.g. `set`, `dict`, generators), non-`PipelineStep` elements, or duplicate step names.

### Representative Examples

```python
# Text domain: invalid input type
trim_text(123)  # ValidationError: Expected str for 'text', got int.

# Structured data domain: non-existent path
get_path({"user": {"name": "Jona"}}, ("user", "age"))  # ValidationError: Key 'age' not found at ('user',).

# Compute domain: zero denominator / empty sequence
safe_divide(10, 0)  # ValidationError: Denominator cannot be zero.
mean_values([])     # ValidationError: Expected non-empty sequence for 'values', got empty sequence.

# Pipeline domain: duplicate step names
run_pipeline(data, [PipelineStep("clean", fn_a), PipelineStep("clean", fn_b)])  # ValidationError: Duplicate pipeline step name: 'clean'.
```

---

## ProcessingError

`ProcessingError` is reserved strictly for operational or execution failures that occur *after* input validation has succeeded on valid arguments.

Key scenarios include:

1. **Arithmetic Overflow / Non-Finite Computation**: Valid finite inputs whose mathematical summation, mean, division, or percentage calculation exceeds IEEE 754 float representable bounds or produces infinity.
2. **Unexpected User Callbacks in Pipelines**: User-provided transformation functions within `run_pipeline` that raise unhandled exceptions (e.g., `RuntimeError`, `TypeError`, `ValueError`).

### Representative Examples

```python
# Compute domain: arithmetic overflow
percentage(1e308, 1e-10)  # ProcessingError: Percentage calculation resulted in a non-finite value.

# Pipeline domain: unexpected callback failure
def broken_transform(data):
    raise RuntimeError("database connection failed")

run_pipeline(data, [PipelineStep("step-1", broken_transform)])
# ProcessingError: Pipeline step 'step-1' failed. (Original RuntimeError attached via __cause__)
```

---

## ConfigurationError

`ConfigurationError` is reserved for invalid library configuration, missing environment variables, or malformed provider configurations. It is distinguished from `ValidationError` because it represents environment/setup defects rather than dynamic function argument defects.

---

## Built-in Exception Boundaries

Public library APIs must **never** leak raw, unhandled internal Python exceptions such as:

* `KeyError` / `IndexError` (translated to `ValidationError` with detailed path context in structured data operations)
* `ZeroDivisionError` (prevented and raised as `ValidationError` in `safe_divide`)
* `re.error` (caught and re-raised as `ValidationError` with regex diagnostic details in text transformations)
* `OverflowError` (caught and re-raised as `ProcessingError` in numeric computations)

Callers can reliably depend on `LLMDataUtilsError` and its subclasses without needing to defensively catch implementation-specific built-ins.

---

## Exception Chaining

When translating internal or lower-level exceptions into library exceptions, root cause context is strictly preserved using explicit `from exc` chaining:

```python
try:
    compiled = re.compile(pattern, flags=flags)
except re.error as exc:
    raise ValidationError(f"Invalid regular expression pattern: {exc.msg}") from exc
```

This ensures full diagnostic tracebacks remain accessible via `error.__cause__` while maintaining a clean, predictable public exception hierarchy.

---

## Error Message Hygiene

Error messages across all modules adhere to strict hygiene principles:

* **Stable and Descriptive**: Clearly state what was expected versus what was received (e.g. `Expected str for 'text', got int.`).
* **Precise Coordinates**: Include path breadcrumbs (e.g. `at ('user', 'scores', 2)`), step names, or argument names to make errors easy to debug.
* **Zero Secret or Full-Payload Leakage**: Never echo raw user data structures, whole documents, API keys, credentials, or sensitive arguments into exception strings.

---

## Python Type Quirks

In Python, `bool` is a subclass of `int` (`isinstance(True, int) == True`). To prevent subtle logical bugs and type coercion issues:

* All numeric and integer validators explicitly reject `bool` inputs (`isinstance(value, bool)` is checked first).
* Functions requiring an integer (such as `chunk_size`, `overlap`, `count`, and path sequence indices) reject boolean values with `ValidationError`.
* Functions accepting numeric numbers (`int | float`) reject boolean values with `ValidationError`.

---

## Callback Boundaries

`run_pipeline` serves as an orchestration boundary around arbitrary user-supplied callables (`DataTransform`).

* **`LLMDataUtilsError` Preservation**: Any existing library exception raised by a step is re-raised unchanged, preserving intentional validation or processing categories.
* **Broad `Exception` Catch**: Unexpected exceptions derived from `Exception` are caught and wrapped in `ProcessingError(f"Pipeline step {step.name!r} failed.") from exc`.
* **No `BaseException` Catching**: System-level signals such as `KeyboardInterrupt`, `SystemExit`, and `GeneratorExit` are **never** caught, ensuring that process interruption and system signals propagate cleanly.

---

## Internal Validation Helpers

To reduce repetitive boilerplate while avoiding unnecessary abstraction layers, primitive type assertions are centralized in the private `llm_data_utils._validation` module:

* `_require_str(value, *, name)`
* `_require_bool(value, *, name)`
* `_require_non_bool_int(value, *, name)`

### Encapsulation Policy

* `_validation.py` is strictly private (prefixed with `_`) and is **never** re-exported in package `__all__` definitions.
* Domain-specific validation rules (such as Unicode forms, regex flags, overlap relationships, list bounds, and duplicate step names) remain local to their respective modules.
