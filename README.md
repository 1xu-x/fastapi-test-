# FastAPI 全特性学习项目

这是一个覆盖 FastAPI 核心与高级特性的学习项目，包含路由、验证、认证、数据库、WebSocket、后台任务等。

## 在线体验
部署地址：https://你的服务.onrender.com
API 文档：https://你的服务.onrender.com/docs

## 本地运行
1. 克隆项目
2. 创建虚拟环境并安装依赖：`pip install -r requirements.txt`
3. 复制 `.env.example` 为 `.env`，填入自己的配置
4. 启动：`uvicorn app.main:app --reload`
5. 访问 http://127.0.0.1:8000/docs

## 技术栈
- FastAPI
- SQLAlchemy
- Pydantic
- JWT 认证
- WebSocket
- Render 部署