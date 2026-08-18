# Computation Utilities

The `llm-data-utils` library provides predictable, provider-independent numeric computation and aggregation primitives designed for data pipelines, metric calculation, and token accounting.

---

## Public API

```python
from llm_data_utils.compute import (
    NumericValue,
    mean_values,
    percentage,
    safe_divide,
    sum_values,
)
```

---

## Numeric Contract

The public type alias is defined as:

```python
NumericValue = int | float
```

### Runtime Validation Rules

* **Finite Numbers Only**: `float("nan")`, `float("inf")`, and `float("-inf")` are rejected with [`ValidationError`](../src/llm_data_utils/exceptions.py).
* **Strict Boolean Exclusion**: In Python, `bool` is a subclass of `int`. To prevent silent type bugs, `True` and `False` are strictly rejected.
* **No Implicit Coercion**: Strings (e.g. `"10"`), `None`, and arbitrary non-numeric objects are not automatically converted.

---

## Supported Aggregation Containers

Aggregation functions (`sum_values`, `mean_values`) operate strictly on concrete sequences:

* **`list`**
* **`tuple`**

Unordered collections (e.g. `set`), mappings (`dict`), and arbitrary iterators or generators are intentionally disallowed at runtime to ensure deterministic and repeatable computations.

---

## Operations

### 1. Summation (`sum_values`)

Sums a sequence of numeric values:

```python
sum_values([1, 2, 3])     # 6
sum_values([1, 2.5, 3])   # 6.5
sum_values([])            # 0
```

* Preserves `int` return type when all inputs are integers.
* Returns `0` for empty lists or tuples.

### 2. Arithmetic Mean (`mean_values`)

Calculates the arithmetic mean of a sequence of numeric values:

```python
mean_values([1, 2, 3])    # 2.0
mean_values((1.0, 2.0))   # 1.5
```

* Always returns a `float`.
* Passing an empty sequence raises `ValidationError`.

### 3. Safe Division (`safe_divide`)

Divides numerator by denominator and returns a float:

```python
safe_divide(10, 4)        # 2.5
safe_divide(0, 10)        # 0.0
safe_divide(-10, 4)       # -2.5
```

* Denominator equal to `0`, `0.0`, or `-0.0` raises `ValidationError`.
* Returns `float`.

### 4. Percentage (`percentage`)

Calculates `(part / whole) * 100`:

```python
percentage(25, 100)       # 25.0
percentage(1, 4)          # 25.0
percentage(-10, 100)      # -10.0
```

* Negative values and values outside `0..100` are permitted without clamping.
* Does not perform automatic rounding (e.g. `percentage(1, 3)` returns `33.333333333333336`).
* Passing `whole=0` raises `ValidationError`.

---

## Error Boundaries

The compute module cleanly delineates between input errors and arithmetic overflow:

| Exception | Condition |
| :--- | :--- |
| **`ValidationError`** | Non-numeric input, `bool` values, `NaN`/`inf`/`-inf`, invalid container types (non list/tuple), empty sequence in `mean_values`, or division by zero (`denominator=0`). |
| **`ProcessingError`** | Valid finite inputs produce an unrepresentable arithmetic overflow or non-finite result during calculation. |
