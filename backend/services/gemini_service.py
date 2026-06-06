"""
Gemini AI Service
=================
Thin wrapper around the Google Generative AI SDK.

- Uses the gemini-1.5-flash model (free tier, fast).
- Centralises all Gemini calls so the API key and config live in one place.
- Falls back gracefully when the API key is missing (returns placeholder text).
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# ── Configure Gemini SDK once at import time ──────────────────────────────────
_API_KEY = os.getenv("GEMINI_API_KEY", "")
_MODEL_NAME = "gemini-1.5-flash"   # Free-tier model; swap to gemini-pro if needed

if _API_KEY:
    genai.configure(api_key=_API_KEY)
else:
    print("[WARNING] GEMINI_API_KEY not set. AI features will return placeholder output.")

# Safety settings — relaxed for support ticket content (may include frustration)
_SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT",        "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_HATE_SPEECH",       "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
]

_GENERATION_CONFIG = {
    "temperature": 0.3,       # Low temperature → consistent, structured output
    "top_p": 0.95,
    "max_output_tokens": 1024,
}


def call_gemini(prompt: str) -> str:
    """
    Sends a prompt to Gemini and returns the text response.

    Args:
        prompt: The full prompt string.

    Returns:
        Model response text.

    Raises:
        RuntimeError: If the API key is missing.
        Exception:    Propagates SDK exceptions for callers to handle.
    """
    if not _API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. "
            "Get a free key at https://aistudio.google.com/app/apikey and add it to .env"
        )

    model = genai.GenerativeModel(
        model_name=_MODEL_NAME,
        generation_config=_GENERATION_CONFIG,
        safety_settings=_SAFETY_SETTINGS,
    )

    response = model.generate_content(prompt)

    # response.text raises if the response was blocked
    return response.text.strip()
