from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api
from datetime import datetime, timedelta
import jwt

# Thêm import cho Swagger UI
from flask_swagger_ui import get_swaggerui_blueprint 
import os

app = Flask(__name__)
api = Api(app)

app.config['SECRET_KEY'] = 'super_secret_key_for_library_api'

BOOKS = {
    1: {"title": "Lập trình Python cơ bản", "author": "Nguyễn Văn C"},
    2: {"title": "Kiến trúc REST API", "author": "Trần Thị D"},
    3: {"title": "Lịch sử Việt Nam", "author": "Phạm Văn E"},
    4: {"title": "Cấu trúc dữ liệu và giải thuật", "author": "Lê Văn F"},
    5: {"title": "Thiết kế hệ thống phân tán", "author": "Hoàng Thị G"},
    6: {"title": "Kinh tế học vĩ mô", "author": "Đặng Văn H"},
    7: {"title": "Lập trình web với Flask", "author": "Nguyễn Văn C"},
    8: {"title": "Phân tích dữ liệu với Pandas", "author": "Trần Thị D"},
    9: {"title": "Cơ sở dữ liệu NoSQL", "author": "Phạm Văn E"},
    10: {"title": "Trí tuệ nhân tạo cơ bản", "author": "Lê Văn F"},
    11: {"title": "DevOps và CI/CD", "author": "Hoàng Thị G"},
    12: {"title": "Marketing kỹ thuật số", "author": "Đặng Văn H"}
}
next_book_id = 13

REVIEWS = {
    1: {"book_id": 1, "user": "member", "rating": 5, "comment": "Sách cơ bản, dễ hiểu."},
    2: {"book_id": 1, "user": "admin", "rating": 4, "comment": "Nội dung tốt, cần thêm ví dụ."},
    3: {"book_id": 2, "user": "member", "rating": 5, "comment": "Hiểu sâu về RESTful design."},
}
next_review_id = 4

USERS = {
    "admin": {"password": "adminpass", "role": "admin"},
    "member": {"password": "memberpass", "role": "member"}
}

def jwt_required(f):
    """Decorator kiểm tra JWT và vai trò (role) của người dùng."""
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token or not token.startswith('Bearer '):
            return {"message": "Unauthorized: Yêu cầu JWT Token trong Header Authorization (Bearer <token>)."}, 401
        
        token = token.split(' ')[1]
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            request.user_role = data.get('role') 
            
        except jwt.ExpiredSignatureError:
            return {"message": "Unauthorized: Token đã hết hạn."}, 401
        except jwt.InvalidTokenError:
            return {"message": "Unauthorized: Token không hợp lệ."}, 401
        
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    """Decorator kiểm tra quyền Admin sau khi JWT đã được xác thực."""
    def wrapper(*args, **kwargs):
        if not hasattr(request, 'user_role') or request.user_role != 'admin':
            return {"message": "Forbidden: Chỉ Admin mới có quyền thực hiện thao tác này."}, 403
        return f(*args, **kwargs)
    return wrapper

# Code on demand
class ReadingTimeCode(Resource):
    def get(self):
        js_code = """
        /* JS Function: Ước tính thời gian đọc dựa trên số lượng từ */
        function calculateReadingTime(wordCount) {
            // Giả sử tốc độ đọc trung bình là 250 từ/phút
            const wordsPerMinute = 250;
            const minutes = Math.ceil(wordCount / wordsPerMinute);
            return {
                minutes: minutes,
                message: `Thời gian đọc ước tính là khoảng ${minutes} phút.`
            };
        }
        """

        res = make_response(js_code)

        res.headers.set('Content-Type', 'application/javascript')
        
        return res
    
class ReviewList(Resource):
    def get(self, book_id):

        # 1. Lấy tham số phân trang
        try:
            offset = int(request.args.get('offset', 0))
            limit = int(request.args.get('limit', 10))
        except ValueError:
            return {"message": "Offset và Limit phải là số nguyên."}, 400

        if book_id not in BOOKS:
            return {"message": f"Không tìm thấy Sách với ID {book_id}."}, 404
        
        # 2. Lọc và Sắp xếp tất cả nhận xét thuộc về book_id
        # Chuyển dictionary thành list các tuples (r_id, review) để sắp xếp
        all_reviews = [
            (r_id, review) 
            for r_id, review in REVIEWS.items() 
            if review['book_id'] == book_id
        ]
        
        # Sắp xếp theo ID nhận xét (r_id)
        all_reviews.sort(key=lambda item: item[0])
        
        total_count = len(all_reviews)

        # 3. Áp dụng OFFSET và LIMIT bằng slicing
        paged_reviews_list = all_reviews[offset : offset + limit]
        
        # Chuyển lại thành dictionary để phản hồi
        paged_reviews = {r_id: review for r_id, review in paged_reviews_list}

        # 4. Tạo Metadata
        metadata = {
            "total_count": total_count,
            "current_items": len(paged_reviews),
            "offset": offset,
            "limit": limit,
            "next_offset": offset + limit if offset + limit < total_count else None
        }
        
        # 5. Phản hồi JSON chuẩn
        response_data = jsonify({"data": paged_reviews, "pagination": metadata})
        res = make_response(response_data)
        res.headers.set('Cache-Control', 'public, max-age=10') 
        return res

    @jwt_required
    def post(self, book_id):
        global next_review_id

        if book_id not in BOOKS:
            return {"message": f"Không tìm thấy Sách với ID {book_id}."}, 404
        
        data = request.get_json()
        rating = data.get('rating')
        comment = data.get('comment', '')

        if not rating or not (1 <= rating <= 5):
            return {"message": "Đánh giá (rating) phải là số từ 1 đến 5."}, 400

        new_review = {
            "book_id": book_id,
            "user": request.user_role,
            "rating": rating,
            "comment": comment
        }
        
        REVIEWS[next_review_id] = new_review
        new_review_id = next_review_id
        next_review_id += 1

        return {"message": "Thêm nhận xét thành công", "review_id": new_review_id, "review": new_review}, 201
    
