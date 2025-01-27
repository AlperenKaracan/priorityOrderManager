import uuid
from datetime import datetime

def generate_id(prefix):
    return f"{prefix}{uuid.uuid4().hex[:8].upper()}"

def create_log(log_type, message, user="System", customer_name=None, product_id=None):
    return {
        "LogID": generate_id("L"),
        "log_type": log_type,
        "message": message,
        "customer_name": customer_name,
        "product_id": product_id,
        "timestamp": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"),
        "user": user
    }

def create_customer(name, email):
    return {
        "CustomerID": generate_id("C"),
        "name": name,
        "email": email,
        "created_at": datetime.utcnow()
    }

def create_order(customer_id, product_id, quantity):
    return {
        "OrderID": generate_id("O"),
        "customer_id": customer_id,
        "product_id": product_id,
        "quantity": quantity,
        "order_date": datetime.utcnow()
    }
