"""Invoice creation."""

import re

from app.common.text import normalize_whitespace


def build_invoice(email: str, title: str, amount: int) -> dict:
    """Build an invoice payload for the given customer email."""
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise ValueError(f"invalid email: {email!r}")
    if amount <= 0:
        raise ValueError(f"amount must be positive: {amount}")
    return {"email": email, "title": normalize_whitespace(title), "amount": amount}
