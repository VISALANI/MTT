"""
Ticket API Routes
=================
POST /api/process-ticket   — full AI agent pipeline
POST /api/translate-only   — translate without analysis (utility)
GET  /api/supported-languages — list of supported input languages
"""

from flask import Blueprint, request, jsonify
from services.ticket_service import process_ticket_pipeline
from services.translation_service import translate_to_english, detect_language
from utils.validators import validate_ticket_input

ticket_bp = Blueprint("tickets", __name__)


@ticket_bp.route("/process-ticket", methods=["POST"])
def process_ticket():
    """
    Main endpoint — runs the full AI Agent Loop:
      1. Validate input
      2. Detect language
      3. Translate → English
      4. Analyse with Gemini
      5. Return structured result

    Request JSON:
        { "ticket_text": "எனது இணையம் வேலை செய்யவில்லை" }

    Response JSON:
        { "success": true, "data": { ...structured_output } }
    """
    data = request.get_json(silent=True)

    # ── Input validation ─────────────────────────────────────────────────────
    validation_error = validate_ticket_input(data)
    if validation_error:
        return jsonify({"success": False, "error": validation_error}), 400

    ticket_text = data["ticket_text"].strip()

    try:
        result = process_ticket_pipeline(ticket_text)
        return jsonify({"success": True, "data": result}), 200

    except ValueError as ve:
        # Known, user-facing errors (e.g., empty text after strip)
        return jsonify({"success": False, "error": str(ve)}), 400

    except Exception as e:
        # Unexpected errors — log and return generic message
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": f"Processing failed: {str(e)}"}), 500


@ticket_bp.route("/translate-only", methods=["POST"])
def translate_only():
    """
    Lightweight endpoint — detect and translate without AI analysis.
    Useful for previewing translation before running the full pipeline.
    """
    data = request.get_json(silent=True)
    validation_error = validate_ticket_input(data)
    if validation_error:
        return jsonify({"success": False, "error": validation_error}), 400

    ticket_text = data["ticket_text"].strip()

    try:
        detected_lang = detect_language(ticket_text)
        translated = translate_to_english(ticket_text, detected_lang)
        return jsonify({
            "success": True,
            "data": {
                "original_text": ticket_text,
                "detected_language": detected_lang,
                "english_translation": translated,
            }
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@ticket_bp.route("/supported-languages", methods=["GET"])
def supported_languages():
    """Returns the list of input languages the system understands."""
    languages = [
        {"code": "ta", "name": "Tamil"},
        {"code": "hi", "name": "Hindi"},
        {"code": "en", "name": "English"},
        {"code": "fr", "name": "French"},
        {"code": "de", "name": "German"},
        {"code": "es", "name": "Spanish"},
        {"code": "ar", "name": "Arabic"},
        {"code": "zh", "name": "Chinese"},
        {"code": "ja", "name": "Japanese"},
        {"code": "pt", "name": "Portuguese"},
        {"code": "ru", "name": "Russian"},
        {"code": "ko", "name": "Korean"},
    ]
    return jsonify({"success": True, "data": languages}), 200
