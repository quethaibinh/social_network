from fastapi import APIRouter, Depends, HTTPException, status, responses
from .. import schemas, models, database, utils
from sqlalchemy.orm import session


router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
async def create_user(user: schemas.UserCreate, db: session = Depends(database.get_db)):

    user.password = utils.hashed(user.password)

    new_user = models.User(**user.dict())

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/{id}", response_model=schemas.UserOut)
async def get_user(id: int, db: session = Depends(database.get_db)):
    
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail= f"not found user with id = {id}")
    
    return user

# # chỉ có người dùng mới được sửa thông tin cá nhân của chính họ => dùng get_current_user để xác minh (JWT)
# @router.put("/update", response_model= schemas.UserOut)
# async def update_user(db: session = Depends(database.get_db)):