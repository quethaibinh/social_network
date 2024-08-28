import re
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime

class User(BaseModel):
    email: EmailStr
    password: str
    name: str
    sex: str
    age: int




class UserCreate(User):
    
    # mật khẩu phải có trên 8 kí tự
    @validator('password')
    def password_length(cls, value):
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return value
    
    # mật khẩu phải có cả chữ, cả số, cả chữ hoa, cả kí tự đặc biệt
    @validator('password')
    def password_strength(cls, value):
        if not re.search(r'[a-z]', value):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[A-Z]', value):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[0-9]', value):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValueError('Password must contain at least one special character')
        return value
    
    
    
class UserOut(BaseModel):
    id: int
    email: str
    create_at: datetime

    class config:
        orm_mode: True



class Token(BaseModel): # dinh dang tra ra ma va kieu token trong ham tao ma token(login)
    access_token: str
    token_type: str



class TokenData(BaseModel):
    id: str | None



class GroupCreate(BaseModel):
    name: str



class GroupSearch(BaseModel):
    name: str
    # bổ sung thêm số lượng thành viên

    class config:
        orm_mode: True



class GroupUpdate(BaseModel):
    id: int
    name: str

    class config:
        orm_mode: True



class Post(BaseModel):
    group_id: int
    content: str
    public: bool    



class PostCreate(Post):
    pass    



class PostUpdate(Post):
    id: int

    class config:
        orm_mode: True



class PostOut(BaseModel):
    name_user: str
    content: str
    create_at: datetime