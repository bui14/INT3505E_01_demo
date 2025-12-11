from flask import Blueprint, jsonify, request
import pybreaker
from extensions import limiter
from services.bank_service import bank_service

v2_bp = Blueprint('v2', __name__, url_prefix='/v2')

@v2_bp.route('/payment-intents', methods=['POST'])
# --- RATE LIMITING: Demo Window Time (3 request / 10 giây) ---
@limiter.limit("3 per 10 seconds") 
def create_payment_intent():    
    try:
        data = request.get_json() or {}
        amount = data.get('amount')
        currency = data.get('currency', 'usd')
        payment_method = data.get('payment_method')
        return_url = data.get('return_url')

        print(f"[v2] Creating payment intent for {amount} {currency}...")

        response = {
            "id": "pi_modern_999",
            "object": "payment_intent",
            "amount": amount,
            "currency": currency,
            "client_secret": "secret_abc_123_xyz",
            "created": 1732600000
        }

        # TRƯỜNG HỢP 1: Client chưa gửi thông tin thẻ (Chưa cần gọi Bank)
        if not payment_method:
            response["status"] = "requires_payment_method"
            # Không làm gì thêm, return ngay
        
        # TRƯỜNG HỢP 2: Client đã gửi thẻ -> GỌI NGÂN HÀNG
        else:
            # --- CIRCUIT BREAKER PROTECTED CALL ---
            # Gọi service này sẽ kích hoạt Cầu dao nếu ngân hàng lỗi
            # Nếu cầu dao đang MỞ, dòng này sẽ raise lỗi CircuitBreakerError ngay lập tức
            bank_result = bank_service.charge_card(amount)

            response["status"] = "requires_action"
            response["payment_method"] = payment_method
            response["bank_transaction_id"] = bank_result.get("transaction_id") # Kèm ID từ ngân hàng

            response["next_action"] = {
                "type": "redirect_to_url",
                "redirect_to_url": {
                    "url": "https://hooks.stripe.com/redirect/authenticate/src_123?client_secret=secret_abc",
                    "return_url": return_url 
                }
            }

        return jsonify(response), 200

    # --- XỬ LÝ LỖI CIRCUIT BREAKER (FAIL FAST) ---
    # Khi cầu dao MỞ, code sẽ nhảy thẳng vào đây, không cần chờ timeout
    except pybreaker.CircuitBreakerError:
        return jsonify({
            "error": "service_unavailable",
            "message": "Hệ thống Ngân hàng đang quá tải (Circuit Breaker OPEN). Vui lòng thử lại sau.",
            "code": "circuit_open"
        }), 503

    except Exception as e:
        return jsonify({
            "error": "bank_error",
            "message": str(e)
        }), 502