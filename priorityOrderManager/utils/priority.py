import time
BASE_PREMIUM = 15
BASE_STANDARD = 10
WAIT_WEIGHT = 0.5

def compute_priority(customer_type, created_at):
    current_time = time.time()
    wait_time = current_time - created_at
    base = BASE_PREMIUM if customer_type == "Premium" else BASE_STANDARD
    return base + (wait_time * WAIT_WEIGHT)
