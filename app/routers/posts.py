from fastapi import FastAPI, APIRouter, Depends, status, HTTPException, responses, Response
from sqlalchemy.orm import session
from .. import schemas, models, database, oauth2
from sqlalchemy import or_, and_


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
        new_post = models.Post(user_id = current_user.id, name_user = name.name, admin_id = current_user.id, status = True, **post.dict())
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return {"message": "successful!"}
    else:
        # check xem group có tồn tại hay không
        admin = db.query(models.Group).filter(models.Group.id == post.group_id).first()
        if not admin:
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                                detail= f'group is not found!')
        # check xem user hiện tại có ở trong group hay chưa
        user = db.query(models.GroupMember).filter(models.GroupMember.user_id == current_user.id,
                                                   models.GroupMember.group_id == post.group_id,
                                                   models.GroupMember.status == True).first()
        if not user:
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                                detail= f'you are not in this group')
        # check xem user hiện tại có là admin của group này hay không
        if user.role_id == 1:
            new_post = models.Post(user_id = current_user.id, name_user = name.name, admin_id = admin.admin_id, status = True, **post.dict())
            db.add(new_post)
            db.commit()
            db.refresh(new_post)
            return {"message": "successful!"}
        
        new_post = models.Post(user_id = current_user.id, name_user = name.name, admin_id = admin.admin_id, **post.dict())
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return {"message": "Post has been placed on the admin approval queue."}



# API khi người dùng bấm vào group, hiện những bài post trong group đó ra
@router.get("/select", response_model= list[schemas.PostOut])
async def select_posts_of_group(post: schemas.PostSelectInGroup, db: session = Depends(database.get_db),
                                current_user: int = Depends(oauth2.get_current_user),
                                limit: int = 10, skip: int = 0):
    
    if post.group_id == 0: #trang cá nhân (chỉ có bản thân xem được => mặc đinh là private)
        posts = db.query(models.Post).filter(models.Post.group_id == 0,
                                             models.Post.user_id == current_user.id).limit(limit).offset(skip).all()
        return posts
    # check xem user hiện tại có ở trong nhóm hay không
    role = db.query(models.GroupMember).filter(models.GroupMember.user_id == current_user.id,
                                               models.GroupMember.group_id == post.group_id,
                                               models.GroupMember.status == True).first()
    if not role:
        raise HTTPException(status_code= status.HTTP_405_METHOD_NOT_ALLOWED,
                            detail= f'you are not in this group!')
    posts = db.query(models.Post).filter(models.Post.group_id == post.group_id).limit(limit).offset(skip).all()
    return posts



# API hiển thị tất cả các bài viết mà người dùng đăng nhập hiện tại có thể thấy
# không hiển thị những bài đăng cá nhân của bản thân, muốn hiển thị thì dùng 1 API khác.
@router.get("/all", response_model= list[schemas.PostOut])
async def all_posts(db: session = Depends(database.get_db),
                    current_user: int = Depends(oauth2.get_current_user),
                    limit: int = 10, skip: int = 0, search: str = ""):
    
    # check xem là user hiện tại đang ở trong những group nào
    group_join = db.query(models.GroupMember).filter(models.GroupMember.user_id == current_user.id,
                                                     models.GroupMember.status == True).all()
    if not group_join:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= f'you need to join group')
    listPost = []
    for group in group_join:
        # check xem với mỗi group thì có những bài đăng nào đẫ được duyệt và được public
        posts = db.query(models.Post).filter(models.Post.group_id == group.group_id,
                                             models.Post.status == True,
                                             models.Post.public == True,
                                             models.Post.content.contains(search)).all()
        if not posts:
            continue
        listPost += posts
    # check xem là có thể hiển thị các bài viết lên trang home hay không (có bài viết trong những nhóm mà mình tham gia không)
    if len(listPost) == 0:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= f'There are currently no posts.')
    # chưa thêm tính năng phân trang (chưa sử dụng limit và offset)
    return listPost