class Login(Resource):
    """POST /api/auth/login để lấy JWT Token."""
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user_info = USERS.get(username)
        
        if user_info and user_info['password'] == password:
            payload = {
                'username': username,
                'role': user_info['role'],
                'exp': datetime.utcnow() + timedelta(minutes=30),
                'iat': datetime.utcnow()
            }

            token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm="HS256")

            return jsonify({
                "message": "Đăng nhập thành công",
                "token": token,
                "token_type": "Bearer"
            }), 200

        return {"message": "Sai tên đăng nhập hoặc mật khẩu."}, 401

class BookList(Resource):
    def get(self):
        try:
            # offset: Bắt đầu từ bản ghi thứ bao nhiêu (mặc định 0)
            # limit: Số lượng bản ghi tối đa trên một trang (mặc định 10)
            offset = int(request.args.get('offset', 0))
            limit = int(request.args.get('limit', 10))
        except ValueError:
            return {"message": "Offset và Limit phải là số nguyên."}, 400

        # Kiểm tra giới hạn (tùy chọn)
        if limit < 1 or limit > 100:
            return {"message": "Limit phải nằm trong khoảng 1 đến 100."}, 400

        # 2. Xử lý logic phân trang
        book_ids = sorted(BOOKS.keys()) # Sắp xếp ID để đảm bảo thứ tự
        total_count = len(BOOKS)
        
        # Áp dụng OFFSET và LIMIT bằng slicing của Python
        paged_ids = book_ids[offset : offset + limit]
        
        # Lấy dữ liệu sách cho trang hiện tại
        paged_books = {
            id: BOOKS[id] 
            for id in paged_ids
        }
        
        # 3. Tạo Metadata Phân trang (Rất quan trọng cho Client)
        metadata = {
            "total_count": total_count,
            "current_items": len(paged_ids),
            "offset": offset,
            "limit": limit,
            # Link/Offset cho trang tiếp theo (chỉ khi còn sách)
            "next_offset": offset + limit if offset + limit < total_count else None
        }

        # 4. Tạo phản hồi JSON chuẩn (bao gồm data và pagination)
        response_data = jsonify({"data": paged_books, "pagination": metadata})
        res = make_response(response_data)

        #Cache - control
        res.headers.set('Cache-Control', 'public, max-age=60') 
        return res
    
    @jwt_required 
    def post(self):
        global next_book_id
        
        data = request.get_json()
        if not data or 'title' not in data or 'author' not in data:
            return {"message": "Thiếu 'title' hoặc 'author' trong payload."}, 400
            
        new_book = {"title": data['title'], "author": data['author']}
        BOOKS[next_book_id] = new_book
        new_book_id = next_book_id
        next_book_id += 1

        return {"message": "Thêm sách thành công", "book_id": new_book_id, "book": new_book}, 201

class Book(Resource):
    def get(self, book_id):
        if book_id not in BOOKS:
            return {"message": f"Không tìm thấy sách với ID {book_id}."}, 404

        response_data = jsonify(BOOKS[book_id])

        res = make_response(response_data)

        res.headers.set('Cache-Control', 'public, max-age=60')
        
        return res

    @jwt_required
    @admin_required
    def put(self, book_id):
        
        if book_id not in BOOKS:
            return {"message": f"Không tìm thấy sách với ID {book_id}."}, 404
            
        data = request.get_json()
        if 'title' in data: BOOKS[book_id]['title'] = data['title']
        if 'author' in data: BOOKS[book_id]['author'] = data['author']
            
        return {"message": "Cập nhật sách thành công", "book": BOOKS[book_id]}, 200

    @jwt_required
    @admin_required
    def delete(self, book_id):
        
        if book_id not in BOOKS:
            return {"message": f"Không tìm thấy sách với ID {book_id}."}, 404
        
        del BOOKS[book_id]
        return {"message": "Xóa sách thành công"}, 204

# --- TÍCH HỢP SWAGGER UI ---
SWAGGER_URL = '/api/docs'
API_URL = '/static/openapi.yaml' # Trỏ đến file YAML trong thư mục static

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Library API Specification",
        'displayRequestDuration': True
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

api.add_resource(Login, '/api/auth/login')
api.add_resource(BookList, '/api/books')
api.add_resource(Book, '/api/books/<int:book_id>')
api.add_resource(ReadingTimeCode, '/api/books/code/reading-time')
api.add_resource(ReviewList, '/api/books/<int:book_id>/reviews')

if __name__ == '__main__':
    print("-" * 50)
    print(f"Ứng dụng Flask đang chạy...")
    print(f"Swagger UI có sẵn tại: http://127.0.0.1:5000{SWAGGER_URL}")
    print("-" * 50)
    app.run(debug=True)