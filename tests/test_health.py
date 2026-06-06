"""
Test 1 — Health check endpoint
"""


def test_health_check(client):
    """GET /api/health should return 200 with success flag."""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'running' in data['message'].lower()
