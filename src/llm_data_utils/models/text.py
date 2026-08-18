"""Data models and structures for text processing."""

from dataclasses import dataclass

__all__ = [
    "TextChunk",
    "TextMatch",
]


@dataclass(frozen=True, slots=True)
class TextChunk:
    """Immutable chunk of text with source offset metadata.

    Attributes:
        text: The chunk string slice from the source text.
        start: Inclusive start character index in the source text.
        end: Exclusive end character index in the source text.
        index: Zero-based sequence index of the chunk.
    """

    text: str
    start: int
    end: int
    index: int


@dataclass(frozen=True, slots=True)
class TextMatch:
    """A matched slice of source text.

    Attributes:
        text: Exact matched slice from the source text.
        start: Inclusive start character index in the source text.
        end: Exclusive end character index in the source text.
        index: Zero-based sequence index of the match.
    """

    text: str
    start: int
    end: int
    index: int