# API khi người dùng muốn xem những bài đăng trong trang cá nhân của chính mình
@router.get("/personal", response_model= list[schemas.PostOut])
async def select_personal(db: session = Depends(database.get_db),
                          current_user: int = Depends(oauth2.get_current_user),
                          limit: int = 10, skip: int = 0, search: str = ""):
    
    # check xem người dùng hiện tại có bài đăng nào ở trang cá nhân không
    posts = db.query(models.Post).filter(models.Post.user_id == current_user.id,
                                         models.Post.group_id == 0,
                                         models.Post.content.contains(search)).limit(limit).offset(skip).all()
    if not posts:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= f'not found')
    return posts



# API khi nguoi dung muon sua bai viet
@router.put("/update", response_model= schemas.PostOut)
async def update_post(post_update: schemas.PostUpdate, db: session = Depends(database.get_db),
                      current_user: int = Depends(oauth2.get_current_user)):
    
    # check xem user hiện tại có là chủ của bài đăng hoặc là admin hay không (admin chính hay phụ đều có quyền chỉnh sửa),  trang cá nhân nữa (trong bảng groupmember không có trường nào có group_id = 0 nên phải xét riêng)
    role = db.query(models.Post).join(models.GroupMember, or_(models.GroupMember.group_id == post_update.group_id, post_update.group_id == 0)).filter(
                                                                                    models.Post.id == post_update.id,
                                                                                    or_(models.Post.user_id == current_user.id,
                                                                                            and_(models.GroupMember.user_id == current_user.id,
                                                                                                models.GroupMember.role_id == 1))).first()
    if not role:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,
                            detail= f'you are not owner of this post!')
    # check xem có tồn tại bài viết không (đã được duyệt)
    post = db.query(models.Post).filter(models.Post.id == post_update.id,
                                        models.Post.status == True)
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
    
    # check xem bài post có tồn tại hay không (đã được duyệt chưa hoặc đã bị xóa chưa)
    post = db.query(models.Post).filter(models.Post.id == id,
                                        models.Post.status == True)
    postCheck = post.first()
    if not postCheck:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= f'post with id = {id} was not found!')
   # check xem user hiện tại có là chủ của bài đăng hoặc là admin hay không (admin chính hay phụ đều có quyền chỉnh sửa),  trang cá nhân nữa (trong bảng groupmember không có trường nào có group_id = 0 nên phải xét riêng)
    role = db.query(models.Post).join(models.GroupMember, or_(models.GroupMember.group_id == postCheck.group_id, postCheck.group_id == 0)).filter(
                                                                                    models.Post.id == id,
                                                                                    or_(models.Post.user_id == current_user.id,
                                                                                            and_(models.GroupMember.user_id == current_user.id,
                                                                                                models.GroupMember.role_id == 1))).first()
    if not role:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,
                            detail= f'you are not owner of this post')
    
    post.delete(synchronize_session = False)
    db.commit()
    return Response(status_code = status.HTTP_204_NO_CONTENT)



# API khi admin duyệt bài đăng 
@router.put("/agree")
async def agree_post(id: int, db: session = Depends(database.get_db),
                     current_user: int = Depends(oauth2.get_current_user)):
    
    # check xem bài viết có tồn tại hay không
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= f'this post was not exist')
    # check xem bài viết đã được duyệt hay chưa
    if post.status == True:
        raise HTTPException(status_code= status.HTTP_302_FOUND,
                            detail= f'this post was exist')
    # check xem user hiện tại có là admin của group đó hay không
    admin = db.query(models.GroupMember).filter(models.GroupMember.group_id == post.group_id,
                                                models.GroupMember.user_id == current_user.id,
                                                models.GroupMember.role_id == 1).first()
    if not admin:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,
                            detail= f'you are not admin')
    post.status = True
    db.commit()
    return {"message": "successful"}