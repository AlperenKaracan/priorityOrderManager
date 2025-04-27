from flask import Blueprint, request, jsonify, render_template, session
from extensions import mongo
from utils.logger import log_event
import threading

product_bp = Blueprint('product', __name__)
stock_lock = threading.Lock()

@product_bp.route("/panel")
def product_panel():
    products = list(mongo.db.products.find({}))
    return render_template("product_panel.html", products=products)

@product_bp.route("/update_stock", methods=["POST"])
def update_stock():
    if session.get("customer_type") != "Admin":
        return jsonify({"error": "Yetkisiz işlem"}), 403
    product_id = request.form.get("product_id")
    amount_str = request.form.get("amount", "0")
    if not product_id:
        return jsonify({"error": "Ürün ID gerekli"}), 400
    try:
        amount = int(amount_str)
    except ValueError:
        return jsonify({"error": "Miktar sayısal olmalı"}), 400
    with stock_lock:
        product = mongo.db.products.find_one({"ProductID": product_id})
        if not product:
            return jsonify({"error": "Ürün bulunamadı"}), 404
        new_stock = product.get("Stock", 0) + amount
        if new_stock < 0:
            return jsonify({"error": "Stok negatif olamaz"}), 400
        mongo.db.products.update_one({"ProductID": product_id}, {"$set": {"Stock": new_stock}})
        log_event("stock_updated", f"Ürün {product_id} stok güncellendi: {new_stock} adet.", session.get("customer_name", "Admin"), product_id)
        return jsonify({"success": True, "message": "Stok güncellendi", "new_stock": new_stock}), 200

@product_bp.route("/add", methods=["POST"])
def add_product():
    if session.get("customer_type") != "Admin":
        return jsonify({"error": "Yetkisiz işlem"}), 403
    product_name = request.form.get("product_name")
    stock_str = request.form.get("stock", "0")
    price_str = request.form.get("price")
    if not product_name or not price_str:
        return jsonify({"error": "Ürün adı ve fiyat gerekli"}), 400
    try:
        stock = int(stock_str)
        price = float(price_str)
    except ValueError:
        return jsonify({"error": "Stok ve fiyat sayısal olmalı"}), 400
    product_count = mongo.db.products.count_documents({})
    product_id = f"P{product_count+1:04d}"
    new_product = {
        "ProductID": product_id,
        "ProductName": product_name,
        "Stock": stock,
        "Price": price
    }
    mongo.db.products.insert_one(new_product)
    log_event("product_added", f"Ürün eklendi: {product_name} (ID: {product_id}, Fiyat: {price} TL)", session.get("customer_name", "Admin"), product_id)
    return jsonify({"success": True, "message": "Ürün eklendi", "ProductID": product_id})

@product_bp.route("/delete", methods=["POST"])
def delete_product():
    if session.get("customer_type") != "Admin":
        return jsonify({"error": "Yetkisiz işlem"}), 403
    product_id = request.form.get("product_id")
    if not product_id:
        return jsonify({"error": "Ürün ID gerekli"}), 400
    result = mongo.db.products.delete_one({"ProductID": product_id})
    if result.deleted_count > 0:
        log_event("product_deleted", f"Ürün silindi: {product_id}", session.get("customer_name", "Admin"), product_id)
        return jsonify({"success": True, "message": f"Ürün silindi: {product_id}"})
    else:
        return jsonify({"error": "Ürün bulunamadı"}), 404
@product_bp.route("/list_json")
def product_list_json():
    products = list(mongo.db.products.find({}))
    for p in products:
        p.pop('_id', None)
    return jsonify({"success": True, "products": products})
