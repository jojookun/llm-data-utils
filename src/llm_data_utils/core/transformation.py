"""Deterministic structured-data path traversal and transformation."""

from llm_data_utils.exceptions import ValidationError
from llm_data_utils.models import DataPath, NormalizedData

__all__ = [
    "get_path",
    "remove_path",
    "set_path",
]


def _validate_path(path: object) -> None:
    """Validate that path is a tuple of str and int segments (excluding bool)."""
    if not isinstance(path, tuple):
        raise ValidationError(
            f"Expected tuple for 'path', got {type(path).__name__}."
        )
    for seg in path:
        if isinstance(seg, bool) or not isinstance(seg, (str, int)):
            raise ValidationError(
                f"Expected str or int for path segment, got {type(seg).__name__}."
            )


def _format_path(path: tuple[object, ...]) -> str:
    """Format a path tuple into a diagnostic string."""
    formatted = "$"
    for seg in path:
        if isinstance(seg, int) and not isinstance(seg, bool):
            formatted += f"[{seg}]"
        else:
            formatted += f"[{seg!r}]"
    return formatted


def get_path(
    data: NormalizedData,
    path: DataPath,
) -> NormalizedData:
    """Retrieve the value located at a specific path in normalized data.

    Args:
        data: The root normalized data structure to traverse.
        path: A tuple of string keys and integer indices. Empty tuple () returns data.

    Returns:
        The normalized value located at the specified path.

    Raises:
        ValidationError: If path is malformed, segment types do not match container
            types, negative indices are used, a key/index is missing, or traversal
            attempts to index into a scalar.
    """
    _validate_path(path)

    current: NormalizedData = data
    for i, seg in enumerate(path):
        current_loc = _format_path(path[:i])
        if isinstance(current, dict):
            if not isinstance(seg, str):
                raise ValidationError(
                    f"Expected str key for mapping at {current_loc!r}, got {type(seg).__name__}."
                )
            if seg not in current:
                raise ValidationError(
                    f"Key {seg!r} not found at {current_loc!r}."
                )
            current = current[seg]
        elif isinstance(current, list):
            if isinstance(seg, bool) or not isinstance(seg, int):
                raise ValidationError(
                    f"Expected int index for sequence at {current_loc!r}, got {type(seg).__name__}."
                )
            if seg < 0:
                raise ValidationError(
                    f"Negative index {seg} is not supported at {current_loc!r}."
                )
            if seg >= len(current):
                raise ValidationError(
                    f"Index {seg} out of range at {current_loc!r} (length {len(current)})."
                )
            current = current[seg]
        else:
            raise ValidationError(
                f"Cannot traverse into non-container value at {current_loc!r}."
            )

    return current


def set_path(
    data: NormalizedData,
    path: DataPath,
    value: NormalizedData,
) -> NormalizedData:
    """Return a copy of data with the value at the specified path updated.

    Performs copy-on-write along the modified path without mutating the input data.
    All path segments must already exist in the structure.

    Args:
        data: The root normalized data structure to transform.
        path: A tuple of string keys and integer indices. Empty tuple () replaces root.
        value: The new normalized data value to insert.

    Returns:
        A new data structure with the path updated.

    Raises:
        ValidationError: If path is malformed, target path does not exist,
            segment types do not match container types, negative indices are used,
            or traversal attempts to index into a scalar.
    """
    _validate_path(path)

    if not path:
        return value

    def _set_recursive(
        current: NormalizedData,
        remaining_path: tuple[object, ...],
        prefix: tuple[object, ...],
    ) -> NormalizedData:
        seg = remaining_path[0]
        current_loc = _format_path(prefix)

        if isinstance(current, dict):
            if not isinstance(seg, str):
                raise ValidationError(
                    f"Expected str key for mapping at {current_loc!r}, got {type(seg).__name__}."
                )
            if seg not in current:
                raise ValidationError(
                    f"Key {seg!r} not found at {current_loc!r}."
                )
            new_dict = dict(current)
            if len(remaining_path) == 1:
                new_dict[seg] = value
            else:
                new_dict[seg] = _set_recursive(
                    current[seg],
                    remaining_path[1:],
                    prefix + (seg,),
                )
            return new_dict

        if isinstance(current, list):
            if isinstance(seg, bool) or not isinstance(seg, int):
                raise ValidationError(
                    f"Expected int index for sequence at {current_loc!r}, got {type(seg).__name__}."
                )
            if seg < 0:
                raise ValidationError(
                    f"Negative index {seg} is not supported at {current_loc!r}."
                )
            if seg >= len(current):
                raise ValidationError(
                    f"Index {seg} out of range at {current_loc!r} (length {len(current)})."
                )
            new_list = list(current)
            if len(remaining_path) == 1:
                new_list[seg] = value
            else:
                new_list[seg] = _set_recursive(
                    current[seg],
                    remaining_path[1:],
                    prefix + (seg,),
                )
            return new_list

        raise ValidationError(
            f"Cannot traverse into non-container value at {current_loc!r}."
        )

    return _set_recursive(data, path, ())


def remove_path(
    data: NormalizedData,
    path: DataPath,
) -> NormalizedData:
    """Return a copy of data with the element at the specified path removed.

    Performs copy-on-write along the modified path without mutating the input data.
    The root path () cannot be removed.

    Args:
        data: The root normalized data structure to transform.
        path: A non-empty tuple of string keys and integer indices.

    Returns:
        A new data structure with the target path removed.

    Raises:
        ValidationError: If path is empty (), malformed, target path does not exist,
            segment types do not match container types, negative indices are used,
            or traversal attempts to index into a scalar.
    """
    _validate_path(path)

    if not path:
        raise ValidationError("Cannot remove root path ().")

    def _remove_recursive(
        current: NormalizedData,
        remaining_path: tuple[object, ...],
        prefix: tuple[object, ...],
    ) -> NormalizedData:
        seg = remaining_path[0]
        current_loc = _format_path(prefix)

        if isinstance(current, dict):
            if not isinstance(seg, str):
                raise ValidationError(
                    f"Expected str key for mapping at {current_loc!r}, got {type(seg).__name__}."
                )
            if seg not in current:
                raise ValidationError(
                    f"Key {seg!r} not found at {current_loc!r}."
                )
            new_dict = dict(current)
            if len(remaining_path) == 1:
                del new_dict[seg]
            else:
                new_dict[seg] = _remove_recursive(
                    current[seg],
                    remaining_path[1:],
                    prefix + (seg,),
                )
            return new_dict

        if isinstance(current, list):
            if isinstance(seg, bool) or not isinstance(seg, int):
                raise ValidationError(
                    f"Expected int index for sequence at {current_loc!r}, got {type(seg).__name__}."
                )
            if seg < 0:
                raise ValidationError(
                    f"Negative index {seg} is not supported at {current_loc!r}."
                )
            if seg >= len(current):
                raise ValidationError(
                    f"Index {seg} out of range at {current_loc!r} (length {len(current)})."
                )
            new_list = list(current)
            if len(remaining_path) == 1:
                del new_list[seg]
            else:
                new_list[seg] = _remove_recursive(
                    current[seg],
                    remaining_path[1:],
                    prefix + (seg,),
                )
            return new_list

        raise ValidationError(
            f"Cannot traverse into non-container value at {current_loc!r}."
        )

    return _remove_recursive(data, path, ())
