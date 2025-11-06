# db_mongo.py
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os

# --- Imports for Pydantic Schemas (Updated for V2) ---
from pydantic import BaseModel, Field, field_validator, ConfigDict # Import field_validator and ConfigDict
from pydantic_core import ValidationError # Import ValidationError for consistency
from typing import Optional, List
from bson import ObjectId 
# ----------------------------------------------------

# --- Cấu hình Kết nối MongoDB (UPDATED) ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://huyhoag282_db_user:1fwvo2somZsA4KDG@cluster0.pppuzia.mongodb.net/?appName=Cluster0") 
DATABASE_NAME = "huyhoag282_db_user" # Tên database bạn muốn sử dụng
# ------------------------------------

mongo_client = None
db = None

def connect_to_mongo():
    """Thiết lập kết nối tới MongoDB."""
    global mongo_client, db
    if mongo_client is None:
        try:
            print(f"Đang kết nối tới MongoDB Atlas...") 
            mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            mongo_client.admin.command('ping') 
            print("Kết nối MongoDB Atlas thành công!")
            db = mongo_client[DATABASE_NAME]
        except ConnectionFailure as e:
            print(f"Lỗi kết nối MongoDB Atlas: {e}")
            mongo_client = None
            db = None
        except Exception as e:
            print(f"Lỗi không xác định khi kết nối MongoDB Atlas: {e}")
            mongo_client = None
            db = None
    return db

def get_db():
    """Trả về database đang kết nối, tự động đảm bảo đúng tên."""
    global db
    if db is None:
        connect_to_mongo()
    if db is not None and db.name != DATABASE_NAME:
        print(f"⚠️ Database name mismatch (expected '{DATABASE_NAME}', got '{db.name}') → switching...")
        db = mongo_client[DATABASE_NAME]
    return db

def close_mongo_connection():
    """Đóng kết nối MongoDB."""
    global mongo_client, db
    if mongo_client:
        print("Đang đóng kết nối MongoDB Atlas...")
        mongo_client.close()
        mongo_client = None
        db = None

# --- Pydantic Schema Definitions (UPDATED FOR V2) ---

# Define a shared ConfigDict for handling ObjectId serialization
# Note: Pydantic V2 often handles ObjectId better without explicit encoders, 
# but this ensures string conversion for JSON if needed.
common_config = ConfigDict(
    populate_by_name=True, 
    arbitrary_types_allowed=True, 
    json_encoders={ObjectId: str}
)

class UserSchema(BaseModel):
    model_config = common_config # Use ConfigDict

    id: Optional[ObjectId] = Field(alias='_id', default=None) 
    username: str = Field(...) 
    password: str = Field(...) 
    role: str = Field(...)

    # Use field_validator instead of validator
    @field_validator('role')
    @classmethod # Classmethod is generally preferred for field validators
    def role_must_be_admin_or_member(cls, v: str) -> str:
        if v not in ['admin', 'member']:
            raise ValueError('Role must be admin or member')
        return v

class ReviewSchema(BaseModel):
    model_config = common_config # Use ConfigDict

    id: Optional[ObjectId] = Field(alias='_id', default=None)
    book_id: ObjectId 
    username: str 
    rating: int = Field(..., ge=1, le=5) 
    comment: Optional[str] = None 

class BookSchema(BaseModel):
    model_config = common_config # Use ConfigDict

    id: Optional[ObjectId] = Field(alias='_id', default=None)
    title: str = Field(...)
    author: str = Field(...)