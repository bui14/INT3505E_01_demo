import pybreaker
import time
import random

bank_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=10)

class BankService:
    @bank_breaker
    def charge_card(self, amount):
        """
        Giả lập gọi sang API Ngân hàng.
        """
        # 1. Giả lập độ trễ mạng
        time.sleep(0.1)

        # 2. Giả lập lỗi (Để test Circuit Breaker)
        if False: 
            raise Exception("Bank API Timeout / Connection Error")

        return {
            "transaction_id": f"txn_{random.randint(1000,9999)}",
            "status": "success"
        }

bank_service = BankService()