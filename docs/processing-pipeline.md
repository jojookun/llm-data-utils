# Processing Pipeline

The `llm-data-utils` library provides a lightweight, synchronous, and linear processing pipeline engine for `NormalizedData`.

---

## Purpose

The pipeline abstraction coordinates callable data transformation steps sequentially without coupling the `core` package to specific feature domains such as `text` or `compute`. It offers predictable data flow, strict definition validation, and clean exception isolation for application-level data preparation workflows.

---

## Public API

```python
from llm_data_utils.core import (
    DataTransform,
    PipelineStep,
    run_pipeline,
)
```

---

## DataTransform

`DataTransform` is a public type alias defined as:

```python
DataTransform = Callable[[NormalizedData], NormalizedData]
```

A transform is any callable object that accepts a `NormalizedData` structure as its sole argument and returns a `NormalizedData` structure. Custom transformation functions are responsible for honoring this contract.

---

## PipelineStep

`PipelineStep` is an immutable, slotted dataclass that couples a unique step name with an executable transform:

```python
@dataclass(frozen=True, slots=True)
class PipelineStep:
    name: str
    transform: DataTransform
```

### Immutability

Because `PipelineStep` is defined with `frozen=True` and `slots=True`, its fields cannot be reassigned or dynamically modified after instantiation. Attempting to assign `step.name = "other"` raises `FrozenInstanceError`.

### Validation

During instantiation (`__post_init__`), `PipelineStep` enforces:

* **Name Validation**: `name` must be a non-empty `str` containing at least one non-whitespace character. Types such as `None`, integers, empty strings `""`, or whitespace-only strings `"   "` raise `ValidationError`. Valid names with surrounding whitespace (e.g. `" clean "`) are preserved as-is without automatic stripping.
* **Transform Validation**: `transform` must be callable at runtime (e.g. function, lambda, or callable object). Non-callable values raise `ValidationError`.

---

## Sequential Execution

The pipeline executes steps in the exact order they are provided in the `steps` sequence:

```text
input data
    │
    ▼
[ Step A ] ──> output A
    │
    ▼
[ Step B ] ──> output B
    │
    ▼
[ Step C ] ──> output C (final result)
```

The output of step $N$ becomes the input to step $N+1$. No sorting, reordering, or parallel execution is performed.

---

## Empty Pipeline

If `steps` is an empty list `[]` or empty tuple `()`, `run_pipeline` returns the input `data` immediately with identity preserved:

```python
data = {"user": "Alice"}
result = run_pipeline(data, ())

assert result is data
```

No unnecessary copies or allocations are performed when executing an empty pipeline.

---

## Unique Names

Within a single `run_pipeline` invocation, all step names must be strictly unique using exact string equality.

```python
# Raises ValidationError before any step executes:
pipeline = (
    PipelineStep("clean", transform_a),
    PipelineStep("clean", transform_b),
)
run_pipeline(data, pipeline)
```

Duplicate detection uses literal string matching without casefolding or trimming. Therefore, `"clean"` and `"CLEAN"` are treated as distinct names.

---

## Validation Before Execution

Before executing any transform, `run_pipeline` performs full definition validation:

1. Validates that the `steps` container is a `list` or `tuple` (rejecting `set`, `dict`, generators, single steps, etc. with `ValidationError`).
2. Validates that every element in the sequence is an instance of `PipelineStep`.
3. Validates that all step names are unique.

If any validation rule fails, execution halts immediately and no step transforms are invoked.

---

## Exception Semantics

Error handling during pipeline execution follows strict boundary rules:

* **Library Exceptions Preserved**: If a transform raises any exception derived from `LLMDataUtilsError` (such as `ValidationError`, `ProcessingError`, or `ConfigurationError`), it is re-raised unchanged.
* **Unexpected Exceptions Wrapped**: If a transform raises an unexpected standard exception (such as `RuntimeError`, `ValueError`, or `TypeError`), it is caught and wrapped in a `ProcessingError` with the failing step name identified:
  ```text
  ProcessingError: Pipeline step 'step_name' failed.
  ```
  The original exception is preserved as the cause (`__cause__`).
* **BaseException Pass-Through**: System-level exceptions such as `KeyboardInterrupt`, `SystemExit`, and `GeneratorExit` are never caught or wrapped.

---

## Mutation Semantics

* **Engine Non-Mutation**: The `run_pipeline` engine itself performs no direct mutation on the input `data` or intermediate results.
* **Transform Responsibility**: The mutation behavior of each step is governed entirely by the transform implementation. If transforms use copy-on-write functions (like `set_path`), data remains unmodified. If a custom transform mutates a mutable dictionary or list in-place, the underlying object is mutated.
* **No Deep Copying**: The engine does not perform automatic deep-copying before or between steps.
* **No Rollback/Transactions**: If a step fails mid-pipeline, previous steps are not rolled back.

---

## Composition Example

Consumer application code can compose foundational `core` functions with domain-specific primitives (such as `text` or `compute`) without creating coupling inside `core`:

```python
from llm_data_utils.core import (
    PipelineStep,
    get_path,
    run_pipeline,
    set_path,
)
from llm_data_utils.exceptions import ValidationError
from llm_data_utils.models import NormalizedData
from llm_data_utils.text import convert_case, trim_text


def trim_user_name(data: NormalizedData) -> NormalizedData:
    name = get_path(data, ("user", "name"))
    if not isinstance(name, str):
        raise ValidationError("Expected string for user name.")
    return set_path(data, ("user", "name"), trim_text(name))


def uppercase_user_name(data: NormalizedData) -> NormalizedData:
    name = get_path(data, ("user", "name"))
    if not isinstance(name, str):
        raise ValidationError("Expected string for user name.")
    return set_path(data, ("user", "name"), convert_case(name, "upper"))


source_data: NormalizedData = {
    "user": {
        "name": "   Jona   ",
    }
}

pipeline = (
    PipelineStep("trim-name", trim_user_name),
    PipelineStep("uppercase-name", uppercase_user_name),
)

result = run_pipeline(source_data, pipeline)

# Result:
# {
#     "user": {
#         "name": "JONA",
#     }
# }
```

---

## Scope

The Day 13 linear pipeline is intentionally minimal. It explicitly does **not** provide:

* Asynchronous execution (`async` / `await`)
* Parallel or multi-threaded execution
* Conditional branching or fallback routes
* Directed Acyclic Graphs (DAGs) or execution graphs
* Automatic retry policies
* Transactional rollback or savepoints
* Distributed tracing or telemetry
* Execution metrics or profiling
* Intermediate result caching or memoization
* LLM provider execution or prompt orchestration
* Runtime recursive deep-validation of arbitrary transform return values
