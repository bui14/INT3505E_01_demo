# app.py
from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint
import os

# --- Import kết nối MongoDB ---
from db_mongo import get_db, close_mongo_connection

# --- Tạo Flask App ---
app = Flask(__name__)

# Thiết lập khóa bảo mật
app.config['SECRET_KEY'] = 'super_secret_key_for_library_api'

try:
    from routes_v1 import v1_bp, limiter
except ImportError as e:
    print(f"❌ Lỗi Import: {e}. Kiểm tra lại tên file routes_v1.py hoặc biến limiter.")
    exit(1)

limiter.init_app(app)

# Đăng ký Blueprint
app.register_blueprint(v1_bp)

with app.app_context():
    db = get_db()
    if db is not None:
        try:
            print(f"✅ Đã kết nối MongoDB. Database: {db.name}")
            # print(f"Collections: {db.list_collection_names()}") # Uncomment nếu muốn xem collections
        except Exception as e:
            print(f"⚠️ Kết nối được nhưng gặp lỗi khi truy vấn: {e}")
    else:
        print("❌ Cảnh báo: Không thể kết nối MongoDB!")

SWAGGER_URL = '/api/docs'
API_URL = '/static/openapi.yaml'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Library API Specification",
        'displayRequestDuration': True
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.teardown_appcontext
def shutdown_session(exception=None):
    close_mongo_connection()

if __name__ == '__main__':
    if not os.path.exists('static'):
        os.makedirs('static')

    if not os.path.exists('static/openapi.yaml'):
        with open('static/openapi.yaml', 'w') as f:
            f.write("openapi: 3.0.0\ninfo:\n  title: Library API\n  version: 1.0.0\npaths: {}")
        print("⚠️ File 'static/openapi.yaml' đã được tạo mới.")

    print("-" * 50)
    print("🚀 Ứng dụng Flask đang khởi động...")
    print(f"🔹 Rate Limiter: Enabled (Storage: Memory)")
    print("📘 API V1 Root: http://127.0.0.1:5000/api/v1/books")
    print("📗 Swagger UI:  http://127.0.0.1:5000/api/docs")
    print("-" * 50)
    
    app.run(debug=True)