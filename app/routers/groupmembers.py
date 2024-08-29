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
    
    user = db.query(models.GroupMember).filter(models.GroupMember.user_id == current_user.id
                                               and models.GroupMember.group_id == join.group_id
                                               and models.GroupMember.status == True).first()
    if user:
        raise HTTPException(status_code= status.HTTP_202_ACCEPTED,
                            detail= f'you have joined the group')
    new_member = models.GroupMember(user_id = current_user.id, group_id = join.group_id, role_id = 2)
    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return new_member



# API khi admin nhấn nút chấp nhận user vào group (có thông báo đến admin khi người dùng joinrequest)
@router.put("/accept", response_model= schemas.NotificationAcceptToUser)
async def accept_request(accept_user: schemas.AcceptRequest, db: session = Depends(database.get_db),
                         current_user: int = Depends(oauth2.get_current_user)):
    
    # check = db.query(models.GroupMember).filter()

    accept = models.GroupMember(user_id = current_user.id, role_id = 2, status = True, **accept_user.dict())
    update_member = db.query(models.GroupMember).filter(models.GroupMember.id == accept_user.id)
    if not update_member.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= f'request is not found!')
    update_member.update(accept.dict(), synchronize_session = False)
    db.commit()
    return update_member.first() # gửi thông báo được chấp thuận về tài khoản user gửi yêu cầu