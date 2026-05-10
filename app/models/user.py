"""
what:映射数据库表的python表
why:ORM让你用面向对象的方式操作数据库,不写SQL
how:继承Base,用Column定义字段.User和Item之间通过外键和relationship建立一对多关系
"""
"""
ORM模型:User和Item
-User:包含认证所需的用户名,哈希密码,角色
-Item:与User一对多关联,演示外键和relationship
"""
from sqlalchemy import Column,Integer,String,Boolean,ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
class User(Base):
    __tablename__="user"
    id=Column(Integer,primary_key=True,index=True)
    username=Column(String(20),unique=True,index=True,nullable=False)
    email=Column(String(100),unique=True,index=True,nullable=False)
    hashed_password=Column(String(128),nullable=False) # 存储bcrypt哈希后的密码
    is_active=Column(Boolean,default=True) # 是否激活
    role=Column(String(10),default='user')  # 角色:user,admin
# item会由Item中的backref自动添加,这里不需要手动定义
class Item(Base):
    __tablename__="item"
    id=Column(Integer,primary_key=True,index=True)
    title=Column(String(200),index=True,nullable=False)
    description=Column(String(200),nullable=True)
    owner_id=Column(Integer,ForeignKey('user.id'))
    # relationship:通过owner可以访问所属User,同时User会多一个items属性(backer)
    owner=relationship("User",backref="item")
    