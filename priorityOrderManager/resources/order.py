from flask import Blueprint, request, jsonify, render_template
from extensions import mongo
import time
import random
from utils.priority import compute_priority
from utils.priority_queue import order_queue
from utils.logger import log_event

order_bp = Blueprint('order', __name__)


@order_bp.route("/panel")
def order_panel():
    orders_snapshot = order_queue.get_all_recalculated()
    products = list(mongo.db.products.find({}))
    return render_template("order_panel.html", orders=orders_snapshot, products=products)


@order_bp.route("/create", methods=["POST"])
def create_order():
    customer_id = request.form.get("customer_id")
    product_id = request.form.get("product_id")
    quantity_str = request.form.get("quantity", "1")

    if not customer_id or not product_id:
        return jsonify({"success": False, "message": "Müşteri ID ve Ürün ID gerekli."}), 400

    try:
        quantity = int(quantity_str)
    except ValueError:
        return jsonify({"success": False, "message": "Miktar sayı olmalı."}), 400

    if quantity > 5:
        return jsonify({"success": False, "message": "Maksimum 5 adet alınabilir."}), 400

    customer = mongo.db.customers.find_one({"CustomerID": customer_id})
    product = mongo.db.products.find_one({"ProductID": product_id})

    if not customer or not product:
        return jsonify({"success": False, "message": "Geçersiz müşteri veya ürün."}), 404

    order_count = mongo.db.orders.count_documents({})
    order_id = f"O{order_count + 1:04d}"

    try:
        mongo.db.orders.insert_one({
            "OrderID": order_id,
            "CustomerID": customer_id,
            "ProductID": product_id,
            "Quantity": quantity,
            "Status": "Pending",
            "CreatedAt": time.time()
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Veritabanına ekleme hatası: {str(e)}"}), 500

    base = 15 if customer["CustomerType"] == "Premium" else 10
    order_queue.push(base, {
        "order_id": order_id,
        "created_at": time.time(),
        "customer_type": customer["CustomerType"]
    })

    log_event("order_created", f"Müşteri {customer_id}, Product{product_id} ürününden {quantity} adet sipariş verdi.",
              customer_id, product_id)

    return jsonify({"success": True, "order_id": order_id}), 201


@order_bp.route("/test_bulk_orders", methods=["POST"])
def test_bulk_orders():
    customers = list(mongo.db.customers.find({}))
    products = list(mongo.db.products.find({}))

    premium_customers = [c for c in customers if c["CustomerType"] == "Premium"]
    standard_customers = [c for c in customers if c["CustomerType"] == "Standard"]

    if len(premium_customers) < 2:
        return jsonify({"success": False, "message": "Sistemde en az 2 premium müşteri bulunmalıdır."}), 400

    created_orders = []
    for i in range(10):
        if i < 2:
            c = random.choice(premium_customers)
        else:
            c = random.choice(customers)

        p = random.choice(products)
        quantity = random.randint(1, 5)
        order_count = mongo.db.orders.count_documents({})
        order_id = f"O{order_count + 1:04d}"
        created_at = time.time()

        try:
            mongo.db.orders.insert_one({
                "OrderID": order_id,
                "CustomerID": c["CustomerID"],
                "ProductID": p["ProductID"],
                "Quantity": quantity,
                "Status": "Pending",
                "CreatedAt": created_at
            })
        except Exception as e:
            log_event("worker_error", f"Bulk order ekleme hatası: {str(e)}", None, None)
            continue

        base = 15 if c["CustomerType"] == "Premium" else 10
        order_queue.push(base, {
            "order_id": order_id,
            "created_at": created_at,
            "customer_type": c["CustomerType"]
        })
        log_event("order_created",
                  f"[TEST] Müşteri {c['CustomerID']} ({c['CustomerType']}), Product{p['ProductID']} ürününden {quantity} adet sipariş verdi.",
                  c["CustomerID"], p["ProductID"])
        created_orders.append(order_id)

    return jsonify({"success": True, "message": f"{len(created_orders)} adet rastgele test siparişi oluşturuldu.",
                    "order_ids": created_orders}), 201
