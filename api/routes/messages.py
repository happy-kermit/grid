# api/routes/messages.py

from fastapi import APIRouter, HTTPException, Depends, Request
from cassandra.cluster import Session
from typing import List
from api.routes.models import Message, User
from api.routes.dependencies import get_current_user
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def get_message_routes(session: Session):

    router = APIRouter(
        dependencies=[Depends(get_current_user)]
    )

    @router.post("/messages", response_model=Message)
    async def send_message(message: Message, request: Request):
        current_user: User = request.state.user
        message.message_id = uuid.uuid4()
        message.created_at = datetime.utcnow()
        message.sender_id = current_user.user_id

        # Ensure user1_id and user2_id are always in the same order
        user1_id, user2_id = sorted([message.sender_id, message.receiver_id])
        insert_message_cql = """
        INSERT INTO messages (user1_id, user2_id, created_at, message_id, sender_id, content)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        session.execute(insert_message_cql, (
            user1_id, user2_id, message.created_at, message.message_id, message.sender_id, message.content
        ))
        logger.info(f"Message sent from {message.sender_id} to {message.receiver_id}")
        return message

    @router.get("/messages/{user1_id}/{user2_id}", response_model=List[Message])
    async def get_messages(user1_id: uuid.UUID, user2_id: uuid.UUID):
        # Ensure user1_id and user2_id are always in the same order
        user1_id, user2_id = sorted([user1_id, user2_id])
        select_messages_cql = """
        SELECT * FROM messages WHERE user1_id = %s AND user2_id = %s ORDER BY created_at ASC
        """
        messages_rows = session.execute(select_messages_cql, (user1_id, user2_id))
        messages = []
        for row in messages_rows:
            message = Message(
                message_id=row.message_id,
                sender_id=row.sender_id,
                receiver_id=user2_id if row.sender_id == user1_id else user1_id,
                content=row.content,
                created_at=row.created_at
            )
            messages.append(message)
        logger.info(f"Retrieved {len(messages)} messages between {user1_id} and {user2_id}")
        return messages

    return router
