# 这个文件集中管理所有可注入的依赖,我们需要同时由查询参数(用于物品列表)和认证依赖(用于保护接口)
"""
依赖注入演示模块(包含查询参数依赖与认证依赖)
what:fastapi的depends机制,复用逻辑,管理资源
why:减少重复代码,分离关注点,便于测试
how:定义可调用对象(函数/类),通过depends()注入路由函数
"""
"""
认证依赖:
1.oauth2_scheme:从请求头中提取Bearer Token
2.get_current_user:解析JWT并查询数据库得到用户对象
3.get_current_active_user:检查用户是否激活
4.role_required:依赖工厂,限制特定角色访问
"""
from fastapi import Query, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.auth_utils import decode_access_token
from app.models.user import User

# 查询参数依赖
def common_query_params(
        q:Optional[str]=Query(None,description="搜索关键词"),
        skip:int=Query(0,ge=0,description="跳过的记录数"),
        limit:int=Query(100,ge=1,le=100,description="返回记录数上限")
)->dict:
    """简单函数依赖:提取公共查询参数,返回字典"""
    return {"q":q,"skip":skip,"limit":limit}
class CommonQueryParamsClass:
    """类依赖:将参数封装未类属性"""
    def __init__(
            self,
            q:Optional[str]=Query(None),
            skip:int=Query(0,ge=0),
            limit:int=Query(100,ge=1,le=100),):
        self.q = q
        self.skip = skip
        self.limit = limit
def get_pagination_from_class(commons:CommonQueryParamsClass=Depends(CommonQueryParamsClass))->dict:
    """嵌套依赖:使用类依赖的输出"""
    return {"q":commons.q,"skip":commons.skip,"limit":commons.limit}

# 认证依赖
# tokenUrl指向登录端点,Swagger UI 会据此先是锁形图标和登录表单
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
def get_current_user(token:str=Depends(oauth2_scheme),db:Session=Depends(get_db))->User:
    """
    从JWT令牌中获取当前用户
    - 解码Bearer Token,提取sub字段(用户名)
    - 查询数据库返回User对象
    - 令牌无效或用户不存在时抛出401
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据,请重新登录",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        username:str=payload.get("sub")
        if username is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    user = db.query(User).filter(User.username==username).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(
        current_user: User = Depends(get_current_user)
)->User:
    """检查当前用户时候激活,未激活则返回400"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用",
        )
    return current_user

def role_required(required_role:str):
    """
    角色权限依赖工厂
    - 返回一个依赖哈桑农户,检查用户角色是否符合
    - 用法:Depends(role_required("admin") 
    """
    def role_checker(current_user: User = Depends(get_current_active_user))->User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要{required_role}权限"
            )
        return current_user
    return role_checker