from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List
from datetime import datetime, timedelta

from database import get_db
from models import User, Message, UserRole
from schemas import MessageCreate, MessageResponse, UserList
from dependencies import get_current_user

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"]
)

@router.get("/users/online", response_model=List[UserList])
async def get_online_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Devuelve usuarios activos en los últimos 15 minutos"""
    # Actualizar 'ahora' al consultar esto
    current_user.last_login = datetime.utcnow()
    db.commit()
    
    time_threshold = datetime.utcnow() - timedelta(minutes=15)
    
    users = db.query(User).filter(
        User.last_login >= time_threshold,
        User.id != current_user.id, # No mostrarse a uno mismo
        User.is_active == True
    ).all()
    
    return users

@router.post("/send", response_model=MessageResponse)
async def send_message(
    msg_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_msg = Message(
        sender_id=current_user.id,
        receiver_id=msg_data.receiver_id,
        content=msg_data.content
    )
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    
    return MessageResponse(
        id=new_msg.id,
        sender_id=new_msg.sender_id,
        sender_name=current_user.full_name,
        receiver_id=new_msg.receiver_id,
        content=new_msg.content,
        timestamp=new_msg.timestamp
    )

@router.get("/history/{other_user_id}", response_model=List[MessageResponse])
async def get_chat_history(
    other_user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene el historial de chat entre el usuario actual y otro"""
    messages = db.query(Message).filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.receiver_id == other_user_id),
            and_(Message.sender_id == other_user_id, Message.receiver_id == current_user.id)
        )
    ).order_by(Message.timestamp.asc()).all()
    
    result = []
    for m in messages:
        sender = db.query(User).filter(User.id == m.sender_id).first()
        result.append(MessageResponse(
            id=m.id,
            sender_id=m.sender_id,
            sender_name=sender.full_name if sender else "Desconocido",
            receiver_id=m.receiver_id,
            content=m.content,
            timestamp=m.timestamp
        ))
    return result