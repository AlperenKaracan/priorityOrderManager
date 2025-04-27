import threading, time
from extensions import mongo
from utils.logger import log_event
from resources.product import stock_lock

order_semaphore = threading.Semaphore(2)

def order_processor():
    from utils.priority_queue import order_queue
    while True:
        order_data = order_queue.pop()
        if order_data is not None:
            with order_semaphore:
                time.sleep(5)
                order_id = order_data["order_id"]
                order = mongo.db.orders.find_one({"OrderID": order_id})
                if not order:
                    continue
                customer = mongo.db.customers.find_one({"CustomerID": order["CustomerID"]})
                product = mongo.db.products.find_one({"ProductID": order["ProductID"]})
                if not customer or not product:
                    mongo.db.orders.update_one({"OrderID": order_id}, {"$set": {"Status": "Rejected", "ProcessedAt": time.time()}})
                    log_event("order_rejected", f"Müşteri {order['CustomerID']} sipariş veya ürün bulunamadı.", order["CustomerID"], order["ProductID"])
                    continue
                quantity = order["Quantity"]
                with stock_lock:
                    current_stock = product["Stock"]
                    if current_stock >= quantity:
                        new_stock = current_stock - quantity
                        mongo.db.products.update_one({"ProductID": product["ProductID"]}, {"$set": {"Stock": new_stock}})
                        total_cost = order["TotalPrice"]
                        if customer["Budget"] >= total_cost:
                            new_budget = customer["Budget"] - total_cost
                            new_spent = customer["TotalSpent"] + total_cost
                            mongo.db.customers.update_one({"CustomerID": customer["CustomerID"]}, {"$set": {"Budget": new_budget, "TotalSpent": new_spent}})
                            mongo.db.orders.update_one({"OrderID": order_id}, {"$set": {"Status": "Approved", "ProcessedAt": time.time()}})
                            log_event("order_approved", f"Müşteri {customer['CustomerID']} ({customer['CustomerType']}) {product['ProductID']} ürününden {quantity} adet aldı. Toplam: {total_cost} TL.", customer["CustomerID"], product["ProductID"])
                        else:
                            mongo.db.orders.update_one({"OrderID": order_id}, {"$set": {"Status": "Rejected", "ProcessedAt": time.time()}})
                            log_event("order_rejected", f"Müşteri {customer['CustomerID']} bütçe yetersiz.", customer["CustomerID"], product["ProductID"])
                    else:
                        mongo.db.orders.update_one({"OrderID": order_id}, {"$set": {"Status": "Rejected", "ProcessedAt": time.time()}})
                        log_event("order_rejected", f"Müşteri {customer['CustomerID']}, {product['ProductID']} stok yetersiz.", customer["CustomerID"], product["ProductID"])
        else:
            time.sleep(1)

def start_worker_threads():
    for _ in range(3):
        t = threading.Thread(target=order_processor, daemon=True)
        t.start()
