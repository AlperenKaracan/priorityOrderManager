from flask import Blueprint, jsonify

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/check", methods=["GET"])
def check():
    return jsonify({"auth": True})
