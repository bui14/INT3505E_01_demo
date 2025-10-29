# routes_v1.py

from flask import request, jsonify, make_response, Blueprint, current_app
from flask_restful import Api, Resource
from datetime import datetime, timedelta, timezone # Thêm timezone
import jwt
import functools 
from bson import ObjectId # Import ObjectId for querying
from pydantic_core import ValidationError # Import ValidationError
# Import get_db và Schemas từ db_mongo.py
from db_mongo import get_db, UserSchema, BookSchema, ReviewSchema 
# Import password hashing if needed (assuming User password needs hashing/checking)
from werkzeug.security import check_password_hash, generate_password_hash

# --- CREATE BLUEPRINT and API for V1 ---
v1_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')
api_v1 = Api(v1_bp) # Attach Flask-RESTful Api to the Blueprint

# --- DECORATORS (using current_app for config) ---
def jwt_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '): return {"message": "Unauthorized: Yêu cầu JWT Token."}, 401
        token = token.split(' ')[1]
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"]) 
            # Lưu cả username và role vào request context nếu cần
            request.jwt_identity = data.get('username') 
            request.user_role = data.get('role')
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError): return {"message": "Unauthorized: Token không hợp lệ hoặc hết hạn."}, 401
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        # jwt_required phải chạy trước để gán request.user_role
        if not hasattr(request, 'user_role') or request.user_role != 'admin': return {"message": "Forbidden: Yêu cầu quyền Admin."}, 403
        return f(*args, **kwargs)
    return wrapper

# --- RESOURCES ---

class LoginV1(Resource):
    def post(self):
        db = get_db()
        if not db: return {"message": "Database connection failed."}, 500
        
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
             return {"message": "Thiếu username hoặc password."}, 400

        user_doc = db.users.find_one({"username": username})
        
        # Kiểm tra user tồn tại và mật khẩu (đã hash)
        if user_doc and check_password_hash(user_doc.get('password', ''), password):
            payload = {
                'username': username, 
                'role': user_doc.get('role'),
                'exp': datetime.now(timezone.utc) + timedelta(minutes=30), # Use timezone aware datetime
                'iat': datetime.now(timezone.utc)
            }
            token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm="HS256") 
            return { "message": "Đăng nhập thành công", "token": token, "token_type": "Bearer"}, 200

        return {"message": "Sai tên đăng nhập hoặc mật khẩu."}, 401

