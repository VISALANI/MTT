"""
Translation Service
===================
Handles language detection and translation to English.

Strategy:
  1. Use `langdetect` (offline, no API key) for language detection.
  2. Use Gemini's generative capability for translation — keeps the
     project to a single free-tier API while staying accurate for
     low-resource languages like Tamil and Hindi.
  3. If the text is already English, skip translation.
"""

import re
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

from services.gemini_service import call_gemini

# Make langdetect deterministic across runs
DetectorFactory.seed = 42

# Human-readable language name map for display purposes
LANGUAGE_NAMES = {
    "ta": "Tamil",
    "hi": "Hindi",
    "en": "English",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "ar": "Arabic",
    "zh-cn": "Chinese",
    "zh-tw": "Chinese (Traditional)",
    "ja": "Japanese",
    "pt": "Portuguese",
    "ru": "Russian",
    "ko": "Korean",
    "it": "Italian",
    "nl": "Dutch",
    "tr": "Turkish",
    "vi": "Vietnamese",
    "th": "Thai",
    "id": "Indonesian",
    "ms": "Malay",
}


def detect_language(text: str) -> str:
    """
    Detects the BCP-47 language code of the input text.

    Returns 'unknown' on failure rather than raising — keeps the
    pipeline running even if detection is uncertain.

    Args:
        text: Raw customer ticket text.

    Returns:
        Language code string, e.g. "ta", "hi", "en".
    """
    try:
        lang = detect(text)
        return lang
    except LangDetectException:
        return "unknown"


def get_language_name(code: str) -> str:
    """Converts a BCP-47 code to a human-readable name."""
    return LANGUAGE_NAMES.get(code.lower(), code.upper())


def translate_to_english(text: str, source_lang: str) -> str:
    """
    Translates `text` from `source_lang` into English using Gemini.

    If the source language is already English, returns the original text
    unchanged to save API quota.

    Args:
        text:        The text to translate.
        source_lang: BCP-47 language code of the source text.

    Returns:
        English translation string.
    """
    # Skip translation for English text
    if source_lang.startswith("en"):
        return text

    lang_name = get_language_name(source_lang)

    prompt = f"""Translate the following {lang_name} customer support ticket into English.
Return ONLY the translated text — no explanations, no quotation marks, no extra commentary.

{lang_name} text:
{text}

English translation:"""

    translated = call_gemini(prompt)

    # Strip any accidental markdown or leading/trailing whitespace
    translated = re.sub(r"^[`\"']+|[`\"']+$", "", translated.strip())
    return translated
