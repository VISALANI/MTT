"""Health check route."""

from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """Returns 200 OK so load-balancers / CI pipelines can verify the service is up."""
    return jsonify({"success": True, "message": "Multilingual Ticket Translator API is running"}), 200
