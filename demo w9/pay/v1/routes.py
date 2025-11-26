# v1/routes.py
from flask import Blueprint, jsonify, request
from middleware.lifecycle import apply_lifecycle_manager

# Tạo Blueprint cho v1
v1_bp = Blueprint('v1', __name__, url_prefix='/v1')

# GẮN MIDDLEWARE VÀO BLUEPRINT NÀY
apply_lifecycle_manager(v1_bp)

@v1_bp.route('/charges', methods=['POST'])
def create_charge():
    data = request.get_json()
    amount = data.get('amount')
    
    # Giả lập logic cũ
    print(f"[v1] Processing sync charge for {amount}...")
    
    return jsonify({
        "id": "ch_legacy_123",
        "object": "charge",
        "amount": amount,
        "status": "succeeded",
        "description": "Processed via v1 (Deprecated)"
    }), 200