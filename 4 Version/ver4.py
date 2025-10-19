from flask import Flask, request, url_for, make_response
from flask_restful import Resource, Api
from functools import wraps
import uuid
import hashlib # Thư viện để tạo hash
import json    # Thư viện để chuyển dict thành chuỗi JSON

app = Flask(__name__)
api = Api(app)

books = {
    "b1": {"title": "Nhà Giả Kim", "author": "Paulo Coelho"},
    "b2": {"title": "Bố Già", "author": "Mario Puzo"},
}

users = {
    "user1_key": {"name": "Alice"},
    "user2_key": {"name": "Bob"}
}

# --- DECORATOR XỬ LÝ CACHE ---
def cacheable_etag(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        # 1. Gọi hàm gốc để lấy dữ liệu và status code
        response_data, status_code = func(*args, **kwargs)
        
        # 2. Tạo ETag từ hash của dữ liệu
        # Chuyển dict thành chuỗi JSON và hash nó
        etag = hashlib.sha1(json.dumps(response_data, sort_keys=True).encode()).hexdigest()
        
        # 3. Kiểm tra header 'If-None-Match' từ client
        client_etag = request.headers.get('If-None-Match')
        
        # 4. Nếu ETag khớp, trả về 304 Not Modified
        if client_etag == etag:
            return '', 304 # Thân response rỗng
            
        # 5. Nếu không, tạo response đầy đủ và gắn ETag vào header
        response = make_response(json.dumps(response_data), status_code)
        response.headers['Content-Type'] = 'application/json'
        response.headers['ETag'] = etag
        return response
        
    return decorated

def require_apikey(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('Authorization')
        if api_key and api_key in users:
            return func(*args, **kwargs)
        else:
            return {"error": "Unauthorized. Cần cung cấp API Key hợp lệ trong header 'Authorization'."}, 401
    return decorated

class Book(Resource):
    @require_apikey
    @cacheable_etag # Áp dụng cache cho phương thức này
    def get(self, book_id):
        if book_id not in books:
            return {"error": "Không tìm thấy sách"}, 404
        
        book_data = books[book_id].copy()
        book_data["_links"] = {
            "self": {"href": url_for('book', book_id=book_id)},
            "collection": {"href": url_for('booklist')}
        }
        # Decorator yêu cầu trả về tuple (data, status_code)
        return book_data, 200

    @require_apikey
    def put(self, book_id):
        if book_id not in books:
            return {"error": "Không tìm thấy sách"}, 404
        update_data = request.json
        books[book_id] = {'title': update_data['title'], 'author': update_data['author']}
        return books[book_id], 200

    @require_apikey
    def delete(self, book_id):
        if book_id not in books:
            return {"error": "Không tìm thấy sách"}, 404
        del books[book_id]
        return '', 204

class BookList(Resource):
    @cacheable_etag # Áp dụng cache cho phương thức này
    def get(self):
        response_data = {}
        for book_id, book_info in books.items():
            response_data[book_id] = {
                "title": book_info["title"],
                "author": book_info["author"],
                "_links": {
                    "self": {"href": url_for('book', book_id=book_id)}
                }
            }
        return response_data, 200
    
    @require_apikey
    def post(self):
        api_key = request.headers.get('Authorization')
        user_name = users[api_key]['name']
        new_book = request.json
        new_id = str(uuid.uuid4())[:4]
        books[new_id] = {'title': new_book['title'], 'author': new_book['author']}
        new_book_url = url_for('book', book_id=new_id)
        response_body = {
            "id": new_id,
            "message": f"User '{user_name}' đã thêm sách thành công!",
            "book": books[new_id],
            "_links": {"self": {"href": new_book_url}}
        }
        return response_body, 201, {'Location': new_book_url}

api.add_resource(BookList, '/api/books', endpoint='booklist')
api.add_resource(Book, '/api/books/<string:book_id>', endpoint='book')

if __name__ == '__main__':
    print("API Server đang chạy với ETag Caching.")
    app.run(debug=True, port=5000)