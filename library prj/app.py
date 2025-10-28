# app.py

from flask import Flask
from flask_restful import Api
from flask_swagger_ui import get_swaggerui_blueprint
import os

# Import hàm khởi tạo routes
import routes_v1
# Import db để đảm bảo dữ liệu được load (nếu cần)
import db

app = Flask(__name__)
# Thiết lập SECRET_KEY
app.config['SECRET_KEY'] = 'super_secret_key_for_library_api'
api = Api(app) # Tạo đối tượng Api

# --- GỌI HÀM KHỞI TẠO ROUTES ---
routes_v1.initialize_routes(api, app.config) # Truyền api và config vào routes_v1

# --- TÍCH HỢP SWAGGER UI ---
SWAGGER_URL = '/api/docs'
API_URL = '/static/openapi.yaml'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={ 'app_name': "Library API Specification", 'displayRequestDuration': True }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

if __name__ == '__main__':
    if not os.path.exists('static'): os.makedirs('static')
    if not os.path.exists('static/openapi.yaml'):
        with open('static/openapi.yaml', 'w') as f:
            f.write("openapi: 3.0.0\ninfo:\n  title: Placeholder API\n  version: 1.0.0\npaths: {}")
        print("Cảnh báo: File 'static/openapi.yaml' không tồn tại. Đã tạo file placeholder.")

    print("-" * 50)
    print(f"Ứng dụng Flask đang chạy...")
    print(f"Swagger UI có sẵn tại: http://127.0.0.1:5000{SWAGGER_URL}")
    print("-" * 50)
    app.run(debug=True)