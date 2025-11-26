# main.py
from flask import Flask
from v1.routes import v1_bp
from v2.routes import v2_bp

app = Flask(__name__)

# Đăng ký các Blueprint (tương đương app.use trong Express)
app.register_blueprint(v1_bp)
app.register_blueprint(v2_bp)

@app.route('/')
def health_check():
    return "PayFast API Gateway (Python/Flask) is running."

if __name__ == '__main__':
    print("🚀 Server running on http://localhost:5000")
    print("   - v1: POST http://localhost:5000/v1/charges (Deprecated)")
    print("   - v2: POST http://localhost:5000/v2/payment-intents (Active)")
    
    app.run(port=5000, debug=True)