from flask import Flask, jsonify, request, Blueprint

app = Flask(__name__)

# --- Dữ liệu giả lập (Mock Data) ---
users_db = {
    1: {"username": "alice", "email": "alice@example.com"},
    2: {"username": "bob", "email": "bob@example.com"},
}

articles_db = {
    101: {"author_id": 1, "title": "Intro to REST APIs", "content": "..."},
    102: {"author_id": 2, "title": "Python Best Practices", "content": "..."},
    103: {"author_id": 1, "title": "Flask for Beginners", "content": "..."},
}

# --- Helper function for error responses ---
def create_error_response(message, status_code):
    # CONSISTENCY: Mọi response lỗi đều có cấu trúc giống nhau
    return jsonify({"error": message}), status_code

# === API Endpoints ===

@app.route('/v1/users', methods=['GET'])
def get_users():
    """Lấy danh sách tất cả người dùng."""
    # NAMING: Dùng danh từ số nhiều "users"
    return jsonify(users_db)

@app.route('/v1/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Lấy thông tin một người dùng cụ thể."""
    if user_id not in users_db:
        return create_error_response("User not found", 404)
    
    user_data = users_db[user_id]
    
    # EXTENSIBILITY: Dùng HATEOAS để gợi ý các tài nguyên liên quan
    user_data["_links"] = {
        "self": f"/v1/users/{user_id}",
        "articles": f"/v1/users/{user_id}/articles" # Link để khám phá bài viết của user
    }
    return jsonify(user_data)

@app.route('/v1/articles', methods=['GET'])
def get_articles():
    """Lấy danh sách tất cả bài viết."""
    # EXTENSIBILITY: Cho phép lọc bài viết theo tác giả
    author_id_filter = request.args.get('author_id', type=int)
    
    if author_id_filter:
        filtered_articles = {
            id: article for id, article in articles_db.items() 
            if article["author_id"] == author_id_filter
        }
        return jsonify(filtered_articles)
        
    return jsonify(articles_db)

@app.route('/v1/users/<int:user_id>/articles', methods=['GET'])
def get_articles_by_user(user_id):
    """Lấy danh sách bài viết của một người dùng cụ thể."""
    # CLARITY: URL này rất rõ ràng, tự nó mô tả chức năng
    if user_id not in users_db:
        return create_error_response("User not found", 404)
        
    user_articles = {
        id: article for id, article in articles_db.items() 
        if article["author_id"] == user_id
    }
    return jsonify(user_articles)

if __name__ == '__main__':
    app.run(debug=True, port=5000)