"""Type definitions and contracts for normalized data structures."""

from typing import TypeAlias

__all__ = [
    "NormalizedData",
    "ScalarValue",
]

ScalarValue: TypeAlias = str | int | float | bool | None

NormalizedData: TypeAlias = (
    ScalarValue | list["NormalizedData"] | dict[str, "NormalizedData"]
)
