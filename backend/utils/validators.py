"""
Input Validators
================
Centralised validation helpers used by route handlers.
"""

MAX_TICKET_LENGTH = 5000   # characters


def validate_ticket_input(data: dict | None) -> str | None:
    """
    Validates the JSON body for the /process-ticket and /translate-only endpoints.

    Args:
        data: Parsed JSON body (or None if parsing failed).

    Returns:
        An error message string if validation fails, or None if input is valid.
    """
    if not data:
        return "Request body must be valid JSON."

    if "ticket_text" not in data:
        return "Missing required field: 'ticket_text'."

    ticket_text = data["ticket_text"]

    if not isinstance(ticket_text, str):
        return "Field 'ticket_text' must be a string."

    if not ticket_text.strip():
        return "Field 'ticket_text' cannot be empty or whitespace."

    if len(ticket_text) > MAX_TICKET_LENGTH:
        return f"Field 'ticket_text' exceeds maximum length of {MAX_TICKET_LENGTH} characters."

    return None  # All good
