"""
ORM 模型：User 和 Item
- User: 包含认证所需的用户名、哈希密码、角色等
- Item: 与 User 一对多关联，演示外键和 relationship
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"    # ✅ 复数

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String(10), default="user")


class Item(Base):
    __tablename__ = "items"    # ✅ 复数

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), index=True, nullable=False)
    description = Column(String(500), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))    # ✅ 改成 users.id

    owner = relationship("User", backref="items")         # ✅ 改成 items
