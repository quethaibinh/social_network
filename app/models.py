from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from .database import Base



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    name = Column(String, nullable= False)
    sex = Column(String, nullable= False)
    age = Column(Integer, nullable= False)
    create_at = Column(TIMESTAMP(timezone= True), nullable=False, server_default= text("NOW()"))



# tài khoản admin trong bảng group này là tài khoản user tạo ra group đó, tương đương với admin chính
class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key= True, nullable= False)
    name = Column(String, nullable= False)
    admin_id = Column(Integer, ForeignKey("users.id", ondelete= "CASCADE"), nullable= False)
    created_at = Column(TIMESTAMP(timezone= True), nullable= False, server_default= text("NOW()"))



class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key= True, nullable= False)
    role_name = Column(String, nullable= False)
    # role = 1 => admin
    # role = 2 => user



# admin_id trong bảng groupmembers này là khi 1 admin cấp quyền cho 1 user nào đo lên làm admin, gọi là admin phụ, tài khoản admin chính cũng ở trong đây.
class GroupMember(Base):
    __tablename__ = "groupmembers"

    id = Column(Integer, primary_key= True, nullable= False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete= "CASCADE"), nullable= False)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete= "CASCADE"), nullable= False)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete= "CASCADE"), nullable= False)
    status = Column(Boolean, nullable= False, server_default= "False")
    admin_id = Column(Integer, nullable= False)
    reason = Column(Integer, nullable= False, server_default= "0") # là lí do ở trong nhóm 0 là tạo ra group, 1 là được mời vào, 2 là yêu cầu được vào
    join_time = Column(TIMESTAMP(timezone= True), nullable= False, server_default= text("NOW()"))



class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key= True, nullable= False)
    admin_id = Column(Integer, nullable= False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete= "CASCADE"), nullable= False)
    name_user = Column(String, nullable= False)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete= "CASCADE"), nullable= False)
    status = Column(Boolean, nullable= False, server_default= "False")
    content = Column(String, nullable= False)
    public = Column(Boolean, nullable= False)
    create_at = Column(TIMESTAMP(timezone= True), nullable= False, server_default= text("NOW()"))