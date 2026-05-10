"""
FastAPI 应用主入口
- 创建应用,配置CORS,中间件,异常处理
- 挂载静态文件
- 注册路由(目前为空壳)
- 启动时自动创建数据库表
"""
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.routers import items, auth, user, upload, websocket, bg_tasks
from app.middleware import add_process_time_header   # 稍后我们创建这个文件
from app.exceptions import global_exception_handler # 稍后我们创建这个文件

# 创建FastAPI实例
# CORS配置

# 启动/关闭事件
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期的启动和关闭逻辑。
    yield 之前是启动时执行，yield 之后是关闭时执行。
    """
    # --- 启动逻辑 ---
    print("正在启动服务，创建数据库表...")
    # 关键步骤：根据所有继承自 Base 的模型，在数据库中创建表。
    # 如果表已存在，则不会重复创建。
    Base.metadata.create_all(bind = engine)
    print("数据库表已检查/创建完毕。")

    yield  # 应用运行期间

    # --- 关闭逻辑 ---
    print("应用正在关闭，可以在这里清理资源...")


app=FastAPI(
    title=settings.APP_NAME,
    description="覆盖FastAPI主要与高级特性的学习项目.包含路由,验证,依赖租入,数据库,认证,websocket",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 注册自定义中间件
app.middleware("http")(add_process_time_header)
# 注册全局异常处理器
app.exception_handler(Exception)(global_exception_handler)
# 挂载静态文件目录
# 访问/static/xxx会映射到app/static目录下的文件
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
# 注册路由
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(items.router)
app.include_router(upload.router)
app.include_router(websocket.router)
app.include_router(bg_tasks.router)
# 根路由
@app.get("/",tags=["根"])
def read_root():
    return {"message":f"欢迎来到{settings.APP_NAME}! 请访问/docs查看API文档"}
