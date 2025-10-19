from flask import Flask, request, url_for
from flask_restful import Resource, Api
import uuid

app = Flask(__name__)
api = Api(app)

# Dữ liệu sách
books = {
    "b1": {"title": "Nhà Giả Kim", "author": "Paulo Coelho"},
    "b2": {"title": "Bố Già", "author": "Mario Puzo"},
}

# --- Resource cho một cuốn sách cụ thể (/api/books/<id>) ---
# Nguyên tắc 1: Identification of Resources - Định danh tài nguyên cụ thể
class Book(Resource):
    def get(self, book_id):
        """Xử lý GET: Lấy thông tin một cuốn sách."""
        if book_id not in books:
            # Nguyên tắc 3: Self-descriptive Message - Dùng mã 404 khi không tìm thấy
            return {"error": "Không tìm thấy sách"}, 404
        
        book_data = books[book_id]
        # Nguyên tắc 4: HATEOAS - Cung cấp link cho các hành động liên quan
        book_data["_links"] = {
            "self": {"href": url_for('book', book_id=book_id)},
            "collection": {"href": url_for('booklist')}
        }
        return book_data, 200

    def put(self, book_id):
        """Xử lý PUT: Cập nhật thông tin một cuốn sách."""
        # Nguyên tắc 2: Manipulation via Representations - Cập nhật bằng biểu diễn JSON
        if book_id not in books:
            return {"error": "Không tìm thấy sách"}, 404
            
        update_data = request.json
        if not update_data or 'title' not in update_data or 'author' not in update_data:
            return {"error": "Dữ liệu không hợp lệ"}, 400
            
        books[book_id] = {'title': update_data['title'], 'author': update_data['author']}
        
        print(f"SERVER: Đã cập nhật sách ID={book_id}.")
        return books[book_id], 200

    def delete(self, book_id):
        """Xử lý DELETE: Xóa một cuốn sách."""
        if book_id not in books:
            return {"error": "Không tìm thấy sách"}, 404
            
        del books[book_id]
        print(f"SERVER: Đã xóa sách ID={book_id}.")
        # Nguyên tắc 3: Self-descriptive Message - Dùng mã 204 cho xóa thành công
        return '', 204

# --- Resource cho danh sách sách (/api/books) ---
class BookList(Resource):
    def get(self):
        """Xử lý GET: Lấy danh sách tất cả sách."""
        print(f"SERVER: Nhận yêu cầu GET /api/books.")
        
        # Nguyên tắc 4: HATEOAS - Thêm link cho từng tài nguyên trong danh sách
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

    def post(self):
        """Xử lý POST: Thêm sách mới."""
        new_book = request.json
        if not new_book or 'title' not in new_book or 'author' not in new_book:
            return {"error": "Dữ liệu không hợp lệ"}, 400

        new_id = str(uuid.uuid4())[:4]
        books[new_id] = {'title': new_book['title'], 'author': new_book['author']}
        
        # Tạo URL cho tài nguyên vừa tạo
        new_book_url = url_for('book', book_id=new_id)
        
        response_body = {
            "id": new_id,
            "message": "Đã thêm sách thành công!",
            "book": books[new_id],
            # Nguyên tắc 4: HATEOAS - Cung cấp link đến tài nguyên mới
            "_links": {
                "self": {"href": new_book_url}
            }
        }
        
        print(f"SERVER: Đã thêm sách mới ID={new_id}.")
        # Nguyên tắc 3: Self-descriptive - Trả về header Location
        return response_body, 201, {'Location': new_book_url}

# --- Cấu hình các Endpoint ---
# `endpoint` giúp url_for() có thể tạo link
api.add_resource(BookList, '/api/books', endpoint='booklist')
api.add_resource(Book, '/api/books/<string:book_id>', endpoint='book')

if __name__ == '__main__':
    print("API Server đang chạy và áp dụng Uniform Interface.")
    app.run(debug=True, port=5000)