"""Deterministic substring search and source-offset-preserving matching."""

from llm_data_utils.exceptions import ValidationError
from llm_data_utils.models import TextMatch

__all__ = ["find_matches"]


def _validate_str(value: object, param_name: str) -> None:
    """Validate that a parameter is a string."""
    if not isinstance(value, str):
        raise ValidationError(
            f"Expected str for {param_name!r}, got {type(value).__name__}."
        )


def _validate_query(query: object) -> None:
    """Validate that query is a non-empty string."""
    if not isinstance(query, str):
        raise ValidationError(
            f"Expected str for 'query', got {type(query).__name__}."
        )
    if len(query) == 0:
        raise ValidationError(
            "Expected non-empty str for 'query', got empty string."
        )


def _validate_bool(value: object, param_name: str) -> None:
    """Validate that a parameter is a boolean."""
    if not isinstance(value, bool):
        raise ValidationError(
            f"Expected bool for {param_name!r}, got {type(value).__name__}."
        )


def find_matches(
    text: str,
    query: str,
    *,
    case_sensitive: bool = True,
) -> list[TextMatch]:
    """Find occurrences of a query string within text, preserving original source offsets.

    Args:
        text: The source string to search within.
        query: The non-empty search string to look for.
        case_sensitive: If True, performs exact character matching. If False, performs
            Unicode-aware casefold matching while preserving original source offsets.
            Defaults to True.

    Returns:
        A list of immutable TextMatch instances representing all matches found
        (including overlapping occurrences), in left-to-right source order.
        Returns an empty list if the input text is empty or no matches exist.

    Raises:
        ValidationError: If text or query is not a string, query is empty,
            or case_sensitive is not a boolean.
    """
    _validate_str(text, "text")
    _validate_query(query)
    _validate_bool(case_sensitive, "case_sensitive")

    text_len = len(text)
    if text_len == 0:
        return []

    matches: list[TextMatch] = []
    match_index = 0

    if case_sensitive:
        query_len = len(query)
        pos = 0
        while True:
            idx = text.find(query, pos)
            if idx == -1:
                break
            end = idx + query_len
            matches.append(
                TextMatch(
                    text=text[idx:end],
                    start=idx,
                    end=end,
                    index=match_index,
                )
            )
            match_index += 1
            pos = idx + 1
    else:
        folded_query = query.casefold()
        target_len = len(folded_query)

        for start in range(text_len):
            max_end = min(text_len, start + target_len)
            for end in range(start + 1, max_end + 1):
                candidate = text[start:end]
                folded_candidate = candidate.casefold()
                if folded_candidate == folded_query:
                    matches.append(
                        TextMatch(
                            text=candidate,
                            start=start,
                            end=end,
                            index=match_index,
                        )
                    )
                    match_index += 1
                    break
                if len(folded_candidate) > target_len:
                    break

    return matches
