from flask import Flask, jsonify, request, Blueprint

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

# Thêm dữ liệu mới cho V2
comments_db = {
    301: {"article_id": 101, "user": "bob", "text": "Great intro!"},
    302: {"article_id": 101, "user": "alice", "text": "Thanks!"},
    303: {"article_id": 102, "user": "alice", "text": "Very useful article."},
}

def create_error_response(message, status_code):
    # CONSISTENCY: Mọi response lỗi đều có cấu trúc giống nhau
    return jsonify({"error": message}), status_code

v2_bp = Blueprint('api_v2', __name__, url_prefix='/v2')

@v2_bp.route('/users', methods=['GET'])
def get_users_v2():
    """V2: Lấy danh sách tất cả người dùng (giống V1)."""
    return jsonify(users_db)

@v2_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user_v2(user_id):
    """V2: Lấy thông tin user với cấu trúc MỚI (Breaking Change)."""
    if user_id not in users_db:
        return create_error_response("User not found", 404)
    
    user_data_v1 = users_db[user_id]
    
    # 1. THAY ĐỔI CẤU TRÚC (BREAKING CHANGE)
    # Chúng ta thay đổi cấu trúc, đưa email vào object 'profile'
    user_data_v2 = {
        "id": user_id,
        "username": user_data_v1["username"],
        "profile": {
            "email": user_data_v1["email"],
            "join_date": "2023-01-01" # 2. THÊM TRƯỜNG MỚI
        }
    }
    
    # 3. THÊM DỮ LIỆU MỚI (NON-BREAKING)
    # Thêm số lượng bài viết của user
    article_count = len([a for a in articles_db.values() if a["author_id"] == user_id])
    user_data_v2["article_count"] = article_count
    
    # Cập nhật links để trỏ đến V2
    user_data_v2["_links"] = {
        "self": f"/v2/users/{user_id}",
        "articles": f"/v2/users/{user_id}/articles"
    }
    return jsonify(user_data_v2)

@v2_bp.route('/articles', methods=['GET'])
def get_articles_v2():
    """V2: Lấy danh sách tất cả bài viết (giống V1)."""
    author_id_filter = request.args.get('author_id', type=int)
    
    if author_id_filter:
        filtered_articles = {
            id: article for id, article in articles_db.items() 
            if article["author_id"] == author_id_filter
        }
        return jsonify(filtered_articles)
        
    return jsonify(articles_db)

@v2_bp.route('/users/<int:user_id>/articles', methods=['GET'])
def get_articles_by_user_v2(user_id):
    """V2: Lấy danh sách bài viết của user (giống V1)."""
    if user_id not in users_db:
        return create_error_response("User not found", 404)
        
    user_articles = {
        id: article for id, article in articles_db.items() 
        if article["author_id"] == user_id
    }
    return jsonify(user_articles)

# 4. THÊM ENDPOINT HOÀN TOÀN MỚI TRONG V2
@v2_bp.route('/articles/<int:article_id>/comments', methods=['GET'])
def get_comments_for_article(article_id):
    """Vi: Lấy tất cả bình luận cho một bài viết."""
    if article_id not in articles_db:
        return create_error_response("Article not found", 404)
    
    article_comments = {
        id: c for id, c in comments_db.items() 
        if c["article_id"] == article_id
    }
    return jsonify(article_comments)

# === Đăng ký các Blueprints vào ứng dụng chính ===
app.register_blueprint(v1_bp)
app.register_blueprint(v2_bp)

if __name__ == '__main__':
    print("API Server đang chạy với 2 phiên bản (V1 và V2):")
    print("V1: http://127.0.0.1:5000/v1/...")
    print("V2: http://127.0.0.1:5000/v2/...")
    app.run(debug=True, port=5000)