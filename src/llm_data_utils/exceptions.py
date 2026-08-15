"""Public exception hierarchy for llm-data-utils."""

__all__ = [
    "ConfigurationError",
    "LLMDataUtilsError",
    "ProcessingError",
    "ValidationError",
]


class LLMDataUtilsError(Exception):
    """Base exception for all errors raised by the llm-data-utils library."""


class ValidationError(LLMDataUtilsError):
    """Raised when data validation, type constraints, or input checks fail."""


class ProcessingError(LLMDataUtilsError):
    """Raised when data manipulation, text processing, or computation fails."""


class ConfigurationError(LLMDataUtilsError):
    """Raised when library settings, environment configuration, or options are invalid."""
