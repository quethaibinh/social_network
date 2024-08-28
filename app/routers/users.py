from fastapi import APIRouter, Depends, HTTPException, status, responses
from .. import schemas, models, database, utils, oauth2
from sqlalchemy.orm import session


router = APIRouter(
    prefix="/users",
    tags=["users"]
)



# API khi người dùng đăng kí
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
async def create_user(user: schemas.UserCreate, db: session = Depends(database.get_db)):

    user.password = utils.hashed(user.password)

    new_user = models.User(**user.dict())

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # return {"message": "sign up successfull!"}
    return new_user



# API khi người dùng muốn tìm kiếm một người dùng khác
@router.get("/{id}", response_model=schemas.UserOut)
async def get_user(id: int, db: session = Depends(database.get_db)):
    
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail= f"not found user with id = {id}")
    
    return user



# API khi người dùng muốn chỉnh sửa thông tin cá nhân của họ
# chỉ có người dùng mới được sửa thông tin cá nhân của chính họ => dùng get_current_user để xác minh (JWT)
@router.put("/update", response_model= schemas.UserOut)
async def update_user(user: schemas.UserCreate, db: session = Depends(database.get_db),
                      current_user: int = Depends(oauth2.get_current_user)):
    us_update = db.query(models.User).filter(models.User.id == current_user.id)
    if not us_update.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= f'user with id = {current_user.id} was not exist')

    user.password = utils.hashed(user.password)
    us_update.update(user.dict(), synchronize_session = False)
    db.commit()
    return us_update.first()