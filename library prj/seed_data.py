# seed_data.py

from db_mongo import get_db, close_mongo_connection, UserSchema, BookSchema, ReviewSchema
from bson import ObjectId
from pydantic_core import ValidationError
# Make sure to install werkzeug: pip install Werkzeug
from werkzeug.security import generate_password_hash

# --- MOCK DATA (Copied from your db.py for reference in this script) ---
# In a real app, you might read this from db.py, but keeping it here makes the script self-contained
INITIAL_BOOKS_DATA = [
    {"title": "Lập trình Python cơ bản", "author": "Nguyễn Văn C"},
    {"title": "Kiến trúc REST API", "author": "Trần Thị D"},
    {"title": "Lịch sử Việt Nam", "author": "Phạm Văn E"},
    {"title": "Cấu trúc dữ liệu và giải thuật", "author": "Lê Văn F"},
    {"title": "Thiết kế hệ thống phân tán", "author": "Hoàng Thị G"},
    {"title": "Kinh tế học vĩ mô", "author": "Đặng Văn H"},
    {"title": "Lập trình web với Flask", "author": "Nguyễn Văn C"},
    {"title": "Phân tích dữ liệu với Pandas", "author": "Trần Thị D"},
    {"title": "Cơ sở dữ liệu NoSQL", "author": "Phạm Văn E"},
    {"title": "Trí tuệ nhân tạo cơ bản", "author": "Lê Văn F"},
    {"title": "DevOps và CI/CD", "author": "Hoàng Thị G"},
    {"title": "Marketing kỹ thuật số", "author": "Đặng Văn H"}
]

INITIAL_REVIEWS_DATA = [
    # We use book_title here to look up the ObjectId later
    {"book_title": "Lập trình Python cơ bản", "username": "member", "rating": 5, "comment": "Sách cơ bản, dễ hiểu."},
    {"book_title": "Lập trình Python cơ bản", "username": "admin", "rating": 4, "comment": "Nội dung tốt, cần thêm ví dụ."},
    {"book_title": "Kiến trúc REST API", "username": "member", "rating": 5, "comment": "Hiểu sâu về RESTful design."}
]
# ---------------------------------------------------------------------

