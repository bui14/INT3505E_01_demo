from flask import Flask, jsonify
from extensions import limiter
from v1.routes import v1_bp
from v2.routes import v2_bp

app = Flask(__name__)

limiter.init_app(app)

app.register_blueprint(v1_bp)
app.register_blueprint(v2_bp)

# Xử lý lỗi 429 (Too Many Requests) - Trả về JSON thay vì HTML
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "error": "too_many_requests",
        "message": f"Bạn đã gửi yêu cầu quá nhanh! {e.description}",
        "code": 429,
        "hint": "Hệ thống đang áp dụng giới hạn 3 requests / 10 giây."
    }), 429

# Xử lý lỗi 404 (Not Found)
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": "not_found",
        "message": "Endpoint không tồn tại. Vui lòng kiểm tra lại URL."
    }), 404

# Xử lý lỗi 500 (Internal Server Error)
@app.errorhandler(500)
def server_error(e):
    return jsonify({
        "error": "internal_server_error",
        "message": "Đã có lỗi xảy ra phía server."
    }), 500

@app.route('/')
def health_check():
    return "PayFast API Gateway is running with Rate Limiting & Circuit Breaker."

if __name__ == '__main__':
    print("🚀 Server running on http://localhost:5000")
    print("🛡️  Rate Limit Policy: Active (3 req/10s on v2)")
    print("⚡ Circuit Breaker: Ready")
    print("   - v1: POST /v1/charges (Deprecated)")
    print("   - v2: POST /v2/payment-intents (Active)")
    
    app.run(port=5000, debug=True)