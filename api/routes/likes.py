# api/routes/likes.py

from fastapi import APIRouter, HTTPException, Depends, Request
from cassandra.cluster import Session
from typing import List
from api.routes.models import User
from api.routes.dependencies import get_current_user
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def get_like_routes(session: Session):

    router = APIRouter(
        dependencies=[Depends(get_current_user)]
    )

    @router.post("/posts/{post_id}/like")
    async def like_post(post_id: uuid.UUID, request: Request):
        current_user: User = request.state.user
        user_id = current_user.user_id
        liked_at = datetime.utcnow()
        insert_post_like_cql = """
        INSERT INTO post_likes (post_id, user_id, liked_at)
        VALUES (%s, %s, %s)
        """
        session.execute(insert_post_like_cql, (post_id, user_id, liked_at))

        insert_user_like_cql = """
        INSERT INTO user_likes (user_id, liked_at, post_id)
        VALUES (%s, %s, %s)
        """
        session.execute(insert_user_like_cql, (user_id, liked_at, post_id))
        logger.info(f"User ID: {user_id} liked post ID: {post_id}")
        return {"message": "Post liked"}

    @router.get("/posts/{post_id}/likes", response_model=List[uuid.UUID])
    async def get_post_likes(post_id: uuid.UUID):
        select_likes_cql = "SELECT user_id FROM post_likes WHERE post_id = %s"
        likes_rows = session.execute(select_likes_cql, (post_id,))
        user_ids = [row.user_id for row in likes_rows]
        logger.info(f"Retrieved {len(user_ids)} likes for post ID: {post_id}")
        return user_ids

    return router
