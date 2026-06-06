"""
AI Analysis Service — AI Agent Loop Core
=========================================
Implements the AI Agent workflow:

  Step 1 → Receive English ticket text
  Step 2 → Build structured analysis prompt
  Step 3 → Call Gemini (external AI API)
  Step 4 → Parse JSON response
  Step 5 → Validate & return structured output

The agent is designed to be deterministic — it always returns the
same six fields regardless of ticket content.
"""

import json
import re

from services.gemini_service import call_gemini

# ── Allowed values for validation ─────────────────────────────────────────────
VALID_CATEGORIES = {
    "Network Issue", "Billing Issue", "Account Issue",
    "Technical Support", "Hardware Issue", "Software Issue",
    "Shipping Issue", "Product Issue", "Service Issue",
    "Security Issue", "General Inquiry", "Other"
}

VALID_PRIORITIES = {"Low", "Medium", "High", "Critical"}

VALID_SENTIMENTS = {"Positive", "Neutral", "Negative", "Very Negative"}


def build_analysis_prompt(english_text: str) -> str:
    """
    Constructs the structured prompt sent to Gemini for ticket analysis.
    The prompt uses strict JSON output instructions to ensure parsability.
    """
    return f"""You are an expert customer support AI analyst.
Analyze the following English customer support ticket and return a structured JSON response.

Ticket:
\"\"\"{english_text}\"\"\"

Return ONLY a valid JSON object with these exact keys (no markdown, no explanation):
{{
  "category": "<one of: Network Issue, Billing Issue, Account Issue, Technical Support, Hardware Issue, Software Issue, Shipping Issue, Product Issue, Service Issue, Security Issue, General Inquiry, Other>",
  "priority": "<one of: Low, Medium, High, Critical>",
  "summary": "<one sentence summary of the customer's problem>",
  "sentiment": "<one of: Positive, Neutral, Negative, Very Negative>",
  "response": "<a professional, empathetic 1-2 sentence suggested reply to send to the customer>",
  "keywords": ["<keyword1>", "<keyword2>", "<keyword3>"]
}}

Rules:
- priority = Critical if the issue involves data loss, security breach, or service outage
- priority = High if the customer is blocked from using the product
- priority = Medium for degraded functionality
- priority = Low for general questions or minor inconveniences
- sentiment must reflect the customer's emotional tone
- response must be polite, professional, and solution-oriented
"""


def parse_gemini_json(raw_response: str) -> dict:
    """
    Extracts and parses JSON from Gemini's response text.

    Gemini sometimes wraps JSON in ```json ... ``` markdown fences.
    This function strips those before parsing.

    Args:
        raw_response: Raw string from Gemini.

    Returns:
        Parsed dict.

    Raises:
        ValueError: If no valid JSON is found.
    """
    # Remove markdown code fences if present
    cleaned = re.sub(r"```(?:json)?", "", raw_response).replace("```", "").strip()

    # Try direct parse first
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Try extracting the first {...} block as fallback
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not parse Gemini response as JSON: {raw_response[:200]}")


def validate_and_normalise(parsed: dict) -> dict:
    """
    Validates the parsed dict against allowed values and fills in
    safe defaults for any missing or invalid fields.

    Args:
        parsed: Dict from parse_gemini_json.

    Returns:
        Validated and normalised dict.
    """
    category = parsed.get("category", "Other")
    if category not in VALID_CATEGORIES:
        category = "Other"

    priority = parsed.get("priority", "Medium")
    if priority not in VALID_PRIORITIES:
        priority = "Medium"

    sentiment = parsed.get("sentiment", "Neutral")
    if sentiment not in VALID_SENTIMENTS:
        sentiment = "Neutral"

    summary = str(parsed.get("summary", "Customer has submitted a support ticket.")).strip()
    response = str(parsed.get("response", "Thank you for contacting us. We will look into this shortly.")).strip()
    keywords = parsed.get("keywords", [])
    if not isinstance(keywords, list):
        keywords = []

    return {
        "category": category,
        "priority": priority,
        "summary": summary,
        "sentiment": sentiment,
        "response": response,
        "keywords": keywords[:5],  # Cap at 5 keywords
    }


def analyze_ticket(english_text: str) -> dict:
    """
    Main analysis function — calls Gemini and returns structured output.

    This is the AI Agent Loop:
      Receive → Prompt → Call → Parse → Validate → Return

    Args:
        english_text: Ticket text already translated to English.

    Returns:
        Dict with category, priority, summary, sentiment, response, keywords.
    """
    prompt = build_analysis_prompt(english_text)
    raw_response = call_gemini(prompt)
    parsed = parse_gemini_json(raw_response)
    return validate_and_normalise(parsed)
