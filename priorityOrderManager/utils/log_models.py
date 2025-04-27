import uuid
from datetime import datetime

def generate_id(prefix):
    return f"{prefix}{uuid.uuid4().hex[:8].upper()}"

def create_log(log_type, message, customer_id=None, customer_name=None, customer_type=None, product_id=None):
    return {
        "LogID": generate_id("L"),
        "log_type": log_type,
        "message": message,
        "CustomerID": customer_id,
        "customer_name": customer_name,
        "customer_type": customer_type,
        "product_id": product_id,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }
