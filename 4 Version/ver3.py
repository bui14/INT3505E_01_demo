from flask import Flask, request, url_for
from flask_restful import Resource, Api
from functools import wraps
import uuid

app = Flask(__name__)
api = Api(app)

# Dữ liệu sách
books = {
    "b1": {"title": "Nhà Giả Kim", "author": "Paulo Coelho"},
    "b2": {"title": "Bố Già", "author": "Mario Puzo"},
}

# --- XỬ LÝ STATELESS AUTHENTICATION ---
users = {
    "user1_key": {"name": "Alice"},
    "user2_key": {"name": "Bob"}
}

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
    # Áp dụng decorator cho các phương thức cần bảo vệ
    @require_apikey
    def get(self, book_id):
        if book_id not in books:
            return {"error": "Không tìm thấy sách"}, 404
        
        book_data = books[book_id].copy() # Dùng copy để tránh thay đổi dữ liệu gốc
        book_data["_links"] = {
            "self": {"href": url_for('book', book_id=book_id)},
            "collection": {"href": url_for('booklist')}
        }
        return book_data, 200

    @require_apikey
    def put(self, book_id):
        if book_id not in books:
            return {"error": "Không tìm thấy sách"}, 404
            
        update_data = request.json
        books[book_id] = {'title': update_data['title'], 'author': update_data['author']}
        print(f"SERVER: Đã cập nhật sách ID={book_id}.")
        return books[book_id], 200

    @require_apikey
    def delete(self, book_id):
        if book_id not in books:
            return {"error": "Không tìm thấy sách"}, 404
            
        del books[book_id]
        print(f"SERVER: Đã xóa sách ID={book_id}.")
        return '', 204

class BookList(Resource):
    # Phương thức GET danh sách có thể công khai, không cần key
    def get(self):
        print(f"SERVER: Nhận yêu cầu GET /api/books.")
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
    
    # Phương thức POST (thêm sách) yêu cầu phải xác thực
    @require_apikey
    def post(self):
        api_key = request.headers.get('Authorization')
        user_name = users[api_key]['name']
        
        new_book = request.json
        new_id = str(uuid.uuid4())[:4]
        books[new_id] = {'title': new_book['title'], 'author': new_book['author']}
        
        new_book_url = url_for('book', book_id=new_id)
        
        print(f"SERVER: User '{user_name}' đã thêm sách mới ID={new_id}.")
        
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
    print("API Server đang chạy với cơ chế xác thực Stateless.")
    app.run(debug=True, port=5000)