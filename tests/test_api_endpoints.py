"""
Tests 18–24 — Flask API endpoint integration tests
All AI services are mocked.
"""

import json
from unittest.mock import patch

MOCK_PIPELINE_RESULT = {
    "original_text": "எனது இணையம் வேலை செய்யவில்லை",
    "detected_language": "ta",
    "language_name": "Tamil",
    "translation": "My internet is not working",
    "category": "Network Issue",
    "priority": "Medium",
    "summary": "Customer reports internet connectivity issue.",
    "sentiment": "Negative",
    "response": "We are investigating the issue and will update you shortly.",
    "keywords": ["internet", "connectivity"],
    "processing_time_ms": 1234,
}


# ── /api/health ───────────────────────────────────────────────────────────────

def test_health_returns_200(client):
    resp = client.get('/api/health')
    assert resp.status_code == 200


# ── /api/supported-languages ─────────────────────────────────────────────────

def test_supported_languages(client):
    resp = client.get('/api/supported-languages')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    codes = [lang['code'] for lang in data['data']]
    assert 'ta' in codes
    assert 'hi' in codes
    assert 'en' in codes


# ── /api/process-ticket ───────────────────────────────────────────────────────

def test_process_ticket_success(client):
    """Valid ticket should return 200 with all structured fields."""
    with patch('routes.ticket_routes.process_ticket_pipeline', return_value=MOCK_PIPELINE_RESULT):
        resp = client.post(
            '/api/process-ticket',
            json={"ticket_text": "எனது இணையம் வேலை செய்யவில்லை"},
        )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body['success'] is True
    assert body['data']['category'] == 'Network Issue'
    assert body['data']['translation'] == 'My internet is not working'


def test_process_ticket_missing_field(client):
    """Request without ticket_text should return 400."""
    resp = client.post('/api/process-ticket', json={"message": "oops"})
    assert resp.status_code == 400
    body = resp.get_json()
    assert body['success'] is False


def test_process_ticket_empty_text(client):
    """Empty ticket_text should return 400."""
    resp = client.post('/api/process-ticket', json={"ticket_text": "   "})
    assert resp.status_code == 400


def test_process_ticket_no_json(client):
    """Non-JSON body should return 400."""
    resp = client.post('/api/process-ticket', data="plain text", content_type='text/plain')
    assert resp.status_code == 400


def test_process_ticket_english_input(client):
    """English ticket should also go through the full pipeline."""
    english_result = {**MOCK_PIPELINE_RESULT, "detected_language": "en", "language_name": "English"}
    with patch('routes.ticket_routes.process_ticket_pipeline', return_value=english_result):
        resp = client.post(
            '/api/process-ticket',
            json={"ticket_text": "My account is locked"},
        )
    assert resp.status_code == 200
    assert resp.get_json()['data']['detected_language'] == 'en'


# ── /api/translate-only ───────────────────────────────────────────────────────

def test_translate_only_success(client):
    """Valid text should return translation without analysis."""
    with patch('routes.ticket_routes.detect_language', return_value='ta'), \
         patch('routes.ticket_routes.translate_to_english', return_value='My internet is not working'):
        resp = client.post(
            '/api/translate-only',
            json={"ticket_text": "எனது இணையம் வேலை செய்யவில்லை"},
        )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body['success'] is True
    assert 'english_translation' in body['data']
    assert 'detected_language' in body['data']


def test_translate_only_missing_field(client):
    """Missing ticket_text should return 400."""
    resp = client.post('/api/translate-only', json={})
    assert resp.status_code == 400
