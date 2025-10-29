# routes_v1.py

# Use current_app for accessing config within requests
from flask import request, jsonify, make_response, Blueprint, current_app
from flask_restful import Api, Resource
from datetime import datetime, timedelta
import jwt
import functools 

# Import data from db.py (assuming db.py holds the dictionaries)
import db

# --- CREATE BLUEPRINT and API for V1 ---
v1_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')
api_v1 = Api(v1_bp) # Attach Flask-RESTful Api to the Blueprint

# --- DECORATORS (using current_app for config) ---
def jwt_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return {"message": "Unauthorized: Yêu cầu JWT Token."}, 401
        token = token.split(' ')[1]
        try:
            # Use current_app.config instead of global variable
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"]) 
            request.user_role = data.get('role')
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return {"message": "Unauthorized: Token không hợp lệ hoặc hết hạn."}, 401
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if not hasattr(request, 'user_role') or request.user_role != 'admin':
            return {"message": "Forbidden: Yêu cầu quyền Admin."}, 403
        return f(*args, **kwargs)
    return wrapper

# --- RESOURCES ---
# (Using original decorator stacking with @functools.wraps)

class LoginV1(Resource): # Renamed for clarity if V2 is added later
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        user_info = db.USERS.get(username)
        if user_info and user_info['password'] == password:
            payload = {
                'username': username, 'role': user_info['role'],
                'exp': datetime.utcnow() + timedelta(minutes=30), 'iat': datetime.utcnow()
            }
            # Use current_app.config
            token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm="HS256") 
            return { "message": "Đăng nhập thành công", "token": token, "token_type": "Bearer"}, 200
        return {"message": "Sai tên đăng nhập hoặc mật khẩu."}, 401

class BookListV1(Resource):
    def get(self):
        try:
            offset = int(request.args.get('offset', 0))
            limit = int(request.args.get('limit', 10))
            search_query = request.args.get('q', '').lower()
        except ValueError: return {"message": "Offset và Limit phải là số nguyên."}, 400
        if limit < 1 or limit > 100: return {"message": "Limit phải nằm trong khoảng 1 đến 100."}, 400

        filtered_book_ids = [id for id, book in db.BOOKS.items() if not search_query or search_query in book['title'].lower() or search_query in book['author'].lower()]
        book_ids = sorted(filtered_book_ids)
        total_count = len(book_ids); paged_ids = book_ids[offset : offset + limit]
        paged_books = {id: db.BOOKS[id] for id in paged_ids}
        metadata = {"total_count": total_count, "current_items": len(paged_ids), "offset": offset, "limit": limit, "next_offset": offset + limit if offset + limit < total_count else None}
        
        # Use v1_bp.url_prefix for base URL construction
        base_url = f"{request.url_root.rstrip('/')}{v1_bp.url_prefix}/books" 
        query_params = f"q={search_query}&" if search_query else ""
        links = {"self": f"{base_url}?{query_params}offset={offset}&limit={limit}", "first": f"{base_url}?{query_params}offset=0&limit={limit}"}
        last_offset = total_count - (total_count % limit or limit)
        links["last"] = f"{base_url}?{query_params}offset={last_offset if last_offset >= 0 else 0}&limit={limit}" if total_count > 0 else f"{base_url}?{query_params}offset=0&limit={limit}"
        if metadata["next_offset"] is not None: links["next"] = f"{base_url}?{query_params}offset={metadata['next_offset']}&limit={limit}"
        if offset > 0: links["prev"] = f"{base_url}?{query_params}offset={max(0, offset - limit)}&limit={limit}"
        
        response_data = jsonify({"data": paged_books, "pagination": metadata, "_links": links, "actions": {"create_book": {"method": "POST", "href": base_url, "schema_ref": "/api/docs#/components/schemas/BookInput"}}})
        res = make_response(response_data); res.headers.set('Cache-Control', 'public, max-age=60'); return res

    @jwt_required
    def post(self):
        data = request.get_json();
        if not data or 'title' not in data or 'author' not in data: return {"message": "Thiếu 'title' hoặc 'author'."}, 400
        new_book = {"title": data['title'], "author": data['author']}
        current_id = db.next_book_id; db.BOOKS[current_id] = new_book; db.next_book_id += 1
        book_url = f"{request.url_root.rstrip('/')}{v1_bp.url_prefix}/books/{current_id}"
        return {"message": "Thêm sách thành công", "book_id": current_id, "book": new_book, "_links": {"self": book_url, "edit": book_url, "delete": book_url, "reviews": f"{request.url_root.rstrip('/')}{v1_bp.url_prefix}/books/{current_id}/reviews"}}, 201

