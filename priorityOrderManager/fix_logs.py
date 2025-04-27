from extensions import mongo
from app import app

def fix_logs():
    with app.app_context():
        print("Eksik loglar tamamlanıyor...")
        logs = mongo.db.logs.find({"$or": [{"customer_name": {"$exists": False}}, {"customer_type": {"$exists": False}}]})
        for log in logs:
            customer_id = log.get("CustomerID")
            customer = mongo.db.customers.find_one({"CustomerID": customer_id})
            if customer:
                customer_name = customer.get("CustomerName", "Unknown")
                customer_type = customer.get("CustomerType", "Standard")
            else:
                customer_name = "Unknown"
                customer_type = "Standard"
            mongo.db.logs.update_one(
                {"_id": log["_id"]},
                {"$set": {"customer_name": customer_name, "customer_type": customer_type}}
            )
        print("Eksik loglar tamamlandı.")

if __name__ == "__main__":
    fix_logs()
