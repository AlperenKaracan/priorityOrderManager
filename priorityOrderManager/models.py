from extensions import mongo
import random

def init_db():
    initial_products = [
        {"ProductID": "P0001", "ProductName": "Product1", "Stock": 500, "Price": 100},
        {"ProductID": "P0002", "ProductName": "Product2", "Stock": 10, "Price": 50},
        {"ProductID": "P0003", "ProductName": "Product3", "Stock": 200, "Price": 45},
        {"ProductID": "P0004", "ProductName": "Product4", "Stock": 75, "Price": 75},
        {"ProductID": "P0005", "ProductName": "Product5", "Stock": 0, "Price": 500},
    ]
    mongo.db.products.insert_many(initial_products)
    num_customers = random.randint(5, 10)
    customers = []
    premium_count = 0
    for i in range(1, num_customers + 1):
        budget = random.randint(500, 3000)
        if premium_count < 2:
            customer_type = "Premium"
            premium_count += 1
        else:
            customer_type = "Premium" if random.random() < 0.3 else "Standard"
            if customer_type == "Premium":
                premium_count += 1
        customers.append({
            "CustomerID": f"C{i:04d}",
            "CustomerName": f"Müşteri {i}",
            "Budget": budget,
            "CustomerType": customer_type,
            "TotalSpent": 0
        })
    mongo.db.customers.insert_many(customers)
