# v1/routes.py
from flask import Blueprint, jsonify, request
from middleware.lifecycle import apply_lifecycle_manager
from config import Config  # <--- BƯỚC 1: Import Config để lấy trạng thái

v1_bp = Blueprint('v1', __name__, url_prefix='/v1')

apply_lifecycle_manager(v1_bp)

@v1_bp.route('/charges', methods=['POST'])
def create_charge():
    data = request.get_json()
    amount = data.get('amount')
    # 1. Lấy card_token từ request gửi lên
    card_token = data.get('card_token', 'tok_unknown') 
    
    print(f"[v1] Processing sync charge for {amount} using {card_token}...")
    
    # 2. Tạo dictionary chứa dữ liệu phản hồi (Chưa chuyển thành JSON ngay)
    response_payload = {
        "id": "ch_legacy_123456",
        "object": "charge",
        "amount": amount,
        "currency": "vnd",
        "paid": True,
        "status": "succeeded",
        "source": {
            "id": "card_gen_from_" + card_token,
            "object": "card",
            "brand": "Visa",
            "last4": "4242",       
            "exp_month": 12,
            "exp_year": 2025
        },
        "description": "Processed via v1 (Deprecated)"
    }

    # 3. --- CHÈN CẢNH BÁO VÀO BODY ---
    # Kiểm tra trong Config, nếu đang Deprecated thì thêm field "warning"
    if Config.V1_DEPRECATED:
        response_payload["warning"] = {
            "type": "deprecation_warning",
            "code": "api_v1_sunset",
            "message": f"⚠️ WARNING: This API version is deprecated. It will stop working on {Config.V1_SUNSET_DATE.strftime('%Y-%m-%d')}.",
            "action_required": "Please migrate to v2 Payment Intents API.",
            "docs_url": Config.MIGRATION_LINK
        }

    # 4. Trả về kết quả cuối cùng
    return jsonify(response_payload), 200