class BookListV1(Resource):
    def get(self):
        db = get_db()
        if not db: return {"message": "Database connection failed."}, 500
        
        try:
            offset = int(request.args.get('offset', 0))
            limit = int(request.args.get('limit', 10))
            search_query = request.args.get('q', '').strip() # Strip whitespace
        except ValueError: return {"message": "Offset và Limit phải là số nguyên."}, 400
        if limit < 1 or limit > 100: return {"message": "Limit phải nằm trong khoảng 1 đến 100."}, 400

        # --- MongoDB Query ---
        query_filter = {}
        if search_query:
            # Tìm kiếm không phân biệt hoa thường ($regex, $options: 'i')
            regex = {"$regex": search_query, "$options": "i"}
            query_filter["$or"] = [
                {"title": regex},
                {"author": regex}
            ]
            
        total_count = db.books.count_documents(query_filter)
        books_cursor = db.books.find(query_filter).sort("_id", 1).skip(offset).limit(limit)
        paged_books_list = list(books_cursor)

        # Chuyển đổi ObjectId thành str và chuẩn bị data
        data_response = []
        for book in paged_books_list:
            book['_id'] = str(book['_id']) # Convert ObjectId to string
            data_response.append(book)
        
        # --- Metadata & HATEOAS ---
        metadata = {"total_count": total_count, "current_items": len(paged_books_list), "offset": offset, "limit": limit, "next_offset": offset + limit if offset + limit < total_count else None}
        base_url = f"{request.url_root.rstrip('/')}{v1_bp.url_prefix}/books" 
        query_params_str = f"q={search_query}&" if search_query else ""
        links = {"self": f"{base_url}?{query_params_str}offset={offset}&limit={limit}", "first": f"{base_url}?{query_params_str}offset=0&limit={limit}"}
        last_offset = total_count - (total_count % limit or limit)
        links["last"] = f"{base_url}?{query_params_str}offset={last_offset if last_offset >= 0 else 0}&limit={limit}" if total_count > 0 else f"{base_url}?{query_params_str}offset=0&limit={limit}"
        if metadata["next_offset"] is not None: links["next"] = f"{base_url}?{query_params_str}offset={metadata['next_offset']}&limit={limit}"
        if offset > 0: links["prev"] = f"{base_url}?{query_params_str}offset={max(0, offset - limit)}&limit={limit}"
        
        response_data = jsonify({"data": data_response, "pagination": metadata, "_links": links, "actions": {"create_book": {"method": "POST", "href": base_url, "schema_ref": "/api/docs#/components/schemas/BookInput"}}})
        res = make_response(response_data); res.headers.set('Cache-Control', 'public, max-age=60'); return res

    @jwt_required
    def post(self):
        db = get_db()
        if not db: return {"message": "Database connection failed."}, 500
        
        data = request.get_json();
        if not data: return {"message": "Không có dữ liệu JSON trong body."}, 400

        # Validate with Pydantic
        try:
            book_model = BookSchema(**data)
            book_to_insert = book_model.model_dump(exclude={'id'}) # Exclude id for insertion
        except ValidationError as e:
            return {"message": f"Dữ liệu sách không hợp lệ: {e}"}, 400
        except Exception as e:
             return {"message": f"Lỗi xử lý dữ liệu sách: {e}"}, 400

        # Insert into MongoDB
        try:
             insert_result = db.books.insert_one(book_to_insert)
             new_book_id = insert_result.inserted_id
        except Exception as e:
             return {"message": f"Lỗi khi thêm sách vào database: {e}"}, 500

        book_url = f"{request.url_root.rstrip('/')}{v1_bp.url_prefix}/books/{new_book_id}"
        # Prepare response data (convert ObjectId to str)
        book_to_insert['_id'] = new_book_id 
        response_book = BookSchema.model_validate(book_to_insert).model_dump(mode='json') 

        return {
            "message": "Thêm sách thành công", 
            "book_id": str(new_book_id), # Return ID as string
            "book": response_book, 
            "_links": { "self": book_url, "edit": book_url, "delete": book_url, "reviews": f"{request.url_root.rstrip('/')}{v1_bp.url_prefix}/books/{new_book_id}/reviews"}
            }, 201

