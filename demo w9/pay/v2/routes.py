# v2/routes.py
from flask import Blueprint, jsonify, request

# Tạo Blueprint cho v2
v2_bp = Blueprint('v2', __name__, url_prefix='/v2')

@v2_bp.route('/payment-intents', methods=['POST'])
def create_payment_intent():
    data = request.get_json()
    amount = data.get('amount')
    currency = data.get('currency', 'usd')
    
    # Giả lập logic mới (Async/Intent)
    print(f"[v2] Creating payment intent for {amount} {currency}...")
    
    return jsonify({
        "id": "pi_modern_999",
        "object": "payment_intent",
        "amount": amount,
        "currency": currency,
        "status": "requires_payment_method",
        "client_secret": "secret_abc_123"
    }), 200