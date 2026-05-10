from fastapi import APIRouter, Depends
from app.schemas.user import UserOut
from app.models.user import User
from app.dependencies import get_current_active_user,role_required

router = APIRouter(prefix="/users", tags=["用户"])   # 注意 tags 里是 "用户"

@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_active_user)):
    return current_user
@router.get("/admin-only")
def admin_only(current_user: User = Depends(role_required("admin"))):
    return {"message": f"你好，管理员 {current_user.username}！此端点仅管理员可见。"}