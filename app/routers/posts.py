from fastapi import FastAPI, APIRouter, Depends, status, HTTPException, responses, Response
from sqlalchemy.orm import session
from .. import schemas, models, database, oauth2


router = APIRouter(
    prefix= '/posts',
    tags=['posts']
)



# API khi người dùng muốn tạo post
@router.post("/", status_code= status.HTTP_201_CREATED)
async def create_post(post: schemas.PostCreate,
                      db: session = Depends(database.get_db),
                      current_user: int = Depends(oauth2.get_current_user)):
    
    name = db.query(models.User).filter(models.User.id == current_user.id).first()
    if post.group_id == 0: # đăng lên trang cá nhân
        new_post = models.Post(user_id = current_user.id, name_user = name.name, admin_id = current_user.id, **post.dict())
    else:
        # group_id là khi người dùng bấm vào 1 group thì sẽ có 1 biến để lưu id của group đó và nhập vào cho người dùng
        admin = db.query(models.Group).filter(models.Group.id == post.group_id).first()
        if not admin:
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                                detail= f'group is not found!')
        new_post = models.Post(user_id = current_user.id, name_user = name.name, admin_id = admin.admin_id, **post.dict())

    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"message": "Post has been placed on the admin approval queue."}



# API khi người dùng bấm vào group, hiện những bài post trong group đó ra
@router.get("/select/{id}", response_model= list[schemas.PostOut])
async def select_posts_of_group(id: int, db: session = Depends(database.get_db),
                                current_user: int = Depends(oauth2.get_current_user)):
    
    role = db.query(models.GroupMember).filter(current_user.id == models.GroupMember.user_id
                                               and models.GroupMember.status == True).first()
    if not role:
        raise HTTPException(status_code= status.HTTP_405_METHOD_NOT_ALLOWED,
                            detail= f'you are not in this group!')
    
    posts = db.query(models.Post).filter(models.Post.group_id == id).all()
    return posts



# API khi nguoi dung muon sua bai viet
@router.put("/update", response_model= schemas.PostOut)
async def update_post(post_update: schemas.PostUpdate, db: session = Depends(database.get_db),
                      current_user: int = Depends(oauth2.get_current_user)):
    
    role = db.query(models.Post).filter(models.Post.user_id == current_user.id).first()
    if not role:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,
                            detail= f'you are not owner of this post!')

    post = db.query(models.Post).filter(models.Post.id == post_update.id)
    if not post.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= f'this post is not found!')
    post.update(post_update.dict(), synchronize_session = False)
    db.commit()
    return post.first()



# API khi nguoi dung muon xoa bai viet
@router.delete("/delete/{id}", status_code= status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db: session = Depends(database.get_db),
                      current_user: int = Depends(oauth2.get_current_user)):
    
    role = db.query(models.Post).filter(models.Post.user_id == current_user.id).first()
    if not role:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,
                            detail= f'you are not owner of this post')
    
    post = db.query(models.Post).filter(models.Post.id == id)
    if not post.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= f'post with id = {id} was not found!')
    post.delete(synchronize_session = False)
    db.commit()
    return Response(status_code = status.HTTP_204_NO_CONTENT)