class BookV1(Resource):
    def get(self, book_id_str):
        db = get_db()
        if not db: return {"message": "Database connection failed."}, 500
        
        try:
            book_oid = ObjectId(book_id_str)
        except Exception:
            return {"message": "Invalid Book ID format."}, 400
            
        book_doc = db.books.find_one({"_id": book_oid})
        if not book_doc: return {"message": f"Không tìm thấy sách ID {book_id_str}."}, 404
        
        book_url = f"{request.url_root.rstrip('/')}{v1_bp.url_prefix}/books/{book_id_str}"
        links = {"self": book_url, "reviews": f"{request.url_root.rstrip('/')}{v1_bp.url_prefix}/books/{book_id_str}/reviews", "edit": book_url, "delete": book_url}
        
        # Validate and serialize using Pydantic
        response_book = BookSchema.model_validate(book_doc).model_dump(mode='json')

        response_data = jsonify({**response_book, "_links": links, "actions": {"update_book": {"method": "PUT", "href": links['edit'], "schema_ref": "/api/docs#/components/schemas/BookInput"}, "delete_book": {"method": "DELETE", "href": links['delete']}}})
        res = make_response(response_data); res.headers.set('Cache-Control', 'public, max-age=60'); return res

    @jwt_required
    @admin_required
    def put(self, book_id_str):
        db = get_db()
        if not db: return {"message": "Database connection failed."}, 500
        
        try:
            book_oid = ObjectId(book_id_str)
        except Exception: return {"message": "Invalid Book ID format."}, 400
            
        data = request.get_json();
        if not data: return {"message": "Không có dữ liệu JSON trong body."}, 400

        # Validate input data (allow partial updates)
        update_data = {}
        if 'title' in data: update_data['title'] = data['title']
        if 'author' in data: update_data['author'] = data['author']
        
        if not update_data:
             return {"message": "Không có trường nào để cập nhật."}, 400
             
        # Optional: Validate update_data against a partial BookSchema if needed
             
        try:
            result = db.books.update_one({"_id": book_oid}, {"$set": update_data})
            if result.matched_count == 0:
                return {"message": f"Không tìm thấy sách ID {book_id_str}."}, 404
            
            # Fetch the updated document to return
            updated_book_doc = db.books.find_one({"_id": book_oid})
            response_book = BookSchema.model_validate(updated_book_doc).model_dump(mode='json')
            
            return {"message": "Cập nhật sách thành công", "book": response_book}, 200
            
        except Exception as e:
            return {"message": f"Lỗi khi cập nhật sách: {e}"}, 500

    @jwt_required
    @admin_required
    def delete(self, book_id_str):
        db = get_db()
        if not db: return {"message": "Database connection failed."}, 500
        
        try:
            book_oid = ObjectId(book_id_str)
        except Exception: return {"message": "Invalid Book ID format."}, 400
        
        try:
            result = db.books.delete_one({"_id": book_oid})
            if result.deleted_count == 0:
                return {"message": f"Không tìm thấy sách ID {book_id_str}."}, 404
            
            # Optionally: Delete related reviews (or handle via DB triggers/logic if possible)
            # db.reviews.delete_many({"book_id": book_oid}) 
                
            return {"message": "Xóa sách thành công"}, 204 # Use 204 No Content for DELETE success
            
        except Exception as e:
             return {"message": f"Lỗi khi xóa sách: {e}"}, 500

