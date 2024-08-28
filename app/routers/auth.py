from fastapi import APIRouter, HTTPException, Response, Depends, status
from sqlalchemy.orm import Session
from .. import database, schemas, models, utils, oauth2
from ..database import engine, get_db
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router = APIRouter(
    tags = ["authentication"]
)



# API khi người dùng đăng nhập, trả về 1 token
@router.post("/login", response_model = schemas.Token) # dung post vi nguoi dung muon dang nhap va tao ra mot ma dang nhap
async def login(user_confirm: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.email == user_confirm.username).first()
    # vi email la duy nhat
    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = "email was incorrect!")
    

    password = utils.verify(user_confirm.password, user.password)
    # check mat khau khi email dung
    if not password:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
                            detail = "password was incorrect")
    
    Token = oauth2.create_access_token(data = {"user_id": user.id})
    return{"access_token": Token, "token_type": "bearer"}
    # return{"message": "successfull"}