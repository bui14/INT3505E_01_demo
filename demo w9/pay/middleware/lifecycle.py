# middleware/lifecycle.py
from flask import request, jsonify, make_response
from datetime import datetime
from config import Config

def apply_lifecycle_manager(blueprint):
    """
    Hàm này gắn logic Lifecycle vào một Blueprint cụ thể.
    """
    
    # 1. Chạy TRƯỚC khi vào logic chính (Kiểm tra Sunset)
    @blueprint.before_request
    def check_sunset():
        now = datetime.now()
        if now > Config.V1_SUNSET_DATE:
            # Trả về lỗi 410 Gone và DỪNG xử lý ngay lập tức
            return jsonify({
                "error": "gone",
                "message": "This API version has been permanently removed.",
                "more_info": Config.MIGRATION_LINK,
                "sunset": Config.V1_SUNSET_DATE.strftime("%a, %d %b %Y %H:%M:%S GMT")
            }), 410

    # 2. Chạy SAU khi logic chính xong (Thêm Header Deprecation)
    @blueprint.after_request
    def add_deprecation_headers(response):
        if Config.V1_DEPRECATED:
            # Format ngày tháng theo chuẩn HTTP (RFC 1123)
            sunset_str = Config.V1_SUNSET_DATE.strftime("%a, %d %b %Y %H:%M:%S GMT")
            
            # Header chuẩn RFC 8594
            response.headers['Deprecation'] = sunset_str
            
            # Header chuẩn RFC 8288
            response.headers['Link'] = f'<{Config.MIGRATION_LINK}>; rel="deprecation"; type="text/html"'
            
            # Header cảnh báo phụ
            response.headers['X-API-Warning'] = 'Version v1 is deprecated. Please migrate to v2.'
            
        return response