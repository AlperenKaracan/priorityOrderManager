from flask import Blueprint, render_template, jsonify
from extensions import mongo

log_bp = Blueprint('log', __name__)

@log_bp.route("/panel")
def panel():
    return render_template("log_panel.html")

@log_bp.route("/list")
def list_logs():
    try:
        logs = list(mongo.db.logs.find({}).sort("_id", -1).limit(50))
        for l in logs:
            l["_id"] = str(l["_id"])
            l['user'] = l.get('user', "Unknown")
            l['log_type'] = l.get('log_type', "unknown")
            l['customer_name'] = l.get('customer_name', "Unknown")
            l['customer_type'] = l.get('customer_type', "Standard")
        return jsonify(logs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
