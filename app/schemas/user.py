"""
用户相关Pydantic Schema
-UserBase:公共字段
-UserCreate:注册请求,包含密码和自定义验证
-UserOut:响应,排除密码,支持ORM模式
-UserLogin:登录请求
-Token:认证请求
"""
from pydantic import BaseModel,Field,EmailStr,field_validator
from typing import Optional
class UserBase(BaseModel):
    """用户名和邮箱的公共schema"""
    username:str=Field(...,min_length=3,max_length=50,description="用户名,3-50个字符")
    email:EmailStr=Field(...,description="有效的邮箱地址")
class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=6,
        max_length=72,   # bcrypt 最多处理 72 字节
        description="密码（6-72个字符，建议纯英文数字）"
    )

    @field_validator("password")
    @classmethod
    def password_must_contain_digit_and_be_bytesafe(cls, v: str) -> str:
        if not any(char.isdigit() for char in v):
            raise ValueError("密码必须包含至少一个数字")
        # 确保字节长度也不超标（应对中文等多字节字符）
        if len(v.encode('utf-8')) > 72:
            raise ValueError("密码字节长度不能超过 72")
        return v
class UserOut(UserBase):
    """用户响应:包含数据库中的id,is_active,role,但不包含密码"""
    id:int
    is_active:bool
    role:str
    class Config:
        # 允许Pydantic从ORM对象读取属性
        from_attributes=True
class UserLogin(BaseModel):
    """登录请求 body"""
    username:str
    password:str
class Token(BaseModel):
    """返回的JWT token"""
    access_token:str
    token_type:str="bearer"
