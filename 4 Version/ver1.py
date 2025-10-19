from flask import Flask, request
from flask_restful import Resource, Api
import uuid 

app = Flask(__name__)
api = Api(app)

books = {
    "b1": {"title": "Nhà Giả Kim", "author": "Paulo Coelho"},
    "b2": {"title": "Bố Già", "author": "Mario Puzo"},
}

class BookList(Resource):
    
    def get(self):
        """Xử lý GET: Lấy danh sách tất cả sách."""

        print(f"SERVER: Nhận yêu cầu GET /api/books.")
        
        # Trả về dữ liệu và mã trạng thái 200 (OK)
        return books, 200

    def post(self):
        """Xử lý POST: Thêm sách mới."""
        new_book = request.json
        if not new_book or 'title' not in new_book or 'author' not in new_book:
            return {"error": "Dữ liệu không hợp lệ"}, 400

        new_id = str(uuid.uuid4())[:4] 
        books[new_id] = {'title': new_book['title'], 'author': new_book['author']}

        message = "Đã thêm sách thành công!"
        
        print(f"SERVER: Đã thêm sách mới ID={new_id} (POST /api/books).")
        # Trả về tài nguyên mới được tạo và mã trạng thái 201 (Created)
        return {"id": new_id, "message": message, "book": books[new_id]}, 201

api.add_resource(BookList, '/api/books')

if __name__ == '__main__':
    # Chạy Server trên cổng 5000
    print("API Server đang chạy ở chế độ Stateless.")
    app.run(debug=True, port=5000)