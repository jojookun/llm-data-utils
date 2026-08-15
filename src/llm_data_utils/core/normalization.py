"""Recursive data normalization utilities for converting Python structures into JSON-friendly format."""

import json
import math
from collections.abc import Mapping

from llm_data_utils.exceptions import ValidationError
from llm_data_utils.models import NormalizedData

__all__ = ["normalize_data"]


def _sort_key(item: NormalizedData) -> str:
    """Generate a stable, deterministic sort key for normalized data elements."""
    return json.dumps(item, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _normalize_value(
    value: object,
    path: str,
    active_ids: frozenset[int],
) -> NormalizedData:
    """Recursively normalize a single value with path and circular reference tracking."""
    # 1. Scalars
    if value is None:
        return None

    if isinstance(value, bool):
        return bool(value)

    if isinstance(value, int):
        return int(value)

    if isinstance(value, str):
        return str(value)

    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValidationError(
                f"Non-finite float value {value!r} encountered at {path}."
            )
        return float(value)

    # 2. Containers (check circular reference on active recursion path)
    if isinstance(value, (Mapping, list, tuple, set, frozenset)):
        obj_id = id(value)
        if obj_id in active_ids:
            raise ValidationError(f"Circular reference detected at {path}.")
        new_active_ids = active_ids | {obj_id}

        # Mappings -> dict[str, NormalizedData]
        if isinstance(value, Mapping):
            normalized_dict: dict[str, NormalizedData] = {}
            for key, val in value.items():
                if not isinstance(key, str):
                    raise ValidationError(
                        f"Invalid mapping key of type {type(key).__name__} at {path}: "
                        "mapping keys must be strings."
                    )
                child_path = f"{path}['{key}']"
                normalized_dict[key] = _normalize_value(
                    val, child_path, new_active_ids
                )
            return normalized_dict

        # Sequences (list, tuple) -> list[NormalizedData]
        if isinstance(value, (list, tuple)):
            normalized_list: list[NormalizedData] = []
            for idx, item in enumerate(value):
                child_path = f"{path}[{idx}]"
                normalized_list.append(
                    _normalize_value(item, child_path, new_active_ids)
                )
            return normalized_list

        # Sets -> sorted list[NormalizedData]
        if isinstance(value, (set, frozenset)):
            normalized_items: list[NormalizedData] = []
            for item in value:
                child_path = f"{path}[*]"
                normalized_items.append(
                    _normalize_value(item, child_path, new_active_ids)
                )
            normalized_items.sort(key=_sort_key)
            return normalized_items

    # 3. Unsupported Types
    raise ValidationError(
        f"Unsupported data type {type(value).__name__} encountered at {path}."
    )


def normalize_data(value: object) -> NormalizedData:
    """Recursively normalize a Python data structure into a JSON-friendly representation.

    Supported scalar types (None, bool, int, finite float, str) are preserved.
    Supported container types (Mapping, list, tuple, set) are converted into new dict
    and list instances with all elements recursively normalized.

    Sets are converted into deterministically sorted lists. Mappings require string keys.

    Args:
        value: The Python object to normalize.

    Returns:
        A new NormalizedData structure composed only of None, bool, int, float, str,
        list, and dict[str, NormalizedData].

    Raises:
        ValidationError: If an unsupported type is encountered, a float is non-finite,
            a mapping contains non-string keys, or a circular container reference is detected.
    """
    return _normalize_value(value, path="$", active_ids=frozenset())
