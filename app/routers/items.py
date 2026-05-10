"""
物品CRUD路由(路由基础完整演示)
- what:实现资源的创建,读取,更新,删除
- why:演示restful api 设计中各种参数类型,方法,状态码的用法
- how:使用pydantic 模型解析请求,SQLAIchemy操作数据库,依赖注入管理认证和查询参数
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, common_query_params, get_pagination_from_class, get_current_active_user
from app.schemas.item import ItemCreate, ItemUpdate, ItemOut, ItemList
from app.models.user import Item, User
router=APIRouter(prefix="/items",tags=["物品"])
# 列表查询(GET)
@router.get("/", response_model=ItemList)
def list_items(
        common:dict=Depends(common_query_params), # 查询参数依赖
        db:Session=Depends(get_db)
):
    """
    获取物品列表(支持搜索和分页)
    - 查询参数q:模糊搜索标题和描述
    - skip/limit:分页控制
    - 返回ItemList(包含物品列表和总数)
    """
    query=db.query(Item)
    if common["q"]:
        search=f"%{common['q']}%"
        query=query.filter(Item.title.ilike(search)|Item.description.ilike(search))
    total=query.count()
    items=query.offset(common["skip"]).limit(common["limit"]).all()
    return {"items": items, "total": total}
# 创建物品(POST)
@router.post("/", response_model=ItemOut,status_code=status.HTTP_201_CREATED)
def create_item(
        item_in:ItemCreate,  #请求体,自动验证
        db:Session=Depends(get_db),
        current_user:User=Depends(get_current_active_user) # 需要登录
):
    """
    创建物品(需要认证)
    - 请求体经过ItemCreate schema校验
    - 物品所有者自动设置为当前登录用户
    - 返回201Created
    """
    item=Item(**item_in.dict(),owner_id=current_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
# 嵌套类依赖演示(GET)
@router.get("/class-dep", response_model=ItemList)
def list_items_with_class_dep(
        commons:dict=Depends(get_pagination_from_class),
        db:Session=Depends(get_db)
):
    """与list_items功能相同,但使用类依赖+嵌套依赖获取参数"""
    query=db.query(Item)
    total=query.count()
    items=query.offset(commons["skip"]).limit(commons["limit"]).all()
    return {"items": items, "total": total}
# 获取单个物品
@router.get("/{item_id}", response_model=ItemOut)
def get_item(item_id:int, db:Session=Depends(get_db)):
    """
    根据路径参数item_id获取单个物品
    - 路径参数自动转换为int类型
    - 物品不存在时返回404
    """
    item=db.query(Item).get(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="物品不存在"
        )
    return item
@router.put("/{item_id}", response_model=ItemOut)
def update_item(
        item_id:int,
        item_in:ItemUpdate,  # 请求体,所有字段可选
        db:Session=Depends(get_db),
        current_user:User=Depends(get_current_active_user)
):
    """
    更新物品(部分更新,需认证为所有者)
    - 使用item_in.dict(exclude_unset=True)只更新新传入的字段
    - 验证所有权,非所有者返回403
    """
    item=db.query(Item).get(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="物品不存在"
        )
    if item.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能修改自己的物品"
        )
    update_data=item_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item
# 删除物品
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id:int, db:Session=Depends(get_db),current_user:User=Depends(get_current_active_user)):
    """
    删除物品(需认证为所有者)
    - 成功删除返回204 No Content,无响应体
    """
    item=db.query(Item).get(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="物品不存在"
        )
    if item.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能删除自己的物品"
        )
    db.delete(item)
    db.commit()
    return  # 204 不需要返回任何内容