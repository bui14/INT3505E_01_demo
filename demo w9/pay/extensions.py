# extensions.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Khởi tạo Limiter (chưa gắn vào app vội)
# key_func=get_remote_address: Chặn theo địa chỉ IP
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://"
)