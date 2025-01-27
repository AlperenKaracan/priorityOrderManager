from flask import Blueprint, render_template, request, jsonify
from extensions import mongo
from utils.logger import log_event

customer_bp = Blueprint('customer', __name__)

@customer_bp.route("/panel", methods=["GET"])
def panel():
    customers = list(mongo.db.customers.find({}))
    products = list(mongo.db.products.find({}))
    return render_template("customer_panel.html", customers=customers, products=products)

@customer_bp.route("/<customer_id>/orders", methods=["GET"])
def customer_orders(customer_id):
    orders = list(mongo.db.orders.find({"CustomerID": customer_id}))

    if not orders:
        return render_template("customer_orders.html", customer=None, orders=None, error="Bu müşterinin hiç siparişi bulunmamaktadır.")

    enriched_orders = []
    for order in orders:
        product = mongo.db.products.find_one({"ProductID": order.get("ProductID")})
        if product:
            order['ProductName'] = product.get("ProductName", "Bilinmiyor")
            order['Price'] = product.get("Price", 0.0)
        else:
            order['ProductName'] = "Ürün Bulunamadı"
            order['Price'] = 0.0
        enriched_orders.append(order)


    customer = mongo.db.customers.find_one({"CustomerID": customer_id})
    if not customer:
        return render_template("customer_orders.html", customer=None, orders=None, error="Müşteri bulunamadı.")

    return render_template("customer_orders.html", customer=customer, orders=enriched_orders, error=None)

@customer_bp.route("/update_budget", methods=["POST"])
def update_budget():
    customer_id = request.form.get("customer_id")
    new_budget = request.form.get("new_budget")

    if not customer_id or not new_budget:
        return jsonify({"success": False, "error": "Müşteri ID ve yeni bütçe gerekli"}), 400

    try:
        new_budget = float(new_budget)
        if new_budget < 0:
            return jsonify({"success": False, "error": "Bütçe negatif olamaz"}), 400
    except ValueError:
        return jsonify({"success": False, "error": "Bütçe geçerli bir sayı olmalı"}), 400

    try:
        result = mongo.db.customers.update_one(
            {"CustomerID": customer_id},
            {"$set": {"Budget": new_budget}}
        )
        if result.matched_count == 1:
            log_event("customer_budget_updated", f"Müşteri {customer_id} bütçesi güncellendi: {new_budget}")
            return jsonify({"success": True, "message": "Bütçe başarıyla güncellendi."}), 200
        else:
            return jsonify({"success": False, "error": "Müşteri bulunamadı."}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@customer_bp.route("/add", methods=["POST"])
def add_customer():
    customer_name = request.form.get("customer_name")
    customer_type = request.form.get("customer_type", "Standard")

    if not customer_name:
        log_event("customer_add_error", "Müşteri adı eksik.")
        return jsonify({"success": False, "error": "Müşteri adı gerekli"}), 400

    customer_count = mongo.db.customers.count_documents({})
    customer_id = f"C{customer_count + 1:04d}"

    new_customer = {
        "CustomerID": customer_id,
        "CustomerName": customer_name,
        "CustomerType": customer_type,
        "Budget": 1000.0,
        "TotalSpent": 0.0
    }

    try:
        mongo.db.customers.insert_one(new_customer)
        log_event("customer_added", f"Müşteri eklendi: {customer_id} - {customer_name}")
        return jsonify({"success": True, "message": "Müşteri başarıyla eklendi.", "CustomerID": customer_id}), 201
    except Exception as e:
        log_event("customer_add_exception", f"Eklenirken hata: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@customer_bp.route("/delete", methods=["POST"])
def delete_customer():
    customer_id = request.form.get("customer_id")
    if not customer_id:
        return jsonify({"success": False, "error": "Müşteri ID gerekli"}), 400

    try:
        result = mongo.db.customers.delete_one({"CustomerID": customer_id})
        if result.deleted_count == 1:
            log_event("customer_deleted", f"Müşteri silindi: {customer_id}")
            return jsonify({"success": True, "message": f"Müşteri {customer_id} başarıyla silindi."}), 200
        else:
            return jsonify({"success": False, "error": "Müşteri bulunamadı."}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

