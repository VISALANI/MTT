"""
Tests 2–6 — Input validation layer
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from utils.validators import validate_ticket_input


def test_valid_input():
    """Valid input should return None (no error)."""
    result = validate_ticket_input({"ticket_text": "My internet is not working"})
    assert result is None


def test_missing_ticket_text_key():
    """Body without ticket_text key should return an error."""
    result = validate_ticket_input({"message": "something"})
    assert result is not None
    assert 'ticket_text' in result


def test_empty_ticket_text():
    """Empty string should be rejected."""
    result = validate_ticket_input({"ticket_text": "   "})
    assert result is not None
    assert 'empty' in result.lower()


def test_none_body():
    """None body (failed JSON parse) should return an error."""
    result = validate_ticket_input(None)
    assert result is not None
    assert 'JSON' in result or 'body' in result.lower()


def test_text_exceeds_max_length():
    """Text over 5000 chars should be rejected."""
    long_text = "a" * 5001
    result = validate_ticket_input({"ticket_text": long_text})
    assert result is not None
    assert '5000' in result


def test_non_string_ticket_text():
    """Non-string value for ticket_text should be rejected."""
    result = validate_ticket_input({"ticket_text": 12345})
    assert result is not None
    assert 'string' in result.lower()
