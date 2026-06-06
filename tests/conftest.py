"""
pytest configuration — provides the Flask test client as a fixture.
All tests import `client` from here.
"""

import sys
import os
import pytest

# Make the backend package importable from tests/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Disable real AI calls during tests
os.environ.setdefault('GEMINI_API_KEY', 'test_key_placeholder')


@pytest.fixture
def app():
    from app import create_app
    flask_app = create_app()
    flask_app.config['TESTING'] = True
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()
