# app.py

from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint
import os

# Import the V1 Blueprint
from routes_v1 import v1_bp 
# Import db (optional, just to ensure it's loaded if needed globally, though unlikely now)
# import db 

app = Flask(__name__)
# Set SECRET_KEY
app.config['SECRET_KEY'] = 'super_secret_key_for_library_api'

# --- REGISTER API V1 BLUEPRINT ---
app.register_blueprint(v1_bp) 

# --- INTEGRATE SWAGGER UI ---
SWAGGER_URL = '/api/docs'
API_URL = '/static/openapi.yaml' # Points to the YAML file in static/

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={ 'app_name': "Library API Specification", 'displayRequestDuration': True }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

if __name__ == '__main__':
    # Ensure static directory exists
    if not os.path.exists('static'): os.makedirs('static')
    # Check for openapi.yaml (create placeholder if missing)
    if not os.path.exists('static/openapi.yaml'):
        with open('static/openapi.yaml', 'w') as f:
            f.write("openapi: 3.0.0\ninfo:\n  title: Placeholder API\n  version: 1.0.0\npaths: {}")
        print("Cảnh báo: File 'static/openapi.yaml' không tồn tại. Đã tạo file placeholder.")

    print("-" * 50)
    print(f"Ứng dụng Flask đang chạy...")
    # Update print message to reflect V1 path
    print(f"API V1 có sẵn tại: http://127.0.0.1:5000/api/v1/...") 
    print(f"Swagger UI có sẵn tại: http://127.0.0.1:5000{SWAGGER_URL}")
    print("-" * 50)
    app.run(debug=True)