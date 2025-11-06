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

# --- Kết nối MongoDB khi khởi động ---
db = get_db()
if db is not None:
    print(f"✅ Đã kết nối MongoDB, Flask đang sử dụng database: {db.name}")
    print(f"✅ Collections hiện có: {db.list_collection_names()}")
else:
    print("❌ Không thể kết nối MongoDB!")

# --- Import các route sau khi DB sẵn sàng ---
from routes_v1 import v1_bp  # Đảm bảo routes có thể gọi get_db()

# --- Đăng ký API Blueprint ---
app.register_blueprint(v1_bp)

# --- Tích hợp Swagger UI ---
SWAGGER_URL = '/api/docs'
API_URL = '/static/openapi.yaml'  # Điểm tới file YAML mô tả API

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Library API Specification",
        'displayRequestDuration': True
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# --- Đóng kết nối khi Flask tắt ---
@app.teardown_appcontext
def shutdown_session(exception=None):
    close_mongo_connection()

# --- Main ---
if __name__ == '__main__':
    # Đảm bảo thư mục static tồn tại
    if not os.path.exists('static'):
        os.makedirs('static')

    # Tạo file openapi.yaml nếu chưa có
    if not os.path.exists('static/openapi.yaml'):
        with open('static/openapi.yaml', 'w') as f:
            f.write("openapi: 3.0.0\ninfo:\n  title: Placeholder API\n  version: 1.0.0\npaths: {}")
        print("⚠️  File 'static/openapi.yaml' chưa tồn tại. Đã tạo file placeholder.")

    print("-" * 50)
    print("🚀 Ứng dụng Flask đang khởi động...")
    print("📘 API V1: http://127.0.0.1:5000/api/v1/...")
    print("📗 Swagger UI: http://127.0.0.1:5000/api/docs")
    print("-" * 50)
    app.run(debug=True)
