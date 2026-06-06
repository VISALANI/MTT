"""
Tests 12–17 — AI Analysis service
All Gemini calls are mocked.
"""

import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from unittest.mock import patch
from services.analysis_service import (
    parse_gemini_json,
    validate_and_normalise,
    analyze_ticket,
)


# ── parse_gemini_json ─────────────────────────────────────────────────────────

def test_parse_clean_json():
    """Should parse a clean JSON string correctly."""
    raw = '{"category": "Network Issue", "priority": "High", "summary": "test", "sentiment": "Negative", "response": "We will fix this.", "keywords": ["internet"]}'
    result = parse_gemini_json(raw)
    assert result['category'] == 'Network Issue'
    assert result['priority'] == 'High'


def test_parse_json_with_markdown_fences():
    """Should strip ```json ... ``` fences before parsing."""
    raw = '```json\n{"category": "Billing Issue", "priority": "Medium", "summary": "s", "sentiment": "Neutral", "response": "r", "keywords": []}\n```'
    result = parse_gemini_json(raw)
    assert result['category'] == 'Billing Issue'


def test_parse_invalid_json_raises():
    """Should raise ValueError for completely unparseable text."""
    import pytest
    with pytest.raises(ValueError):
        parse_gemini_json("This is not JSON at all, sorry.")


# ── validate_and_normalise ────────────────────────────────────────────────────

def test_normalise_valid_data():
    """Valid data should pass through unchanged."""
    data = {
        "category": "Network Issue",
        "priority": "High",
        "summary": "Internet down.",
        "sentiment": "Negative",
        "response": "We are on it.",
        "keywords": ["internet", "down"],
    }
    result = validate_and_normalise(data)
    assert result['category'] == 'Network Issue'
    assert result['priority'] == 'High'


def test_normalise_invalid_category_defaults_to_other():
    """Unknown category should default to 'Other'."""
    data = {"category": "Fake Category", "priority": "Low",
            "summary": "s", "sentiment": "Neutral", "response": "r", "keywords": []}
    result = validate_and_normalise(data)
    assert result['category'] == 'Other'


def test_normalise_caps_keywords_at_five():
    """Keywords list should be capped at 5 items."""
    data = {"category": "Other", "priority": "Low", "summary": "s",
            "sentiment": "Neutral", "response": "r",
            "keywords": ["a", "b", "c", "d", "e", "f", "g"]}
    result = validate_and_normalise(data)
    assert len(result['keywords']) == 5


# ── analyze_ticket (integration, Gemini mocked) ───────────────────────────────

def test_analyze_ticket_full_flow():
    """analyze_ticket should return all required keys with a mocked Gemini."""
    mock_response = json.dumps({
        "category": "Network Issue",
        "priority": "Medium",
        "summary": "Customer reports internet not working.",
        "sentiment": "Negative",
        "response": "We are investigating and will update you.",
        "keywords": ["internet", "connectivity"],
    })

    with patch('services.analysis_service.call_gemini', return_value=mock_response):
        result = analyze_ticket("My internet is not working")

    required_keys = {'category', 'priority', 'summary', 'sentiment', 'response', 'keywords'}
    assert required_keys.issubset(result.keys())
    assert result['category'] == 'Network Issue'
