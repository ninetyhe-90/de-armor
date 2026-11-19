"""Text helpers shared across modules."""


def normalize_whitespace(value: str) -> str:
    """Collapse runs of whitespace into single spaces."""
    return " ".join(value.split())
