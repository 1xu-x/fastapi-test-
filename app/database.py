# app/database.py
"""
数据库集成模块（SQLAlchemy 同步版本）
- What: 创建引擎、会话工厂、声明基类，提供 get_db 依赖（yield）
- Why: ORM 抽象化数据库操作，依赖注入管理会话生命周期
- How: 使用 SQLite（可替换为 PostgreSQL），get_db 作为生成器依赖
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# 创建引擎：SQLite 需要额外参数 check_same_thread=False 才能多线程访问
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG,  # 调试模式会打印 SQL 语句
)

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类：所有 ORM 模型都要继承它
Base = declarative_base()

def get_db():
    """
    数据库会话依赖（带 yield）
    ---
    每个请求会调用此函数，生成一个 DB 会话，请求结束后自动关闭。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()