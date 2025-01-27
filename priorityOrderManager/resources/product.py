from flask import Blueprint, request, jsonify, render_template
from extensions import mongo
from utils.logger import log_event
from utils.log_models import generate_id

product_bp = Blueprint('product', __name__)

from flask import Blueprint, request, jsonify
from extensions import mongo
import threading
from utils.logger import log_event

stock_lock = threading.Lock()

@product_bp.route("/panel")
def product_panel():
    products = list(mongo.db.products.find({}))

    return render_template("product_panel.html", products=products)

@product_bp.route("/update_stock", methods=["POST"])
def update_stock():
    product_id = request.form.get("product_id")
    amount_str = request.form.get("amount", "0")

    if not product_id:
        return jsonify({"error": "Ürün ID gerekli"}), 400

    try:
        amount = int(amount_str)
    except ValueError:
        return jsonify({"error": "amount sayısal değer olmalıdır"}), 400

    with stock_lock:
        product = mongo.db.products.find_one({"ProductID": product_id})
        if not product:
            return jsonify({"error": "Ürün bulunamadı"}), 404

        new_stock = product.get("Stock", 0) + amount
        if new_stock < 0:
            return jsonify({"error": "Stok negatif olamaz"}), 400

        mongo.db.products.update_one(
            {"ProductID": product_id},
            {"$set": {"Stock": new_stock}}
        )

        log_event("stock_updated", f"Ürün {product_id} stok güncellendi. Yeni stok: {new_stock}")

        return jsonify({"message": "Stok güncellendi", "new_stock": new_stock, "success": True}), 200

@product_bp.route("/add", methods=["POST"])
def add_product():
    product_name = request.form.get("product_name")
    price_str = request.form.get("price")
    stock_str = request.form.get("stock", "0")

    if not product_name or not price_str:
        return jsonify({"error": "Ürün adı ve fiyat gerekli"}), 400

    try:
        price = float(price_str)
        stock = int(stock_str)
    except ValueError:
        return jsonify({"error": "Fiyat ve stok sayısal olmalı"}), 400

    product_count = mongo.db.products.count_documents({})
    product_id = f"P{product_count+1:04d}"

    new_product = {
        "ProductID": product_id,
        "ProductName": product_name,
        "Price": price,
        "Stock": stock
    }

    try:
        mongo.db.products.insert_one(new_product)
        log_event("product_added", f"Ürün eklendi: {product_id} - {product_name}, Fiyat: {price}, Stok: {stock}")
        return jsonify({"message": "Ürün başarıyla eklendi.", "ProductID": product_id, "success": True}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@product_bp.route("/delete", methods=["POST"])
def delete_product():
    product_id = request.form.get("product_id")
    if not product_id:
        return jsonify({"error": "Ürün ID gerekli"}), 400

    result = mongo.db.products.delete_one({"ProductID": product_id})
    if result.deleted_count > 0:
        log_event("product_deleted", f"Ürün silindi: {product_id}")
        return jsonify({"message": f"Ürün silindi: {product_id}", "success": True})
    else:
        return jsonify({"error": "Ürün bulunamadı"}), 404
