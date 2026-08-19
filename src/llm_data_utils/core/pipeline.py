"""Synchronous linear processing pipeline for normalized data structures."""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import TypeAlias

from llm_data_utils._validation import _require_str
from llm_data_utils.exceptions import (
    LLMDataUtilsError,
    ProcessingError,
    ValidationError,
)
from llm_data_utils.models import NormalizedData

__all__ = [
    "DataTransform",
    "PipelineStep",
    "run_pipeline",
]

DataTransform: TypeAlias = Callable[
    [NormalizedData],
    NormalizedData,
]


@dataclass(frozen=True, slots=True)
class PipelineStep:
    """An immutable, named transformation step in a processing pipeline.

    Attributes:
        name: A unique, non-empty identifier for the pipeline step.
        transform: A callable accepting and returning NormalizedData.
    """

    name: str
    transform: DataTransform

    def __post_init__(self) -> None:
        """Validate step attributes upon initialization."""
        _require_str(self.name, name="name")
        if not self.name.strip():
            raise ValidationError(
                f"Step name must be a non-empty str with non-whitespace characters, got {self.name!r}."
            )
        if not callable(self.transform):
            raise ValidationError(
                f"Step transform must be callable, got {type(self.transform).__name__}."
            )


def run_pipeline(
    data: NormalizedData,
    steps: Sequence[PipelineStep],
) -> NormalizedData:
    """Execute a sequential processing pipeline over normalized data.

    All pipeline steps and names are validated before any step is executed.
    Steps execute sequentially, passing the output of each step as input to the next.

    Args:
        data: The initial normalized data structure.
        steps: A list or tuple of PipelineStep instances with unique names.

    Returns:
        The final transformed NormalizedData structure, or the original data if steps is empty.

    Raises:
        ValidationError: If steps container is not a list/tuple, contains non-PipelineStep
            elements, contains duplicate step names, or if a step raises a ValidationError.
        ProcessingError: If a step raises an unexpected exception (wrapped with step identification)
            or an existing ProcessingError.
        LLMDataUtilsError: If a step raises any other library exception (re-raised unchanged).
    """
    if not isinstance(steps, (list, tuple)):
        raise ValidationError(
            f"Expected list or tuple for 'steps', got {type(steps).__name__}."
        )

    seen_names: set[str] = set()
    for i, step in enumerate(steps):
        if not isinstance(step, PipelineStep):
            raise ValidationError(
                f"Expected PipelineStep at index {i}, got {type(step).__name__}."
            )
        if step.name in seen_names:
            raise ValidationError(
                f"Duplicate pipeline step name: {step.name!r}."
            )
        seen_names.add(step.name)

    current: NormalizedData = data
    for step in steps:
        try:
            current = step.transform(current)
        except LLMDataUtilsError:
            raise
        except Exception as exc:
            raise ProcessingError(
                f"Pipeline step {step.name!r} failed."
            ) from exc

    return current
