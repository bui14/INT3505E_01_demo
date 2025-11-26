# v2/routes.py
from flask import Blueprint, jsonify, request

v2_bp = Blueprint('v2', __name__, url_prefix='/v2')

@v2_bp.route('/payment-intents', methods=['POST'])
def create_payment_intent():
    data = request.get_json()
    amount = data.get('amount')
    currency = data.get('currency', 'usd')
    payment_method = data.get('payment_method') # Lấy ID thẻ/ví (VD: pm_card_visa)
    return_url = data.get('return_url')         # URL để quay về sau khi xác thực xong

    print(f"[v2] Creating payment intent for {amount} {currency}...")

    # Cấu trúc cơ bản
    response = {
        "id": "pi_modern_999",
        "object": "payment_intent",
        "amount": amount,
        "currency": currency,
        "client_secret": "secret_abc_123_xyz",
        "created": 1732600000
    }

    # LOGIC ĐIỀU HƯỚNG TRẠNG THÁI (State Machine)
    
    # TRƯỜNG HỢP 1: Client chưa gửi thông tin thẻ/ví
    if not payment_method:
        response["status"] = "requires_payment_method"
        # Không có link redirect vì chưa biết user dùng thẻ gì
        # Client cần hiển thị form nhập thẻ ở bước này.
    
    # TRƯỜNG HỢP 2: Client đã gửi thẻ (Giả lập thẻ cần 3D Secure/OTP)
    else:
        response["status"] = "requires_action"
        response["payment_method"] = payment_method
        
        # ĐÂY LÀ PHẦN BẠN CẦN: Link hướng dẫn bước tiếp theo
        response["next_action"] = {
            "type": "redirect_to_url",
            "redirect_to_url": {
                # Link giả lập trang nhập OTP của Ngân hàng
                "url": "https://hooks.stripe.com/redirect/authenticate/src_123?client_secret=secret_abc",
                # Link merchant muốn user quay về sau khi nhập OTP xong
                "return_url": return_url 
            }
        }

    return jsonify(response), 200