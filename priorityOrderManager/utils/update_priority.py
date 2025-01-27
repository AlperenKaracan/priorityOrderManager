from extensions import mongo
from datetime import datetime
import logging
import time

logger = logging.getLogger(__name__)

def update_dynamic_priorities():
    logger.debug("Dinamik öncelik güncellemesi başladı.")
    try:
        orders=mongo.db.orders.find({"Status":"Processing"})
        for o in orders:
            cname=o.get("CustomerName","Unknown")
            date_str=o.get("Date","")
            base=15 if "Premium" in cname else 10
            try:
                od=datetime.strptime(date_str,"%Y-%m-%d")
            except:
                od=datetime.now()
            wait_days=(datetime.now()-od).days
            dyn=base+wait_days

            mongo.db.orders.update_one({"OrderID":o["OrderID"]},
                                       {"$set":{"DynamicPriority":dyn}})
        logger.debug("Dinamik öncelik güncellemesi tamamlandı.")
    except Exception as e:
        logger.error(f"Dinamik öncelik hata: {e}")
