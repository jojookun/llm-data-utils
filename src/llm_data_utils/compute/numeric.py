"""Predictable numeric computation and aggregation utilities."""

import math
from collections.abc import Sequence
from typing import TypeAlias

from llm_data_utils.exceptions import ProcessingError, ValidationError

__all__ = [
    "NumericValue",
    "mean_values",
    "percentage",
    "safe_divide",
    "sum_values",
]

NumericValue: TypeAlias = int | float


def _validate_numeric(value: object, location: str) -> None:
    """Validate that a value is a finite int or float (excluding bool)."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(
            f"Expected int or float for {location}, got {type(value).__name__}."
        )
    if isinstance(value, float) and not math.isfinite(value):
        raise ValidationError(
            f"Expected finite number for {location}, got non-finite float."
        )


def _validate_sequence(values: object) -> None:
    """Validate that the values container is a list or tuple of valid NumericValues."""
    if not isinstance(values, (list, tuple)):
        raise ValidationError(
            f"Expected list or tuple for 'values', got {type(values).__name__}."
        )
    for i, val in enumerate(values):
        _validate_numeric(val, f"values[{i}]")


def sum_values(
    values: Sequence[NumericValue],
) -> NumericValue:
    """Sum a sequence of numeric values.

    Args:
        values: A list or tuple of finite integer or float numbers.

    Returns:
        The sum of the values as an int or float, preserving integer type
        when all values are integers. Returns 0 for an empty sequence.

    Raises:
        ValidationError: If values is not a list/tuple or contains non-numeric / non-finite items.
        ProcessingError: If arithmetic summation results in an unrepresentable or non-finite value.
    """
    _validate_sequence(values)

    if len(values) == 0:
        return 0

    try:
        total: NumericValue = 0
        for val in values:
            total = total + val
    except (OverflowError, ArithmeticError) as exc:
        raise ProcessingError(f"Arithmetic overflow during summation: {exc}") from exc

    if isinstance(total, float) and not math.isfinite(total):
        raise ProcessingError("Summation resulted in a non-finite value.")

    return total


def mean_values(
    values: Sequence[NumericValue],
) -> float:
    """Calculate the arithmetic mean of a sequence of numeric values.

    Args:
        values: A non-empty list or tuple of finite integer or float numbers.

    Returns:
        The arithmetic mean as a float.

    Raises:
        ValidationError: If values is empty, not a list/tuple, or contains non-numeric / non-finite items.
        ProcessingError: If arithmetic mean calculation results in an unrepresentable or non-finite value.
    """
    _validate_sequence(values)

    if len(values) == 0:
        raise ValidationError(
            "Expected non-empty sequence for 'values', got empty sequence."
        )

    total = sum_values(values)
    try:
        result = total / len(values)
    except (OverflowError, ArithmeticError) as exc:
        raise ProcessingError(f"Arithmetic overflow during mean calculation: {exc}") from exc

    if not math.isfinite(result):
        raise ProcessingError("Mean calculation resulted in a non-finite value.")

    return result


def safe_divide(
    numerator: NumericValue,
    denominator: NumericValue,
) -> float:
    """Safely divide two numbers, returning a float.

    Args:
        numerator: The dividend (finite int or float).
        denominator: The divisor (finite non-zero int or float).

    Returns:
        The division result as a float.

    Raises:
        ValidationError: If operands are invalid or denominator is zero.
        ProcessingError: If division produces an arithmetic overflow or non-finite result.
    """
    _validate_numeric(numerator, "'numerator'")
    _validate_numeric(denominator, "'denominator'")

    if denominator == 0:
        raise ValidationError("Denominator cannot be zero.")

    try:
        result = numerator / denominator
    except (OverflowError, ArithmeticError) as exc:
        raise ProcessingError(f"Arithmetic overflow during division: {exc}") from exc

    if not math.isfinite(result):
        raise ProcessingError("Division resulted in a non-finite value.")

    return result


def percentage(
    part: NumericValue,
    whole: NumericValue,
) -> float:
    """Calculate the percentage of part relative to whole ((part / whole) * 100).

    Args:
        part: The subset value (finite int or float).
        whole: The baseline value (finite non-zero int or float).

    Returns:
        The calculated percentage as a float.

    Raises:
        ValidationError: If operands are invalid or whole is zero.
        ProcessingError: If percentage calculation produces an arithmetic overflow or non-finite result.
    """
    div_result = safe_divide(part, whole)

    try:
        result = div_result * 100.0
    except (OverflowError, ArithmeticError) as exc:
        raise ProcessingError(f"Arithmetic overflow during percentage calculation: {exc}") from exc

    if not math.isfinite(result):
        raise ProcessingError("Percentage calculation resulted in a non-finite value.")

    return result
