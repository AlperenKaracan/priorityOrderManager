from flask import Blueprint, render_template, jsonify, request, session
from extensions import mongo

log_bp = Blueprint('log', __name__)

@log_bp.route("/panel")
def panel():
    return render_template("log_panel.html")

@log_bp.route("/list")
def list_logs():
    try:
        user_type = session.get("customer_type")
        query = {}
        log_type = request.args.get("log_type")
        if log_type:
            query["log_type"] = log_type
        if user_type != "Admin":
            query["CustomerID"] = session.get("customer_id")
        logs = list(mongo.db.logs.find(query).sort("_id", -1).limit(50))
        for l in logs:
            l["_id"] = str(l["_id"])
        return jsonify(logs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
