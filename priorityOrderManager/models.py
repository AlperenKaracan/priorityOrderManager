from extensions import mongo

def init_db():
    initial_products = [
        {"ProductID": 1, "ProductName": "Product1", "Stock": 100},
        {"ProductID": 2, "ProductName": "Product2", "Stock": 200},
        {"ProductID": 3, "ProductName": "Product3", "Stock": 50},
        {"ProductID": 4, "ProductName": "Product4", "Stock": 300},
        {"ProductID": 5, "ProductName": "Product5", "Stock": 1000},
    ]
    mongo.db.products.insert_many(initial_products)

    initial_customers = [
        {"CustomerID": 1, "CustomerName": "Müşteri 1", "Budget": 10000, "CustomerType": "Premium", "TotalSpent": 0},
        {"CustomerID": 2, "CustomerName": "Müşteri 2", "Budget": 5000, "CustomerType": "Standard", "TotalSpent": 0},
        {"CustomerID": 3, "CustomerName": "Müşteri 3", "Budget": 8000, "CustomerType": "Premium", "TotalSpent": 0},
        {"CustomerID": 4, "CustomerName": "Müşteri 4", "Budget": 2000, "CustomerType": "Standard", "TotalSpent": 0},
        {"CustomerID": 5, "CustomerName": "Müşteri 5", "Budget": 6000, "CustomerType": "Standard", "TotalSpent": 0},
    ]
    mongo.db.customers.insert_many(initial_customers)