class BookV1(Resource):
    def get(self, book_id):
        if book_id not in db.BOOKS: return {"message": f"Không tìm thấy sách ID {book_id}."}, 404
        book_data = db.BOOKS[book_id]
        book_url = f"{request.url_root.rstrip('/')}{v1_bp.url_prefix}/books/{book_id}"
        links = {"self": book_url, "reviews": f"{request.url_root.rstrip('/')}{v1_bp.url_prefix}/books/{book_id}/reviews", "edit": book_url, "delete": book_url}
        response_data = jsonify({**book_data, "_links": links, "actions": {"update_book": {"method": "PUT", "href": links['edit'], "schema_ref": "/api/docs#/components/schemas/BookInput"}, "delete_book": {"method": "DELETE", "href": links['delete']}}})
        res = make_response(response_data); res.headers.set('Cache-Control', 'public, max-age=60'); return res

    @jwt_required
    @admin_required
    def put(self, book_id):
        if book_id not in db.BOOKS: return {"message": f"Không tìm thấy sách ID {book_id}."}, 404
        data = request.get_json();
        if 'title' in data: db.BOOKS[book_id]['title'] = data['title']
        if 'author' in data: db.BOOKS[book_id]['author'] = data['author']
        return {"message": "Cập nhật sách thành công", "book": db.BOOKS[book_id]}, 200

    @jwt_required
    @admin_required
    def delete(self, book_id):
        if book_id not in db.BOOKS: return {"message": f"Không tìm thấy sách ID {book_id}."}, 404
        del db.BOOKS[book_id]; return {"message": "Xóa sách thành công"}, 204

class ReviewListV1(Resource):
    def get(self, book_id):
        if book_id not in db.BOOKS: return {"message": f"Không tìm thấy sách ID {book_id}."}, 404
        try: offset = int(request.args.get('offset', 0)); limit = int(request.args.get('limit', 10))
        except ValueError: return {"message": "Offset/Limit phải là số nguyên."}, 400
        all_reviews = [(rid, r) for rid, r in db.REVIEWS.items() if r['book_id'] == book_id]; all_reviews.sort(key=lambda item: item[0])
        total_count = len(all_reviews); paged_reviews_list = all_reviews[offset : offset + limit]; paged_reviews = {rid: r for rid, r in paged_reviews_list}
        metadata = {"total_count": total_count, "current_items": len(paged_reviews), "offset": offset, "limit": limit, "next_offset": offset + limit if offset + limit < total_count else None}
        base_url = f"{request.url_root.rstrip('/')}{v1_bp.url_prefix}/books/{book_id}/reviews"
        links = {"self": f"{base_url}?offset={offset}&limit={limit}", "book_detail": f"{request.url_root.rstrip('/')}{v1_bp.url_prefix}/books/{book_id}", "add_review": {"method": "POST", "href": base_url, "schema_ref": "/api/docs#/components/schemas/ReviewInput"}}
        if metadata["next_offset"] is not None: links["next"] = f"{base_url}?offset={metadata['next_offset']}&limit={limit}"
        response_data = jsonify({"data": paged_reviews, "pagination": metadata, "_links": links}); res = make_response(response_data); res.headers.set('Cache-Control', 'public, max-age=10'); return res

    @jwt_required
    def post(self, book_id):
        if book_id not in db.BOOKS: return {"message": f"Không tìm thấy sách ID {book_id}."}, 404
        data = request.get_json(); rating = data.get('rating');
        if not rating or not (1 <= rating <= 5): return {"message": "Rating phải từ 1 đến 5."}, 400
        new_review = {"book_id": book_id, "user": request.user_role, "rating": rating, "comment": data.get('comment', '')}
        current_id = db.next_review_id; db.REVIEWS[current_id] = new_review; db.next_review_id += 1
        review_url = f"{request.url_root.rstrip('/')}{v1_bp.url_prefix}/books/{book_id}/reviews/{current_id}" # Assuming reviews have individual IDs later
        return {"message": "Thêm nhận xét thành công", "review_id": current_id, "review": new_review, "_links": {"self": review_url, "book_detail": f"{request.url_root.rstrip('/')}{v1_bp.url_prefix}/books/{book_id}"}}, 201

class ReadingTimeCodeV1(Resource):
    def get(self):
        js_code = """ function calculateReadingTime(wordCount) { const wordsPerMinute = 250; const minutes = Math.ceil(wordCount / wordsPerMinute); return { minutes: minutes, message: `Thời gian đọc ước tính là khoảng ${minutes} phút.` }; } """
        res = make_response(js_code); res.headers.set('Content-Type', 'application/javascript'); return res


# --- REGISTER RESOURCES WITH THE BLUEPRINT API ---
# Paths are relative to the Blueprint's /api/v1 prefix
api_v1.add_resource(LoginV1, '/auth/login')
api_v1.add_resource(BookListV1, '/books')
api_v1.add_resource(BookV1, '/books/<int:book_id>')
api_v1.add_resource(ReadingTimeCodeV1, '/books/code/reading-time')
api_v1.add_resource(ReviewListV1, '/books/<int:book_id>/reviews')