"""Controlled string transformation and replacement primitives."""

import re

from llm_data_utils._validation import _require_non_bool_int, _require_str
from llm_data_utils.exceptions import ValidationError

__all__ = [
    "remove_pattern",
    "replace_pattern",
    "replace_text",
]


def _validate_count(count: object) -> None:
    """Validate that the count argument is a non-negative int or None (excluding bool)."""
    if count is None:
        return
    val = _require_non_bool_int(count, name="count")
    if val < 0:
        raise ValidationError(
            f"Expected non-negative int or None for 'count', got {val}."
        )


def _validate_flags(flags: object) -> None:
    """Validate that flags is an instance of re.RegexFlag."""
    if not isinstance(flags, re.RegexFlag):
        raise ValidationError(
            f"Expected re.RegexFlag for 'flags', got {type(flags).__name__}."
        )


def replace_text(
    text: str,
    old: str,
    new: str,
    *,
    count: int | None = None,
) -> str:
    """Replace occurrences of a literal substring within text.

    Args:
        text: The source string to process.
        old: The literal substring to search for.
        new: The literal replacement substring.
        count: Maximum number of occurrences to replace. If None, replaces all occurrences.
            If 0, returns the text unchanged. Defaults to None.

    Returns:
        The string with replacements applied.

    Raises:
        ValidationError: If text, old, or new is not a string, or count is invalid.
    """
    _require_str(text, name="text")
    _require_str(old, name="old")
    _require_str(new, name="new")
    _validate_count(count)

    if count == 0:
        return text
    if count is None:
        return text.replace(old, new)
    return text.replace(old, new, count)


def replace_pattern(
    text: str,
    pattern: str,
    replacement: str,
    *,
    count: int | None = None,
    flags: re.RegexFlag = re.NOFLAG,
) -> str:
    """Replace occurrences of a regular expression pattern within text.

    Args:
        text: The source string to process.
        pattern: The regular expression pattern to search for.
        replacement: The replacement string (supports backreferences like \\1, \\g<1>).
        count: Maximum number of occurrences to replace. If None, replaces all occurrences.
            If 0, returns the text unchanged after validating the pattern and
            replacement template. Defaults to None.
        flags: Regular expression compilation flags (e.g. re.IGNORECASE). Defaults to re.NOFLAG.

    Returns:
        The string with pattern replacements applied.

    Raises:
        ValidationError: If text, pattern, or replacement is not a string, count or flags
            is invalid, or if the pattern syntax or replacement template is malformed.
    """
    _require_str(text, name="text")
    _require_str(pattern, name="pattern")
    _require_str(replacement, name="replacement")
    _validate_count(count)
    _validate_flags(flags)

    try:
        compiled = re.compile(pattern, flags=flags)
    except re.error as exc:
        raise ValidationError(
            f"Invalid regular expression pattern: {exc.msg}"
        ) from exc

    if count == 0:
        try:
            compiled.sub(replacement, "")
        except re.error as exc:
            raise ValidationError(
                f"Invalid regular expression replacement template: {exc.msg}"
            ) from exc
        except (IndexError, ValueError) as exc:
            raise ValidationError(
                "Invalid regular expression replacement template."
            ) from exc
        return text

    re_count = 0 if count is None else count
    try:
        return compiled.sub(replacement, text, count=re_count)
    except re.error as exc:
        raise ValidationError(
            f"Invalid regular expression replacement template: {exc.msg}"
        ) from exc
    except (IndexError, ValueError) as exc:
        raise ValidationError(
            "Invalid regular expression replacement template."
        ) from exc


def remove_pattern(
    text: str,
    pattern: str,
    *,
    count: int | None = None,
    flags: re.RegexFlag = re.NOFLAG,
) -> str:
    """Remove occurrences of a regular expression pattern from text.

    Args:
        text: The source string to process.
        pattern: The regular expression pattern to remove.
        count: Maximum number of occurrences to remove. If None, removes all occurrences.
            If 0, returns the text unchanged after verifying pattern validity. Defaults to None.
        flags: Regular expression compilation flags (e.g. re.IGNORECASE). Defaults to re.NOFLAG.

    Returns:
        The string with matched patterns removed.

    Raises:
        ValidationError: If text or pattern is not a string, count or flags is invalid,
            or if the pattern syntax is malformed.
    """
    return replace_pattern(text, pattern, "", count=count, flags=flags)
