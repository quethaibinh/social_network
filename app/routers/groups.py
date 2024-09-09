from fastapi import FastAPI, APIRouter, Depends, status, HTTPException, responses, Response
from sqlalchemy.orm import session
from .. import schemas, models, database, oauth2
from sqlalchemy import func



router = APIRouter(
    prefix="/groups",
    tags=['groups']
)


group_id = 0


# API khi người dùng muốn tạo groups
@router.post("/", status_code= status.HTTP_201_CREATED)
async def create_group(group: schemas.GroupCreate, db: session = Depends(database.get_db),
                        current_user: int = Depends(oauth2.get_current_user)):
    
    new_group = models.Group(name = group.name, admin_id = current_user.id)
    db.add(new_group)
    db.commit()
    db.refresh(new_group)

    new_groupmember = models.GroupMember(user_id = current_user.id, group_id = new_group.id,
                                         role_id = 1, admin_id = current_user.id, status = True)
    db.add(new_groupmember)
    db.commit()
    db.refresh(new_groupmember)

    return {"message": "create successful!"}



# API của ô tìm kiếm groups
@router.get("/search", response_model= list[schemas.GroupSearch])
async def group_search(db: session = Depends(database.get_db),
                       current_user: int = Depends(oauth2.get_current_user),
                       sch: str = ""):
    
    user = current_user
    groups = db.query(models.Group).filter(models.Group.name.contains(sch)).all()
    if not groups:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"not found with {sch}")
    return groups



# API khi người dùng muốn update groups
@router.put("/update", response_model= schemas.GroupSearch)
async def group_update(group: schemas.GroupUpdate, db: session = Depends(database.get_db),
                       current_user: int = Depends(oauth2.get_current_user)):
    
    role = db.query(models.GroupMember).filter(current_user.id == models.GroupMember.user_id,
                                               group.id == models.GroupMember.group_id,
                                               models.GroupMember.role_id == 1).first()
    if not role:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= f'you are not admin!')

    gr_update = db.query(models.Group).filter(models.Group.id == group.id)
    if not gr_update.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail= f'not found group with {group.id}')
    gr_update.update(group.dict(), synchronize_session = False)
    db.commit()
    return gr_update.first()



# API khi người dùng muốn xóa groups
@router.delete("/delete/{id}", status_code = status.HTTP_204_NO_CONTENT)
async def group_delete(id: int, db: session = Depends(database.get_db),
                       current_user: int = Depends(oauth2.get_current_user)):
    
    role = db.query(models.GroupMember).filter(models.GroupMember.user_id == current_user.id,
                                               models.GroupMember.group_id == id,
                                               models.GroupMember.role_id == 1).first()
    if not role:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= f'you are not admin!')
    
    gr_delete = db.query(models.Group).filter(models.Group.id == id)
    if not gr_delete.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= f'not found group with id = {id}')
    gr_delete.delete(synchronize_session = False)
    db.commit()
    return Response(status_code = status.HTTP_204_NO_CONTENT)