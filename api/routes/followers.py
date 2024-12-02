# api/routes/followers.py

from fastapi import APIRouter, HTTPException, Depends, Request
from cassandra.cluster import Session
from typing import List
from api.routes.models import User
from api.routes.dependencies import get_current_user
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def get_follower_routes(session: Session):

    router = APIRouter(
        dependencies=[Depends(get_current_user)]
    )

    @router.post("/users/{user_id}/follow")
    async def follow_user(user_id: uuid.UUID, request: Request):
        current_user: User = request.state.user
        follower_id = current_user.user_id
        followed_at = datetime.utcnow()
        insert_follower_cql = """
        INSERT INTO user_followers (user_id, follower_id, followed_at)
        VALUES (%s, %s, %s)
        """
        session.execute(insert_follower_cql, (user_id, follower_id, followed_at))

        insert_following_cql = """
        INSERT INTO user_following (user_id, following_id, followed_at)
        VALUES (%s, %s, %s)
        """
        session.execute(insert_following_cql, (follower_id, user_id, followed_at))
        logger.info(f"User ID: {follower_id} followed user ID: {user_id}")
        return {"message": "User followed"}

    @router.get("/users/{user_id}/followers", response_model=List[uuid.UUID])
    async def get_followers(user_id: uuid.UUID):
        select_followers_cql = "SELECT follower_id FROM user_followers WHERE user_id = %s"
        followers_rows = session.execute(select_followers_cql, (user_id,))
        follower_ids = [row.follower_id for row in followers_rows]
        logger.info(f"Retrieved {len(follower_ids)} followers for user ID: {user_id}")
        return follower_ids

    return router
