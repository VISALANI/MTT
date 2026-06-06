"""
Multilingual Ticket Translator — Flask Application Entry Point
=============================================================
Initialises the Flask app, registers blueprints, and wires up CORS.
"""

import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from routes.ticket_routes import ticket_bp
from routes.health_routes import health_bp

# Load environment variables from .env (project root)
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))


def create_app() -> Flask:
    """Application factory — returns a fully configured Flask app."""
    app = Flask(__name__)

    # Allow all origins in development; lock this down in production
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ── Register blueprints ───────────────────────────────────────────────────
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(ticket_bp, url_prefix="/api")

    # ── Global error handlers ─────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        from flask import jsonify
        return jsonify({"success": False, "error": "Route not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        from flask import jsonify
        return jsonify({"success": False, "error": "Internal server error"}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
