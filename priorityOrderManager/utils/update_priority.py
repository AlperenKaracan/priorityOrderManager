from extensions import mongo
from datetime import datetime
import time, logging

logger = logging.getLogger(__name__)

def update_dynamic_priorities():
    logger.debug("Dinamik öncelik güncellemesi başladı.")
    try:
        orders = mongo.db.orders.find({"Status": "Processing"})
        for o in orders:
            created_at = o.get("CreatedAt", time.time())
            base = 15 if o.get("CustomerType") == "Premium" else 10
            wait_seconds = time.time() - created_at
            dyn = base + (wait_seconds * 0.5)
            mongo.db.orders.update_one({"OrderID": o["OrderID"]}, {"$set": {"DynamicPriority": dyn}})
        logger.debug("Dinamik öncelik güncellemesi tamamlandı.")
    except Exception as e:
        logger.error(f"Dinamik öncelik hata: {e}")
