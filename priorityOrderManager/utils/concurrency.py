import threading
import logging

logger = logging.getLogger(__name__)

stock_lock = threading.Lock()
order_semaphore = threading.Semaphore(10)

def acquire_stock_lock():
    stock_lock.acquire()
    logger.debug("Stock lock acquired.")

def release_stock_lock():
    stock_lock.release()
    logger.debug("Stock lock released.")

def acquire_order_semaphore():
    order_semaphore.acquire()
    logger.debug("Order semaphore acquired.")

def release_order_semaphore():
    order_semaphore.release()
    logger.debug("Order semaphore released.")

class StockLock:
    def __enter__(self):
        acquire_stock_lock()
    def __exit__(self, exc_type, exc_val, exc_tb):
        release_stock_lock()

class OrderSemaphore:
    def __enter__(self):
        acquire_order_semaphore()
    def __exit__(self, exc_type, exc_val, exc_tb):
        release_order_semaphore()
