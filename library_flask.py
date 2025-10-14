from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from datetime import datetime, timedelta
import jwt

app = Flask(__name__)
api = Api(app)

app.config['SECRET_KEY'] = 'super_secret_key_for_library_api'

BOOKS = {
    1: {"title": "Lập trình Python cơ bản", "author": "Nguyễn Văn C"},
    2: {"title": "Kiến trúc REST API", "author": "Trần Thị D"},
    3: {"title": "Lịch sử Việt Nam", "author": "Phạm Văn E"}
}
next_book_id = 4

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
        return BOOKS, 200

class Book(Resource):
    def get(self, book_id):
        if book_id not in BOOKS:
            return {"message": f"Không tìm thấy sách với ID {book_id}."}, 404
        return BOOKS[book_id], 200

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

api.add_resource(Login, '/api/auth/login')
api.add_resource(BookList, '/api/books')
api.add_resource(Book, '/api/books/<int:book_id>')

if __name__ == '__main__':
    app.run(debug=True)