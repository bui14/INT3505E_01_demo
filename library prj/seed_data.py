# seed_data.py

from db_mongo import get_db, close_mongo_connection, UserSchema, BookSchema, ReviewSchema
from bson import ObjectId
from pydantic_core import ValidationError
from werkzeug.security import generate_password_hash

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
    {"book_title": "Lập trình Python cơ bản", "username": "member", "rating": 5, "comment": "Sách cơ bản, dễ hiểu."},
    {"book_title": "Lập trình Python cơ bản", "username": "admin", "rating": 4, "comment": "Nội dung tốt, cần thêm ví dụ."},
    {"book_title": "Kiến trúc REST API", "username": "member", "rating": 5, "comment": "Hiểu sâu về RESTful design."}
]

def seed_database():
    db = get_db()
    if db is None:
        print("❌ Không thể kết nối tới MongoDB.")
        return

    print(f"\n🚀 Bắt đầu chèn dữ liệu mẫu vào database '{db.name}'...")

    # 1️⃣ Reset collections
    for col_name in ["users", "books", "reviews"]:
        db[col_name].delete_many({})
        print(f"🧹 Đã xóa dữ liệu cũ trong collection '{col_name}'.")

    # 2️⃣ Users
    users_data = [
        {"username": "admin", "password": generate_password_hash("adminpass"), "role": "admin"},
        {"username": "member", "password": generate_password_hash("memberpass"), "role": "member"}
    ]
    validated_users = []
    for u in users_data:
        try:
            user = UserSchema(**u)
            validated_users.append(user.model_dump(by_alias=True, exclude_none=True))
        except ValidationError as e:
            print("❌ Lỗi validation user:", e)

    db["users"].insert_many(validated_users)
    print(f"✅ Đã chèn {len(validated_users)} người dùng.")

    # 3️⃣ Books
    validated_books = []
    for b in INITIAL_BOOKS_DATA:
        try:
            book = BookSchema(**b)
            validated_books.append(book.model_dump(by_alias=True, exclude_none=True))
        except ValidationError as e:
            print("❌ Lỗi validation book:", e)

    result = db["books"].insert_many(validated_books)
    print(f"📚 Đã chèn {len(result.inserted_ids)} sách.")

    # Tạo map {title: _id}
    book_title_to_id_map = {b["title"]: _id for b, _id in zip(INITIAL_BOOKS_DATA, result.inserted_ids)}

    # 4️⃣ Reviews
    validated_reviews = []
    for r in INITIAL_REVIEWS_DATA:
        book_id = book_title_to_id_map.get(r["book_title"])
        if not book_id:
            print(f"⚠️  Bỏ qua review cho '{r['book_title']}' (không tìm thấy sách).")
            continue
        try:
            review = ReviewSchema(
                book_id=book_id,
                username=r["username"],
                rating=r["rating"],
                comment=r.get("comment")
            )
            validated_reviews.append(review.model_dump(by_alias=True, exclude_none=True))
        except ValidationError as e:
            print("❌ Lỗi validation review:", e)

    if validated_reviews:
        db["reviews"].insert_many(validated_reviews)
        print(f"💬 Đã chèn {len(validated_reviews)} nhận xét.")

    print("\n✅ Hoàn tất seed dữ liệu!")
    close_mongo_connection()

if __name__ == "__main__":
    seed_database()
