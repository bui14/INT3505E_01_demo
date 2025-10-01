from flask import Flask, request
from flask_restful import Resource, Api
from datetime import datetime

app = Flask(__name__)
api = Api(app)

BOOKS = {
    1: {"title": "Lập trình Python cơ bản", "author": "Nguyễn Văn C", "status": "available"},
    2: {"title": "Kiến trúc REST API", "author": "Trần Thị D", "status": "available"},
    3: {"title": "Lịch sử Việt Nam", "author": "Phạm Văn E", "status": "on loan"}
}
next_book_id = 4
next_loan_id = 1
LOANS = {}

# --- QUẢN LÝ SÁCH ---

class BookList(Resource):
    def get(self):
        return BOOKS, 200

    def post(self):
        global next_book_id
        data = request.get_json()
        
        if not data or 'title' not in data or 'author' not in data:
            return {"message": "Thiếu tiêu đề hoặc tác giả."}, 400
            
        new_book = {"title": data['title'], "author": data['author'], "status": "available"}
        BOOKS[next_book_id] = new_book
        new_book_id = next_book_id
        next_book_id += 1
        
        return {"message": "Thêm sách thành công", "book_id": new_book_id, "book": new_book}, 201

class Book(Resource):
    def get(self, book_id):
        if book_id not in BOOKS:
            return {"message": "Không tìm thấy sách."}, 404
        return BOOKS[book_id], 200

    def put(self, book_id):
        if book_id not in BOOKS:
            return {"message": "Không tìm thấy sách."}, 404
            
        data = request.get_json()
        if 'title' in data: BOOKS[book_id]['title'] = data['title']
        if 'author' in data: BOOKS[book_id]['author'] = data['author']
            
        return {"message": "Cập nhật sách thành công", "book": BOOKS[book_id]}, 200

    def delete(self, book_id):
        if book_id not in BOOKS:
            return {"message": "Không tìm thấy sách."}, 404
        
        del BOOKS[book_id]
        return {"message": "Xóa sách thành công"}, 204

# --- MƯỢN/TRẢ SÁCH ---

class LoanManagement(Resource):
    def get(self):
        return LOANS, 200

    def post(self):
        global next_loan_id
        data = request.get_json()
        book_id = data.get('book_id')
        member_id = data.get('member_id')

        if not book_id or not member_id:
            return {"message": "Thiếu book_id hoặc member_id."}, 400

        try:
            book_id = int(book_id)
        except ValueError:
            return {"message": "book_id không hợp lệ."}, 400

        if book_id not in BOOKS:
            return {"message": "Sách không tồn tại."}, 404
        
        if BOOKS[book_id]['status'] != 'available':
            return {"message": "Sách đang được mượn."}, 409

        BOOKS[book_id]['status'] = 'on loan'
        
        new_loan = {
            "book_id": book_id,
            "member_id": member_id,
            "loan_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "return_date": None
        }
        LOANS[next_loan_id] = new_loan
        new_loan_id = next_loan_id
        next_loan_id += 1
        
        return {"message": "Mượn sách thành công", "loan_id": new_loan_id, "loan": new_loan}, 201

class LoanReturn(Resource):
    def put(self, loan_id):
        try:
            loan_id = int(loan_id)
        except ValueError:
             return {"message": "loan_id không hợp lệ."}, 400

        if loan_id not in LOANS:
            return {"message": "Không tìm thấy giao dịch mượn."}, 404
            
        loan = LOANS[loan_id]

        if loan['return_date'] is not None:
            return {"message": "Sách đã được trả."}, 409

        loan['return_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        book_id = loan['book_id']
        if book_id in BOOKS:
            BOOKS[book_id]['status'] = 'available'
        
        return {"message": "Trả sách thành công", "loan": loan}, 200

# --- ĐỊNH NGHĨA ENDPOINT ---
api.add_resource(BookList, '/api/books')
api.add_resource(Book, '/api/books/<int:book_id>')
api.add_resource(LoanManagement, '/api/loans')
api.add_resource(LoanReturn, '/api/loans/<loan_id>/return')

if __name__ == '__main__':
    app.run(debug=True)