"""
Ticket Processing Pipeline Service
====================================
Orchestrates the full AI Agent Loop for a single ticket:

  [Input] → [Detect Language] → [Translate] → [Analyse] → [Assemble Output]

This module is the single source of truth for the pipeline order.
All individual steps are delegated to their respective services.
"""

import time
from services.translation_service import detect_language, translate_to_english, get_language_name
from services.analysis_service import analyze_ticket


def process_ticket_pipeline(ticket_text: str) -> dict:
    """
    Runs the complete AI Agent Loop for a customer support ticket.

    Args:
        ticket_text: Raw customer input (any supported language).

    Returns:
        A structured dict with all pipeline outputs including:
            - original_text
            - detected_language / language_name
            - translation (English)
            - category, priority, summary, sentiment, response, keywords
            - processing_time_ms

    Raises:
        ValueError: For empty or whitespace-only input.
        Exception:  Propagates AI/network errors to the route handler.
    """
    if not ticket_text or not ticket_text.strip():
        raise ValueError("Ticket text cannot be empty.")

    start_time = time.time()

    # ── AGENT STEP 1: Language Detection ─────────────────────────────────────
    detected_lang = detect_language(ticket_text)
    lang_name = get_language_name(detected_lang)

    # ── AGENT STEP 2: Translation → English ──────────────────────────────────
    english_text = translate_to_english(ticket_text, detected_lang)

    # ── AGENT STEP 3: AI Analysis (Gemini) ───────────────────────────────────
    analysis = analyze_ticket(english_text)

    # ── AGENT STEP 4: Assemble Final Output ───────────────────────────────────
    processing_time_ms = round((time.time() - start_time) * 1000)

    return {
        # Input echo
        "original_text": ticket_text,

        # Translation stage
        "detected_language": detected_lang,
        "language_name": lang_name,
        "translation": english_text,

        # AI analysis stage
        "category":  analysis["category"],
        "priority":  analysis["priority"],
        "summary":   analysis["summary"],
        "sentiment": analysis["sentiment"],
        "response":  analysis["response"],
        "keywords":  analysis["keywords"],

        # Metadata
        "processing_time_ms": processing_time_ms,
    }
