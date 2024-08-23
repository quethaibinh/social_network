from fastapi import FastAPI, APIRouter, Depends, status, HTTPException, responses
from sqlalchemy.orm import session
from .. import schemas, models, database, oauth2



router = APIRouter(
    prefix="/groups",
    tags=['groups']
)

@router.post("/", status_code= status.HTTP_201_CREATED)
async def create_group(group: schemas.GroupCreate, db: session = Depends(database.get_db),
                        current_user: int = Depends(oauth2.get_current_user)):
    
    new_group = models.Group(**group.dict())
    db.add(new_group)
    db.commit()
    db.refresh(new_group)

    new_groupmember = models.GroupMember(user_id = current_user.id, group_id = new_group.id,
                                         role_id = 1, status = True)
    db.add(new_groupmember)
    db.commit()
    db.refresh(new_groupmember)

    return {"message": "create successfull!"}



@router.get("/search", response_model= list[schemas.GroupSearch])
async def group_search(db: session = Depends(database.get_db),
                       current_user: int = Depends(oauth2.get_current_user),
                       search: str = ""):
    
    user = current_user
    groups = db.query(models.Group).filter(models.Group.name.contains(search)).all()
    if not groups:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"not found with {search}")
    return groups

