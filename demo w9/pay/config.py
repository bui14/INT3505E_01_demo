# config.py
from datetime import datetime

class Config:
    # Cấu hình cho v1
    V1_DEPRECATED = True
    # Lưu ý: Python datetime(Năm, Tháng, Ngày, Giờ, Phút, Giây)
    V1_SUNSET_DATE = datetime(2025, 12, 31, 23, 59, 59) 
    MIGRATION_LINK = "https://payfast.com/docs/migration-v1-to-v2"