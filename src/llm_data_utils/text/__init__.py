"""String and text processing functionality."""

from llm_data_utils.text.chunking import chunk_text
from llm_data_utils.text.matching import find_matches
from llm_data_utils.text.normalization import (
    CaseMode,
    UnicodeForm,
    convert_case,
    normalize_unicode,
    normalize_whitespace,
    trim_text,
)
from llm_data_utils.text.transformation import (
    remove_pattern,
    replace_pattern,
    replace_text,
)

__all__ = [
    "CaseMode",
    "UnicodeForm",
    "chunk_text",
    "convert_case",
    "find_matches",
    "normalize_unicode",
    "normalize_whitespace",
    "remove_pattern",
    "replace_pattern",
    "replace_text",
    "trim_text",
]
