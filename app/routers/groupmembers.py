from fastapi import FastAPI, APIRouter, Depends, status, HTTPException, responses, Response
from sqlalchemy.orm import session
from .. import schemas, models, database, oauth2

router = APIRouter(
    prefix= '/grmember',
    tags= ['grmember']
)



# API khi người dùng muốn tham gia vào group => gửi yêu cầu
# gửi thông báo đến tài khoản của admin
@router.post("/request", response_model= schemas.NotificationRequestToAdmin)
async def join_request(join: schemas.JoinRequest, db: session = Depends(database.get_db),
                       current_user: int = Depends(oauth2.get_current_user)):
    
    user = db.query(models.GroupMember).filter(models.GroupMember.user_id == current_user.id,
                                               models.GroupMember.group_id == join.group_id).first()
    # print(user)
    if user:
        raise HTTPException(status_code= status.HTTP_202_ACCEPTED,
                            detail= f'you have joined the group or you need admin accept')
    admin = db.query(models.Group).filter(models.Group.id == join.group_id).first()
    if not admin:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= f'group with id = {join.group_id} was not exist')
    new_member = models.GroupMember(user_id = current_user.id, group_id = join.group_id, role_id = 2, admin_id = admin.admin_id, reason = 2)
    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return new_member



# API khi admin nhấn nút chấp nhận user vào group (có thông báo đến admin khi người dùng joinrequest)
@router.put("/accept", response_model= schemas.NotificationAcceptToUser)
async def accept_request(accept_user: schemas.AcceptRequest, db: session = Depends(database.get_db),
                         current_user: int = Depends(oauth2.get_current_user)):
    
    # check xem cái yêu cầu join nhóm của user còn hiệu lực không
    check = db.query(models.Group).filter(models.Group.admin_id == current_user.id,
                                          models.Group.id == accept_user.group_id).first()
    if not check: 
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,
                            detail= f'you are not admin')
    update_member = db.query(models.GroupMember).filter(models.GroupMember.group_id == accept_user.group_id,
                                                        models.GroupMember.user_id == accept_user.user_id,
                                                        models.GroupMember.status == False).first()
    if not update_member:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= f'request id not found or you have already agreed to this request')

    update_member.status = True
    db.commit()
    return update_member # gửi thông báo được chấp thuận về tài khoản user gửi yêu cầu



# API khi admin gửi lời mời tham gia group đến 1 user nào đó
@router.post("/invite", response_model= schemas.NotificationRequestToAdmin)
async def send_invitation(invite: schemas.invite, db: session = Depends(database.get_db),
                          current_user: int = Depends(oauth2.get_current_user)):
    
    check = db.query(models.Group).filter(models.Group.id == invite.group_id,
                                          models.Group.admin_id == current_user.id).first()
    if not check:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= f'you are not admin')

    invi = db.query(models.GroupMember).filter(models.GroupMember.group_id == invite.group_id,
                                                models.GroupMember.user_id == invite.user_id)
    if invi.first():
        raise HTTPException(status_code= status.HTTP_303_SEE_OTHER,
                            detail= f'You sent an invitation or the user is already in the group')
    # admin này là admin mời vào (có thể là admin phụ, có thể là admin chính)
    new_member = models.GroupMember(user_id = invite.user_id, group_id = invite.group_id, role_id = 2, admin_id = current_user.id, reason = 1)
    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return new_member



# API khi người dùng được mời và ấn chấp nhận tham gia group (thông báo đến tài khoản user)
@router.put("/agree", response_model= schemas.NotificationAcceptToUser)
async def agree_join(agree: schemas.agree, db: session = Depends(database.get_db),
                     current_user: int = Depends(oauth2.get_current_user)):
    
    check = db.query(models.GroupMember).filter(models.GroupMember.group_id == agree.group_id,
                                                models.GroupMember.user_id == current_user.id,
                                                models.GroupMember.status == False).first()
    if not check:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= f'You are already in the group or the table is not invited to the group')
    check.status = True
    db.commit()
    return check
    


# làm sao mà khi mình gửi lời mời hoặc yêu cầu tham gia nhóm thì nó sẽ ngay lập tức gửi thông báo về tài khoản admin