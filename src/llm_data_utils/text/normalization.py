"""Fundamental string normalization primitives for text processing pipelines."""

import re
import unicodedata
from typing import Literal

from llm_data_utils._validation import _require_str
from llm_data_utils.exceptions import ValidationError

__all__ = [
    "CaseMode",
    "UnicodeForm",
    "convert_case",
    "normalize_unicode",
    "normalize_whitespace",
    "trim_text",
]

UnicodeForm = Literal["NFC", "NFD", "NFKC", "NFKD"]

CaseMode = Literal[
    "lower",
    "upper",
    "casefold",
]

_VALID_UNICODE_FORMS = frozenset({"NFC", "NFD", "NFKC", "NFKD"})
_VALID_CASE_MODES = frozenset({"lower", "upper", "casefold"})
_WHITESPACE_REGEX = re.compile(r"\s+")


def trim_text(text: str) -> str:
    """Remove leading and trailing whitespace from text while preserving internal content.

    Args:
        text: The input string to trim.

    Returns:
        The string with leading and trailing whitespace removed.

    Raises:
        ValidationError: If text is not a string.
    """
    _require_str(text, name="text")
    return text.strip()


def normalize_whitespace(text: str) -> str:
    """Collapse consecutive Unicode whitespace runs into single ASCII spaces.

    This function preserves the presence of leading or trailing whitespace
    (collapsing leading/trailing runs to a single space) without trimming.

    Args:
        text: The input string to normalize.

    Returns:
        The string with all consecutive whitespace sequences collapsed to single spaces.

    Raises:
        ValidationError: If text is not a string.
    """
    _require_str(text, name="text")
    return _WHITESPACE_REGEX.sub(" ", text)


def normalize_unicode(text: str, form: UnicodeForm = "NFC") -> str:
    """Normalize text into a standard Unicode canonical or compatibility form.

    Args:
        text: The input string to normalize.
        form: The Unicode normalization form ('NFC', 'NFD', 'NFKC', or 'NFKD').
            Defaults to 'NFC'.

    Returns:
        The normalized Unicode string.

    Raises:
        ValidationError: If text is not a string or form is not a valid Unicode form.
    """
    _require_str(text, name="text")
    _require_str(form, name="form")
    if form not in _VALID_UNICODE_FORMS:
        raise ValidationError(
            f"Invalid Unicode normalization form: {form!r}. "
            "Expected one of: 'NFC', 'NFD', 'NFKC', 'NFKD'."
        )
    return unicodedata.normalize(form, text)


def convert_case(text: str, mode: CaseMode) -> str:
    """Convert text case using a specified case mapping mode.

    Args:
        text: The input string to convert.
        mode: The conversion mode ('lower', 'upper', or 'casefold').

    Returns:
        The converted string.

    Raises:
        ValidationError: If text is not a string or mode is not a valid CaseMode.
    """
    _require_str(text, name="text")
    _require_str(mode, name="mode")
    if mode not in _VALID_CASE_MODES:
        raise ValidationError(
            f"Invalid case conversion mode: {mode!r}. "
            "Expected one of: 'lower', 'upper', 'casefold'."
        )
    if mode == "lower":
        return text.lower()
    if mode == "upper":
        return text.upper()
    return text.casefold()
