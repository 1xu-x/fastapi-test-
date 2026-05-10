# app/routers/bg_tasks.py
from fastapi import APIRouter, BackgroundTasks

router = APIRouter(prefix="/tasks", tags=["后台任务"])

def write_to_log(message: str):
    import time
    time.sleep(2)  # 模拟耗时操作
    with open("bg_tasks_log.txt", "a", encoding="utf-8") as f:
        f.write(message + "\n")

@router.post("/send-notification")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_to_log, f"向 {email} 发送通知")
    return {"message": f"通知任务已提交，将发送到 {email}"}