def seed_database():
    """Chèn TOÀN BỘ dữ liệu mẫu ban đầu vào MongoDB."""

    db = get_db()
    if db is None:
        print("Lỗi: Không thể kết nối tới MongoDB để chèn dữ liệu.")
        return

    print(f"Bắt đầu chèn dữ liệu mẫu vào database '{db.name}'...")

    # --- 1. Chèn Users ---
    try:
        users_collection = db["users"]
        if users_collection.count_documents({}) == 0:
            print("- Collection 'users' rỗng, đang chèn users mẫu...")
            users_data = [
                {"username": "admin", "password": generate_password_hash("adminpass"), "role": "admin"},
                {"username": "member", "password": generate_password_hash("memberpass"), "role": "member"}
            ]
            validated_users = []
            for user_d in users_data:
                try:
                    user_model = UserSchema(**user_d)
                    validated_users.append(user_model.model_dump(by_alias=True, exclude_none=True))
                except ValidationError as e:
                    print(f"  Lỗi validation User: {e}")
            if validated_users:
                users_collection.insert_many(validated_users)
                print(f"- Đã chèn {len(validated_users)} người dùng.")
        else:
            print("- Collection 'users' đã có dữ liệu, bỏ qua.")
    except Exception as e:
        print(f" Lỗi khi xử lý Users: {e}")

    # --- 2. Chèn ALL Books (hoặc lấy ID nếu đã tồn tại) ---
    book_title_to_id_map = {}
    try:
        books_collection = db["books"]

        # *** DÁN LẠI TIÊU ĐỀ CHÍNH XÁC TỪ MONGODB ATLAS VÀO ĐÂY LẦN NỮA ***
        required_titles_for_reviews = [
            "Lập trình Python cơ bản",  # <-- Copy lại chính xác từ Atlas
            "Kiến trúc REST API"       # <-- Copy lại chính xác từ Atlas
        ]
        # ******************************************************

        if books_collection.count_documents({}) == 0:
           # ... (logic chèn sách nếu rỗng giữ nguyên) ...
           pass # Giữ nguyên logic chèn và lấy ID ở đây

        else:
            print("- Collection 'books' đã có dữ liệu.")
            print(f"- Đang lấy ID cho sách có tiêu đề trong: {required_titles_for_reviews}")

            # Thực hiện query
            existing_books_cursor = books_collection.find(
                {"title": {"$in": required_titles_for_reviews}},
                {"title": 1, "_id": 1} # Chỉ lấy title và _id
            )

            # *** THÊM BƯỚC DEBUG: In ra kết quả thô từ cursor ***
            found_books_list = list(existing_books_cursor) # Chuyển cursor thành list để xem
            print(f"- Kết quả thô từ MongoDB find(): {found_books_list}")
            # **************************************************

            # Chuyển đổi kết quả query thành dictionary {title: _id}
            # Sử dụng list vừa tạo để tránh tiêu thụ cursor
            book_title_to_id_map = {book['title']: book['_id'] for book in found_books_list}

            print(f"- Tìm thấy ID cho {len(book_title_to_id_map)} sách cần thiết.")
            if len(book_title_to_id_map) > 0:
                 print(f"- IDs tìm thấy: {book_title_to_id_map}")
            elif len(required_titles_for_reviews) > 0:
                 print(f"- KHÔNG TÌM THẤY sách nào khớp với tiêu đề được yêu cầu.")
                 print("- Vui lòng kiểm tra kỹ lại tiêu đề trong `required_titles_for_reviews` và dữ liệu thực tế trên MongoDB Atlas.")

            if len(book_title_to_id_map) < len(required_titles_for_reviews):
                 print("  Cảnh báo: Không tìm thấy ID cho tất cả sách cần thiết cho reviews!")

    except Exception as e:
        print(f" Lỗi khi xử lý Books: {e}")
        book_title_to_id_map = {}

    # --- 3. Chèn ALL Reviews (Sử dụng ID sách đã lấy được) ---
    try:
        reviews_collection = db["reviews"]
        # Chỉ chèn nếu collection rỗng VÀ có ID sách để liên kết
        if reviews_collection.count_documents({}) == 0:
            if book_title_to_id_map: # Chỉ tiếp tục nếu tìm thấy ID sách
                print("- Collection 'reviews' rỗng, đang chèn toàn bộ nhận xét mẫu...")
                validated_reviews = []
                for review_d in INITIAL_REVIEWS_DATA: # Use the full list
                    book_id = book_title_to_id_map.get(review_d["book_title"])
                    if book_id:
                         try:
                            review_model = ReviewSchema(
                                book_id=book_id, # Use the ObjectId found
                                username=review_d["username"],
                                rating=review_d["rating"],
                                comment=review_d.get("comment")
                            )
                            validated_reviews.append(review_model.model_dump(by_alias=True, exclude_none=True))
                         except ValidationError as e:
                             print(f"  Lỗi validation Review: {e}")
                    else:
                        print(f"- Bỏ qua review cho '{review_d['book_title']}' vì không tìm thấy ID sách tương ứng trong database.")

                if validated_reviews:
                    reviews_collection.insert_many(validated_reviews)
                    print(f"- Đã chèn {len(validated_reviews)} nhận xét.")
            else:
                 print("- Không tìm thấy ID sách cần thiết, không thể chèn reviews.")

        else:
             print("- Collection 'reviews' đã có dữ liệu, bỏ qua.")


    except Exception as e:
        print(f" Lỗi khi chèn Reviews: {e}")

    print("\nChèn dữ liệu mẫu hoàn tất.")
    close_mongo_connection()

if __name__ == "__main__":
    seed_database()