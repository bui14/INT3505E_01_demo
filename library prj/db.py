# db.py

BOOKS = {
    1: {"title": "Lập trình Python cơ bản", "author": "Nguyễn Văn C"},
    2: {"title": "Kiến trúc REST API", "author": "Trần Thị D"},
    3: {"title": "Lịch sử Việt Nam", "author": "Phạm Văn E"},
    4: {"title": "Cấu trúc dữ liệu và giải thuật", "author": "Lê Văn F"},
    5: {"title": "Thiết kế hệ thống phân tán", "author": "Hoàng Thị G"},
    6: {"title": "Kinh tế học vĩ mô", "author": "Đặng Văn H"},
    7: {"title": "Lập trình web với Flask", "author": "Nguyễn Văn C"},
    8: {"title": "Phân tích dữ liệu với Pandas", "author": "Trần Thị D"},
    9: {"title": "Cơ sở dữ liệu NoSQL", "author": "Phạm Văn E"},
    10: {"title": "Trí tuệ nhân tạo cơ bản", "author": "Lê Văn F"},
    11: {"title": "DevOps và CI/CD", "author": "Hoàng Thị G"},
    12: {"title": "Marketing kỹ thuật số", "author": "Đặng Văn H"}
}
next_book_id = 13

REVIEWS = {
    1: {"book_id": 1, "user": "member", "rating": 5, "comment": "Sách cơ bản, dễ hiểu."},
    2: {"book_id": 1, "user": "admin", "rating": 4, "comment": "Nội dung tốt, cần thêm ví dụ."},
    3: {"book_id": 2, "user": "member", "rating": 5, "comment": "Hiểu sâu về RESTful design."},
}
next_review_id = 4

USERS = {
    "admin": {"password": "adminpass", "role": "admin"},
    "member": {"password": "memberpass", "role": "member"}
}