class ReviewListV1(Resource):
    # GET /api/v1/books/{book_id}/reviews (N+1 Avoidance)
    def get(self, book_id_str): 
        db = get_db()
        if not db: return {"message": "Database connection failed."}, 500
        try:
            book_oid = ObjectId(book_id_str)
        except Exception: return {"message": "Invalid Book ID format."}, 400

        book = db.books.find_one({"_id": book_oid}, {"title": 1}) # Fetch only title
        if not book: return {"message": f"Không tìm thấy Sách với ID {book_id_str}."}, 404

        try:
            offset = int(request.args.get('offset', 0)); limit = int(request.args.get('limit', 10))
        except ValueError: return {"message": "Offset/Limit phải là số nguyên."}, 400

        reviews_cursor = db.reviews.find({"book_id": book_oid}).sort("_id", 1).skip(offset).limit(limit)
        paged_reviews = list(reviews_cursor)
        total_count = db.reviews.count_documents({"book_id": book_oid}) 

        usernames = list(set(r.get('username') for r in paged_reviews if r.get('username')))
        users_map = {}
        if usernames:
            users_cursor = db.users.find({"username": {"$in": usernames}}, {"_id": 0, "username": 1, "name": 1}) 
            users_map = {user['username']: user.get('name', user['username']) for user in users_cursor}

        results = []
        book_title = book.get('title', 'N/A') 
        for review in paged_reviews:
            reviewer_name = users_map.get(review.get('username'), review.get('username', 'Unknown')) 
            # Validate and serialize each review
            try:
                review_model = ReviewSchema.model_validate(review)
                review_dict = review_model.model_dump(mode='json') # Convert ObjectId to str
                results.append({
                    **review_dict, # Include all validated review fields
                    "book_title": book_title, # Add related data
                    "reviewer_name": reviewer_name # Add related data
                    # Remove original book_id and username if redundant
                    # 'book_id': str(review_dict.get('book_id')), 
                    # 'username': review_dict.get('username'), 
                })
            except ValidationError as e:
                 print(f"Warning: Skipping review due to validation error: {e}") # Log error, skip invalid doc
                 continue

        metadata = { "total_count": total_count, "current_items": len(results), "offset": offset, "limit": limit, "next_offset": offset + limit if offset + limit < total_count else None}
        base_url = f"{request.url_root.rstrip('/')}{v1_bp.url_prefix}/books/{book_id_str}/reviews"
        links = {"self": f"{base_url}?offset={offset}&limit={limit}", "book_detail": f"{request.url_root.rstrip('/')}{v1_bp.url_prefix}/books/{book_id_str}", "add_review": {"method": "POST", "href": base_url, "schema_ref": "/api/docs#/components/schemas/ReviewInput"}}
        if metadata["next_offset"] is not None: links["next"] = f"{base_url}?offset={metadata['next_offset']}&limit={limit}"
        if offset > 0: links["prev"] = f"{base_url}?offset={max(0, offset - limit)}&limit={limit}"
        
        response_data = jsonify({"data": results, "pagination": metadata, "_links": links})
        res = make_response(response_data); res.headers.set('Cache-Control', 'public, max-age=10'); return res

    @jwt_required
    def post(self, book_id_str): 
        db = get_db()
        if not db: return {"message": "Database connection failed."}, 500
        try:
            book_oid = ObjectId(book_id_str)
        except Exception: return {"message": "Invalid Book ID format."}, 400
        if db.books.count_documents({"_id": book_oid}) == 0: return {"message": f"Không tìm thấy Sách với ID {book_id_str}."}, 404

        data = request.get_json(); rating = data.get('rating');
        if not rating or not (1 <= rating <= 5): return {"message": "Rating phải từ 1 đến 5."}, 400

        try:
            review_data = { "book_id": book_oid, "username": request.jwt_identity, "rating": rating, "comment": data.get('comment', '')}
            review_model = ReviewSchema(**review_data)
            review_to_insert = review_model.model_dump(exclude={'id'}) 
        except ValidationError as e: return {"message": f"Dữ liệu review không hợp lệ: {e}"}, 400
        except Exception as e: return {"message": f"Lỗi xử lý dữ liệu review: {e}"}, 400

        try:
            insert_result = db.reviews.insert_one(review_to_insert)
            new_review_id = insert_result.inserted_id
        except Exception as e: return {"message": f"Lỗi khi thêm review: {e}"}, 500

        review_url = f"{request.url_root.rstrip('/')}{v1_bp.url_prefix}/books/{book_id_str}/reviews/{new_review_id}" 
        review_to_insert['_id'] = new_review_id 
        response_review = ReviewSchema.model_validate(review_to_insert).model_dump(mode='json') 

        return { "message": "Thêm nhận xét thành công", "review_id": str(new_review_id), "review": response_review, "_links": { "self": review_url, "book_detail": f"{request.url_root.rstrip('/')}{v1_bp.url_prefix}/books/{book_id_str}"}}, 201

class ReadingTimeCodeV1(Resource):
    def get(self):
        js_code = """ function calculateReadingTime(wordCount) { const wordsPerMinute = 250; const minutes = Math.ceil(wordCount / wordsPerMinute); return { minutes: minutes, message: `Thời gian đọc ước tính là khoảng ${minutes} phút.` }; } """
        res = make_response(js_code); res.headers.set('Content-Type', 'application/javascript'); return res

# --- REGISTER RESOURCES WITH THE BLUEPRINT API ---
api_v1.add_resource(LoginV1, '/auth/login')
api_v1.add_resource(BookListV1, '/books')
api_v1.add_resource(BookV1, '/books/<string:book_id_str>') # Use string for ObjectId
api_v1.add_resource(ReadingTimeCodeV1, '/books/code/reading-time')
api_v1.add_resource(ReviewListV1, '/books/<string:book_id_str>/reviews') # Use string for ObjectId