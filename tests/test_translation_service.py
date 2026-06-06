"""
Tests 7–11 — Translation service (language detection + translation)
Gemini calls are mocked so no API key is required.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from unittest.mock import patch
from services.translation_service import (
    detect_language,
    get_language_name,
    translate_to_english,
)


def test_detect_english():
    """English text should be detected as 'en'."""
    lang = detect_language("My internet connection is not working")
    assert lang == 'en'


def test_detect_returns_string():
    """detect_language should always return a string."""
    result = detect_language("some random text")
    assert isinstance(result, str)


def test_get_language_name_known():
    """Known codes should return human-readable names."""
    assert get_language_name('ta') == 'Tamil'
    assert get_language_name('hi') == 'Hindi'
    assert get_language_name('fr') == 'French'


def test_get_language_name_unknown():
    """Unknown codes should return the code uppercased."""
    assert get_language_name('xx') == 'XX'


def test_translate_english_skips_api():
    """English source text should be returned as-is without calling Gemini."""
    with patch('services.translation_service.call_gemini') as mock_gemini:
        result = translate_to_english("Hello world", "en")
        assert result == "Hello world"
        mock_gemini.assert_not_called()


def test_translate_non_english_calls_gemini():
    """Non-English source should call Gemini and return its response."""
    with patch('services.translation_service.call_gemini', return_value="My internet is not working") as mock_gemini:
        result = translate_to_english("எனது இணையம் வேலை செய்யவில்லை", "ta")
        assert result == "My internet is not working"
        mock_gemini.assert_called_once()
