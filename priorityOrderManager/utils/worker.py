import threading
import time
from extensions import mongo
from utils.logger import log_event
from resources.product import stock_lock

order_semaphore = threading.Semaphore(2)

def order_processor():
    from utils.priority_queue import order_queue
    while True:
        order_data = order_queue.pop()
        if order_data is not None:
            log_event("worker_info", f"Sipariş işlenmeye başladı: {order_data['order_id']}", None, None)
            with order_semaphore:
                try:
                    time.sleep(5)
                    order_id = order_data["order_id"]
                    order = mongo.db.orders.find_one({"OrderID": order_id})
                    if not order:
                        log_event("worker_error", f"Sipariş bulunamadı: {order_id}", None, None)
                        continue
                    customer = mongo.db.customers.find_one({"CustomerID": order["CustomerID"]})
                    product = mongo.db.products.find_one({"ProductID": order["ProductID"]})
                    if not customer or not product:
                        mongo.db.orders.update_one({"OrderID": order_id}, {"$set": {"Status": "Rejected"}})
                        log_event("order_rejected", f"Müşteri veya ürün bulunamadı: Sipariş ID {order_id}", order["CustomerID"] if customer else None, order["ProductID"] if product else None)
                        continue

                    quantity = order["Quantity"]
                    with stock_lock:
                        current_stock = product["Stock"]
                        if current_stock >= quantity:
                            new_stock = current_stock - quantity
                            mongo.db.products.update_one({"ProductID": product["ProductID"]}, {"$set": {"Stock": new_stock}})
                            total_cost = quantity * product["Price"]
                            if customer["Budget"] >= total_cost:
                                new_budget = customer["Budget"] - total_cost
                                new_spent = customer.get("TotalSpent", 0.0) + total_cost
                                mongo.db.customers.update_one({"CustomerID": customer["CustomerID"]}, {"$set": {"Budget": new_budget, "TotalSpent": new_spent}})
                                mongo.db.orders.update_one({"OrderID": order_id}, {"$set": {"Status": "Approved"}})
                                ctype = "Premium" if customer.get("CustomerType") == "Premium" else "Standard"
                                log_event("order_approved", f"Müşteri {customer['CustomerID']} ({ctype}), Product{product['ProductID']} ürününden {quantity} adet aldı. Toplam Harcama: {total_cost}.", customer["CustomerID"], product["ProductID"])
                            else:
                                mongo.db.orders.update_one({"OrderID": order_id}, {"$set": {"Status": "Rejected"}})
                                log_event("order_rejected", f"Müşteri {customer['CustomerID']} bütçe yetersiz: Sipariş ID {order_id}", customer["CustomerID"], product["ProductID"])
                        else:
                            mongo.db.orders.update_one({"OrderID": order_id}, {"$set": {"Status": "Rejected"}})
                            log_event("order_rejected", f"Stok yetersiz: Product{product['ProductID']} için sipariş ID {order_id}", customer["CustomerID"], product["ProductID"])
                    log_event("worker_info", f"Sipariş işlendi: {order_id}", customer["CustomerID"], product["ProductID"])
                except Exception as e:
                    log_event("worker_error", f"Worker hata: {str(e)}", None, None)
        else:
            time.sleep(1)

def start_worker_threads():
    for _ in range(3):
        t = threading.Thread(target=order_processor, daemon=True)
        t.start()
