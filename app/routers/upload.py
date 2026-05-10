# app/routers/upload.py
"""
文件上传与后台任务
- What: UploadFile 接收文件，BackgroundTasks 执行后台任务
- Why: 文件处理是常见需求，后台任务能快速响应客户端
"""
import os
import time
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/upload", tags=["上传与后台任务"])

# 保存上传文件的目录
UPLOAD_DIR = "app/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def write_log_slowly(filename: str, username: str):
    """模拟一个耗时的后台任务（例如写日志）"""
    time.sleep(3)  # 模拟耗时处理
    with open("upload_log.txt", "a", encoding="utf-8") as f:
        f.write(f"用户 {username} 上传了文件: {filename}\n")


@router.post("/file")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="要上传的文件"),
    current_user=Depends(get_current_active_user)
):
    """
    上传文件端点
    - 使用 UploadFile 接收文件
    - 保存到 app/static/uploads 目录
    - 通过 BackgroundTasks 添加一个后台任务记录日志
    """
    contents = await file.read()
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(contents)

    background_tasks.add_task(write_log_slowly, file.filename, current_user.username)

    return {
        "filename": file.filename,
        "size": len(contents),
        "message": "文件上传成功，后台正在处理"
    }