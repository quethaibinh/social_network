from fastapi import FastAPI, APIRouter, Depends, status, HTTPException, responses, Response
from sqlalchemy.orm import session
from .. import schemas, models, database, oauth2

router = APIRouter(
    prefix= '/grmember',
    tags= ['grmember']
)



# API khi người dùng muốn tham gia vào group => gửi yêu cầu
# gửi thông báo đến manf hình của group, những tài khoản nào của group có role là admin sẽ nhìn thấy
@router.post("/request", response_model= schemas.NotificationRequestToAdmin)
async def join_request(join: schemas.JoinRequest, db: session = Depends(database.get_db),
                       current_user: int = Depends(oauth2.get_current_user)):
    
    # check xem yêu cầu đã tồn tại chưa
    user = db.query(models.GroupMember).filter(models.GroupMember.user_id == current_user.id,
                                               models.GroupMember.group_id == join.group_id).first()
    if user:
        raise HTTPException(status_code= status.HTTP_202_ACCEPTED,
                            detail= f'you have joined the group or you need admin accept')
    # check xem group có tồn tại hay không
    admin = db.query(models.Group).filter(models.Group.id == join.group_id).first() # => admin_id này mặc định là admin chính(người tạo ra group)
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
    
    # check xem người dùng hiện tại có phải admin hay không
    check = db.query(models.GroupMember).filter(models.GroupMember.user_id == current_user.id,
                                          models.Group.id == accept_user.group_id,
                                          models.GroupMember.role_id == 1).first()
    if not check: 
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,
                            detail= f'you are not admin')
    # check xem cái yêu cầu join nhóm của user còn hiệu lực không (xem admin khác đã duyệt chưa)
    update_member = db.query(models.GroupMember).filter(models.GroupMember.group_id == accept_user.group_id,
                                                        models.GroupMember.user_id == accept_user.user_id,
                                                        models.GroupMember.status == False).first()
    if not update_member:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= f'request id not found or you have already agreed to this request')

    update_member.status = True
    db.commit()
    return update_member # gửi thông báo được chấp thuận về tài khoản user gửi yêu cầu



# API khi admin gửi lời mời tham gia group đến 1 user nào đó (chỉ có admin mới được quyền mời)
@router.post("/invite", response_model= schemas.NotificationRequestToAdmin)
async def send_invitation(invite: schemas.Invite, db: session = Depends(database.get_db),
                          current_user: int = Depends(oauth2.get_current_user)):
    
    # check xem group có tồn tại hay không
    admin = db.query(models.Group).filter(models.Group.id == invite.group_id).first()
    if not admin:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= f'group with id = {invite.group_id} was not found')
    # check xem user hiện tại có phải admin hay không
    check = db.query(models.GroupMember).filter(models.GroupMember.group_id == invite.group_id,
                                          models.GroupMember.user_id == current_user.id,
                                          models.GroupMember.role_id == 1).first()
    if not check:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= f'you are not admin')
    # check xem user được mời có tồn tại hay không
    user = db.query(models.User).filter(models.User.id == invite.user_id).first()
    if not user:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= f'user was not exist')
    # check xem đã tồn tại lời mời hay chưa
    invi = db.query(models.GroupMember).filter(models.GroupMember.group_id == invite.group_id,
                                                models.GroupMember.user_id == invite.user_id)
    if invi.first():
        raise HTTPException(status_code= status.HTTP_303_SEE_OTHER,
                            detail= f'You sent an invitation or the user is already in the group')
    new_member = models.GroupMember(user_id = invite.user_id, group_id = invite.group_id, role_id = 2, admin_id = admin.admin_id, reason = 1)
    # => admin_id trong bảng groupmembers mặc định là admin tạo ra group(admin chính)
    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return new_member



# API khi người dùng được mời và ấn chấp nhận tham gia group (thông báo đến tài khoản user)
@router.put("/agree", response_model= schemas.NotificationAcceptToUser)
async def agree_join(agree: schemas.Agree, db: session = Depends(database.get_db),
                     current_user: int = Depends(oauth2.get_current_user)):
    
    # check xem lời mời còn hiệu lực hay không
    check = db.query(models.GroupMember).filter(models.GroupMember.group_id == agree.group_id,
                                                models.GroupMember.user_id == current_user.id,
                                                models.GroupMember.status == False).first()
    if not check:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= f'You are already in the group or the table is not invited to the group')
    check.status = True
    db.commit()
    return check



# API khi 1 admin đề xuất 1 user khác trong nhóm làm admin {nhập vào id của user muốn làm admin}
@router.put("/upgrade_role")
async def upgrade_role(role: schemas.ChangeRole, db: session = Depends(database.get_db),
                       current_user: int = Depends(oauth2.get_current_user)):
    
    # check xem user đó đã trong group hay chưa
    user = db.query(models.GroupMember).filter(models.GroupMember.user_id == role.user_id,
                                                models.GroupMember.group_id == role.group_id,
                                                models.GroupMember.status == True).first()
    if not user:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= f'user with id = {role.user_id} was not exist in this group')
    # check xem user đó đã là admin hay chưa
    if user.role_id == 1:
        raise HTTPException(status_code= status.HTTP_302_FOUND,
                            detail= f'this user have been admin')
    # check xem nguời dùng hiện tại có là admin chính không(người tạo ra group) => chỉ có admin chính mới có quyền duyệt user khác làm admin
    admin = db.query(models.Group).filter(models.Group.id == role.group_id,
                                          models.Group.admin_id == current_user.id).first()
    if not admin:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,
                            detail= f'you are not main_admin, only the main_admin has the right to change roles.')
    user.role_id = 1
    db.commit()
    return user



# API khi admin chính muốn phế bỏ quyền admin của 1 admin phụ nào đó
@router.put("/downgrade")
async def downgrade_role(role: schemas.ChangeRole, db: session = Depends(database.get_db),
                         current_user: int = Depends(oauth2.get_current_user)):
    
    # chexk xem user đó có trong group hay chưa
    user = db.query(models.GroupMember).filter(models.GroupMember.user_id == role.user_id,
                                               models.GroupMember.group_id == role.group_id,
                                               models.GroupMember.status == True).first()
    if not user:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= f'this user was not exist in group')
    # check xem user đó có phải admin hay không
    if user.role_id != 1:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= f'this user is not admin')
    # check xem user hiện tại(người đăng nhập) có quyền phế bỏ admin hay không(có là admin chính hay không)
    admin = db.query(models.Group).filter(models.Group.id == role.group_id,
                                          models.Group.admin_id == current_user.id).first()
    if not admin:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,
                            detail= f'you are not main_admin, only the main_admin has the right to change roles.')
    user.role_id = 2
    db.commit()
    return user


# bổ sung relationship trong get những bài post(hiển thị hết thông tin của bài post đó, thông tin của người đăng, thông tin comment, like, ...)
# cập nhật lại get group, hiển thị ra số lượng người trong group