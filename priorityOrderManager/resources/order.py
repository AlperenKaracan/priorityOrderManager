from flask import Blueprint, request, jsonify, render_template, session
from extensions import mongo
import time, random
from utils.priority import compute_priority
from utils.priority_queue import order_queue
from utils.logger import log_event

order_bp = Blueprint('order', __name__)


@order_bp.route("/panel")
def order_panel():
    user_type = session.get("customer_type")
    if user_type == "Admin":
        orders_snapshot = order_queue.get_all_recalculated()
    else:
        customer_id = session.get("customer_id")
        orders_snapshot = list(mongo.db.orders.find({"CustomerID": customer_id}))
        for o in orders_snapshot:
            o["DynamicPriority"] = compute_priority(o.get("CustomerType", "Standard"), o.get("CreatedAt", time.time()))
    orders_snapshot = sorted(orders_snapshot, key=lambda o: o.get("CreatedAt", 0), reverse=True)

    products = list(mongo.db.products.find({}))
    customers = list(mongo.db.customers.find({})) if user_type == "Admin" else None
    return render_template("order_panel.html", orders=orders_snapshot, products=products, customers=customers)


@order_bp.route("/create", methods=["POST"])
def create_order():
    customer_id = request.form.get("customer_id")
    product_id = request.form.get("product_id")
    quantity_str = request.form.get("quantity", "1")
    if not customer_id or not product_id:
        return jsonify({"success": False, "message": "Müşteri ve Ürün seçimi gerekli."}), 400
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

    if product["Stock"] < quantity:
        log_event("order_rejected", f"Ürün stoğu yetersiz: {product_id}", customer_id, product_id)
        return jsonify({"success": False, "message": "Ürün stoğu yetersiz."}), 400

    total_price = quantity * product["Price"]
    if customer["Budget"] < total_price:
        log_event("order_rejected", f"Müşteri bakiyesi yetersiz: {customer_id}", customer_id, product_id)
        return jsonify({"success": False, "message": "Müşteri bakiyesi yetersiz."}), 400

    order_count = mongo.db.orders.count_documents({})
    order_id = f"O{order_count + 1:04d}"
    created_at = time.time()
    order_doc = {
        "OrderID": order_id,
        "CustomerID": customer_id,
        "ProductID": product_id,
        "Quantity": quantity,
        "TotalPrice": total_price,
        "OrderDate": created_at,
        "Status": "Pending",
        "CreatedAt": created_at,
        "CustomerType": customer["CustomerType"]
    }
    try:
        mongo.db.orders.insert_one(order_doc)
    except Exception as e:
        return jsonify({"success": False, "message": f"Veritabanı hatası: {str(e)}"}), 500

    base = 15 if customer["CustomerType"] == "Premium" else 10
    order_queue.push(base, {
        "order_id": order_id,
        "created_at": created_at,
        "customer_type": customer["CustomerType"]
    })

    log_event("order_created",
              f"Müşteri {customer_id} {product_id} ürününden {quantity} adet aldı, Toplam: {total_price} TL.",
              customer_id, product_id)
    return jsonify({"success": True, "order_id": order_id}), 201


@order_bp.route("/test_bulk_orders", methods=["POST"])
def test_bulk_orders():
    if session.get("customer_type") != "Admin":
        return jsonify({"success": False, "message": "Yetkisiz işlem"}), 403
    customers = list(mongo.db.customers.find({}))
    products = list(mongo.db.products.find({}))
    created_orders = []
    for i in range(10):
        c = random.choice(customers)
        p = random.choice(products)
        quantity = random.randint(1, 5)
        if p["Stock"] < quantity or c["Budget"] < (quantity * p["Price"]):
            continue
        order_count = mongo.db.orders.count_documents({})
        order_id = f"O{order_count + 1:04d}"
        created_at = time.time()
        total_price = quantity * p["Price"]
        try:
            mongo.db.orders.insert_one({
                "OrderID": order_id,
                "CustomerID": c["CustomerID"],
                "ProductID": p["ProductID"],
                "Quantity": quantity,
                "TotalPrice": total_price,
                "OrderDate": created_at,
                "Status": "Pending",
                "CreatedAt": created_at,
                "CustomerType": c["CustomerType"]
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
                  f"[TEST] Müşteri {c['CustomerID']} ({c['CustomerType']}) {p['ProductID']} ürününden {quantity} adet aldı, Toplam: {total_price} TL.",
                  c["CustomerID"], p["ProductID"])
        created_orders.append(order_id)
    return jsonify({"success": True, "message": f"{len(created_orders)} adet test siparişi oluşturuldu.",
                    "order_ids": created_orders}), 201


@order_bp.route("/priority_list", methods=["GET"])
def priority_list():
    orders_snapshot = order_queue.get_all_recalculated()
    for o in orders_snapshot:
        o["WaitTime"] = round(time.time() - o.get("created_at", time.time()), 2)
    return jsonify(orders_snapshot)
