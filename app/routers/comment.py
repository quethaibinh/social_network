from fastapi import FastAPI, APIRouter, Depends, status, HTTPException, responses, Response
from sqlalchemy.orm import session
from .. import schemas, models, database, oauth2
from sqlalchemy import or_, and_


router = APIRouter(
    prefix= '/comment',
    tags=['comment']
)


# API khi user muốn tạo comment trong bài viết của group
@router.post("/", status_code= status.HTTP_201_CREATED)
async def create_comment(comment: schemas.CreateComment, db: session = Depends(database.get_db),
                         current_user: int = Depends(oauth2.get_current_user)):
    
    # do chưa làm tính năng publish trang cá nhân nên chưa thể comment
    if comment.group_id == 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                    detail="You cannot comment on personal posts.")
    # check xem người dùng hiện tại có đang ở trong group hay không
    user = db.query(models.GroupMember).filter(models.GroupMember.user_id == current_user.id,
                                               models.GroupMember.group_id == comment.group_id,
                                               models.GroupMember.status == True).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"You are not a member of this group.")
    # check bài post có còn tồn tại hay không
    post = db.query(models.Post).filter(models.Post.id == comment.post_id,
                                        models.Post.group_id == comment.group_id,
                                        models.Post.status == True).first()
    if not post:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= f'this post was not exist')
    new_comment = models.Comment(user_id = current_user.id, group_id = comment.group_id, post_id = comment.post_id,
                                content = comment.content, id_comment = comment.id_comment)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return {
        "message": "Comment created successfully",
        "comment": new_comment
    }



# API khi user muốn xem comment của bài viết 
@router.get("/select", response_model= list[schemas.ResponComment])
async def select_commnets(comment: schemas.SeleteComment, db: session = Depends(database.get_db),
                          current_user: int = Depends(oauth2.get_current_user)):
    
    # check bài post có tồn tại hay không
    post = db.query(models.Post).filter(models.Post.id == comment.post_id,
                                        models.Post.status == True).first()
    if not post:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= f'this post was not exist')
    # check xem user hiện tại có ở trong group có bài viết này hay không
    user = db.query(models.GroupMember).filter(models.GroupMember.user_id == current_user.id,
                                               models.GroupMember.group_id == post.group_id,
                                               models.GroupMember.status == True).first()
    if not user:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= f'you are not in this group')
    com = db.query(models.Comment).filter(models.Comment.post_id == comment.post_id,
                                        models.Comment.id_comment == comment.id_comment).all()
    if not com:
        return {"message": "0 comment"}
    return com



# API khi người dùng muốn xoá comment
@router.delete("/delete", status_code= status.HTTP_204_NO_CONTENT)
async def delete_comment(id: int, db: session = Depends(database.get_db),
                         current_user: int = Depends(oauth2.get_current_user)):
    
    # check xem comment muốn xóa còn tồn tại hay không
    comment = db.query(models.Comment).filter(models.Comment.id == id)
    if not comment.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= f'this comment with id = {id} was not exist')
    # check xem user hiện tại có là chủ của comment muốn xóa hay không
    if comment.first().user_id != current_user.id:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,
                            detail= f'you are not owner of this comment')
    comment.delete(synchronize_session = False)
    db.commit()
    return Response(status_code= status.HTTP_204_NO_CONTENT)