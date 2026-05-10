# app/config.py
"""
配置管理模块（Pydantic Settings）
- What: 使用 pydantic-settings 加载 .env，提供类型安全的配置项
- Why: 环境变量与代码分离，支持多环境部署，自动类型校验
- How: 继承 BaseSettings，字段名与环境变量自动匹配
"""
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "FastAPI 学习项目"
    DEBUG: bool = False
    DATABASE_URL: str = "sqlite:///./app.db"
    SECRET_KEY: str = "change-me-in-production"       # JWT 签名密钥
    ALGORITHM: str = "HS256"                          # 签名算法
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30             # 令牌过期时间（分钟）
    ALLOWED_ORIGINS: List[str] = ["*"]                # CORS 允许的源

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# 模块级单例，其他地方直接 import settings 使用
settings = Settings()