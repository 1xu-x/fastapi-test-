"""
认证路由:用户注册与登录
- 注册:校验唯一性->哈希密码->入库->返回用户信息(不含密码)
- 登录:验证凭证->签发JWT->返回令牌

"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.user import UserCreate, UserOut, Token
from app.models.user import User
from app.auth_utils import verify_password, get_password_hash, create_access_token
router = APIRouter(prefix="/auth", tags=["认证"])

@router.post("/register",response_model=UserOut,status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册
    - 检查用户名,邮箱是否存在(409冲突)
    - 密码自动通过UserCreate schema 的validator校验(至少一个数字)
    - 返回创建的用户信息,状态码 201
    """
    # 唯一性检查
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,  # ✅ 正确
            detail = "用户名已存在"
        )
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已注册"
        )
    # 在 user = User(...) 之前
    print(f"📨 即将哈希的密码: {user_in.password}, 长度: {len(user_in.password)}")
    # 创建用户(密码已通过schema已验证,这里进行哈希)
    user=User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user) # 刷新以获得数据库生成的id
    return user
@router.post("/login", response_model=None)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    登录(OAuth2 密码流)
    - 使用OAuth2PasswordRequestForm获取form数据(username+password)
    - 验证用户存在且密码正确
    - 生成JWT令牌,sub字段存用户名
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password,user.hashed_password):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,  # ✅ 正确
            detail = "用户名或密码错误",
            headers = {"WWW-Authenticate":"Bearer"},
        )
    # 创建令牌
    access_token=create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
