import heapq, threading, time
from utils.priority import compute_priority

queue_lock = threading.Lock()

class PriorityOrderQueue:
    def __init__(self):
        self.heap = []
        self.counter = 0

    def push(self, initial_priority, order_data):
        with queue_lock:
            self.counter += 1
            heapq.heappush(self.heap, (-initial_priority, self.counter, order_data))

    def pop(self):
        with queue_lock:
            if not self.heap:
                return None
            current_orders = []
            while self.heap:
                neg_priority, cnt, data = heapq.heappop(self.heap)
                new_priority = compute_priority(data["customer_type"], data["created_at"])
                current_orders.append((new_priority, cnt, data))
            for p, c, d in current_orders:
                heapq.heappush(self.heap, (-p, c, d))
            if self.heap:
                _, _, order_data = heapq.heappop(self.heap)
                return order_data
            return None

    def get_all_recalculated(self):
        with queue_lock:
            if not self.heap:
                return []
            current_orders = []
            while self.heap:
                neg_priority, cnt, data = heapq.heappop(self.heap)
                new_priority = compute_priority(data["customer_type"], data["created_at"])
                current_orders.append((new_priority, cnt, data))
            for p, c, d in current_orders:
                heapq.heappush(self.heap, (-p, c, d))
            from extensions import mongo
            result = []
            temp = []
            while self.heap:
                neg_p, c, d = heapq.heappop(self.heap)
                p = -neg_p
                order = mongo.db.orders.find_one({"OrderID": d["order_id"]})
                if order:
                    wait_time = round(time.time() - d["created_at"], 2)
                    order["WaitTime"] = wait_time
                    order["DynamicPriority"] = round(p, 2)
                    result.append(order)
                temp.append((neg_p, c, d))
            for item in temp:
                heapq.heappush(self.heap, item)
            result.sort(key=lambda x: x["DynamicPriority"], reverse=True)
            return result

order_queue = PriorityOrderQueue()
