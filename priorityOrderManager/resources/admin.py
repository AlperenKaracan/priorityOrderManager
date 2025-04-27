from flask import Blueprint, render_template, session, abort, jsonify
from extensions import mongo
from functools import wraps
import time

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("customer_type") != "Admin":
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    total_customers = mongo.db.customers.count_documents({})
    total_products = mongo.db.products.count_documents({})
    total_orders = mongo.db.orders.count_documents({})
    pending_orders = mongo.db.orders.count_documents({"Status": "Pending"})
    approved_orders = mongo.db.orders.count_documents({"Status": "Approved"})
    rejected_orders = mongo.db.orders.count_documents({"Status": "Rejected"})
    total_revenue_pipeline = [
        {"$match": {"Status": "Approved"}},
        {"$group": {"_id": None, "total": {"$sum": "$TotalPrice"}}}
    ]
    revenue_result = list(mongo.db.orders.aggregate(total_revenue_pipeline))
    total_revenue = revenue_result[0]['total'] if revenue_result else 0
    customer_type_pipeline = [
        {"$group": {"_id": "$CustomerType", "count": {"$sum": 1}}}
    ]
    customer_types = list(mongo.db.customers.aggregate(customer_type_pipeline))
    customer_type_stats = {item['_id']: item['count'] for item in customer_types}

    top_products_pipeline = [
        {"$match": {"Status": "Approved"}},
        {"$group": {"_id": "$ProductID", "count": {"$sum": "$Quantity"}}},
        {"$sort": {"count": -1}},
        {"$limit": 5},
        {"$lookup": {
            "from": "products",
            "localField": "_id",
            "foreignField": "ProductID",
            "as": "productInfo"
        }},
        {"$unwind": "$productInfo"},
        {"$project": {"_id": 0, "ProductName": "$productInfo.ProductName", "count": 1}}

    ]
    top_products = list(mongo.db.orders.aggregate(top_products_pipeline))


    stats = {
        "total_customers": total_customers,
        "total_products": total_products,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "approved_orders": approved_orders,
        "rejected_orders": rejected_orders,
        "total_revenue": round(total_revenue, 2),
        "customer_types": customer_type_stats,
        "top_products": top_products
    }

    return render_template("admin_dashboard.html", stats=stats)

@admin_bp.route("/stats_data")
@admin_required
def stats_data():
    orders_by_status_pipeline = [
        {"$group": {"_id": "$Status", "count": {"$sum": 1}}}
    ]
    orders_status = list(mongo.db.orders.aggregate(orders_by_status_pipeline))
    chart_data = {
        "labels": [item['_id'] for item in orders_status],
        "data": [item['count'] for item in orders_status],
        "backgroundColor": [
                'rgba(255, 193, 7, 0.7)' if item['_id'] == 'Pending' else
                'rgba(40, 167, 69, 0.7)' if item['_id'] == 'Approved' else
                'rgba(220, 53, 69, 0.7)' if item['_id'] == 'Rejected' else
                'rgba(108, 117, 125, 0.7)'
                for item in orders_status
            ]
    }
    return jsonify(chart_data)