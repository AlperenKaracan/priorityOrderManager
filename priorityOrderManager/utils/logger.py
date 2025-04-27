from datetime import datetime
from extensions import mongo
import threading

log_lock = threading.Lock()

def log_event(log_type, message, customer_id=None, product_id=None):
    with log_lock:
        try:
            customer_name = "Unknown"
            customer_type = "Standard"
            if customer_id:
                customer = mongo.db.customers.find_one({"CustomerID": customer_id})
                if customer:
                    customer_name = customer.get("CustomerName", "Unknown")
                    customer_type = customer.get("CustomerType", "Standard")
            log_entry = {
                "log_type": log_type,
                "message": message,
                "CustomerID": customer_id,
                "customer_name": customer_name,
                "customer_type": customer_type,
                "product_id": product_id,
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            }
            mongo.db.logs.insert_one(log_entry)
            print(f"Log eklendi: {log_type} - {message}")
        except Exception as e:
            print(f"Log eklenirken hata: {e}")
