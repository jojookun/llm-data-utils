"""Type definitions and contracts for normalized data structures."""

from typing import TypeAlias

__all__ = [
    "DataPath",
    "NormalizedData",
    "PathSegment",
    "ScalarValue",
]

ScalarValue: TypeAlias = str | int | float | bool | None

NormalizedData: TypeAlias = (
    ScalarValue | list["NormalizedData"] | dict[str, "NormalizedData"]
)

PathSegment: TypeAlias = str | int

DataPath: TypeAlias = tuple[PathSegment, ...]
