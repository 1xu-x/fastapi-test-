"""
物品相关pydantic Schema
- ItemBase:公共字段
- ItemCreate:创建请求
- ItemUpdate:更新请求(所有字段可选,支持部分更新)
- ItemOut:响应
- ItemList:列表响应,包含嵌套的ItemOut列表和总数
"""
from pydantic import BaseModel,Field
from typing import Optional,List

class ItemBase(BaseModel):
    title:str=Field(...,description="物品标题")
    description:Optional[str]=Field(None,max_length=300,description="物品描述,最多300字符")
class ItemCreate(ItemBase):
    """创建物品,无需额外字段"""
    pass
class ItemUpdate(BaseModel):
    """更新物品,所有字段可选,传入什么就更新什么"""
    title:Optional[str]=Field(None,min_length=1)
    description:Optional[str]=Field(None,max_length=300)
class ItemOut(ItemBase):
    id:int
    owner_id:int
    class Config:
        from_attributes=True
class ItemList(BaseModel):
    """返回物品列表和总数,演示嵌套模型"""
    items:List[ItemOut]
    total:int
