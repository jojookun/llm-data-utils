"""Deterministic fixed-width text chunking and segmentation."""

from llm_data_utils._validation import _require_non_bool_int, _require_str
from llm_data_utils.exceptions import ValidationError
from llm_data_utils.models import TextChunk

__all__ = ["chunk_text"]


def _validate_chunk_size(chunk_size: object) -> None:
    """Validate that chunk_size is a positive integer (excluding bool)."""
    val = _require_non_bool_int(chunk_size, name="chunk_size")
    if val <= 0:
        raise ValidationError(
            f"Expected positive int for 'chunk_size', got {val}."
        )


def _validate_overlap(overlap: object, chunk_size: int) -> None:
    """Validate that overlap is a non-negative integer strictly less than chunk_size."""
    val = _require_non_bool_int(overlap, name="overlap")
    if val < 0:
        raise ValidationError(
            f"Expected non-negative int for 'overlap', got {val}."
        )
    if val >= chunk_size:
        raise ValidationError(
            f"Expected 'overlap' to be strictly less than 'chunk_size' ({chunk_size}), got {val}."
        )


def chunk_text(
    text: str,
    *,
    chunk_size: int,
    overlap: int = 0,
) -> list[TextChunk]:
    """Deterministically split text into fixed-width character chunks with source offsets.

    Args:
        text: The source string to chunk.
        chunk_size: Maximum number of characters per chunk (must be > 0).
        overlap: Number of characters to overlap between consecutive chunks (must be >= 0
            and < chunk_size). Defaults to 0.

    Returns:
        A list of immutable TextChunk instances containing text slices and source offsets.
        Returns an empty list if the input text is empty.

    Raises:
        ValidationError: If text is not a string, chunk_size is not a positive int,
            overlap is not a non-negative int, or overlap is >= chunk_size.
    """
    _require_str(text, name="text")
    _validate_chunk_size(chunk_size)
    _validate_overlap(overlap, chunk_size)

    text_len = len(text)
    if text_len == 0:
        return []

    step = chunk_size - overlap
    chunks: list[TextChunk] = []
    start = 0
    index = 0

    while True:
        end = min(start + chunk_size, text_len)
        chunks.append(
            TextChunk(
                text=text[start:end],
                start=start,
                end=end,
                index=index,
            )
        )
        if end == text_len:
            break
        start += step
        index += 1

    return chunks
