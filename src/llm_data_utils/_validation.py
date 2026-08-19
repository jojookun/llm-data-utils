"""Internal runtime validation primitives for primitive types."""

from llm_data_utils.exceptions import ValidationError

__all__ = [
    "_require_bool",
    "_require_non_bool_int",
    "_require_str",
]


def _require_str(
    value: object,
    *,
    name: str,
) -> str:
    """Validate that a value is a string and return it.

    Args:
        value: The object to validate.
        name: The parameter name for error reporting.

    Returns:
        The validated string.

    Raises:
        ValidationError: If value is not a string.
    """
    if not isinstance(value, str):
        raise ValidationError(
            f"Expected str for {name!r}, got {type(value).__name__}."
        )
    return value


def _require_bool(
    value: object,
    *,
    name: str,
) -> bool:
    """Validate that a value is a boolean and return it.

    Args:
        value: The object to validate.
        name: The parameter name for error reporting.

    Returns:
        The validated boolean.

    Raises:
        ValidationError: If value is not a boolean.
    """
    if not isinstance(value, bool):
        raise ValidationError(
            f"Expected bool for {name!r}, got {type(value).__name__}."
        )
    return value


def _require_non_bool_int(
    value: object,
    *,
    name: str,
) -> int:
    """Validate that a value is an integer (excluding bool) and return it.

    Args:
        value: The object to validate.
        name: The parameter name for error reporting.

    Returns:
        The validated integer.

    Raises:
        ValidationError: If value is a boolean or not an integer.
    """
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError(
            f"Expected int for {name!r}, got {type(value).__name__}."
        )
    return value
