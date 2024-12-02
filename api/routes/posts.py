# api/routes/posts.py

from fastapi import APIRouter, HTTPException, Depends, Request
from cassandra.cluster import Session
from typing import List
from api.routes.models import Post, User
from api.routes.dependencies import get_current_user
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def get_post_routes(session: Session):

    router = APIRouter(
        dependencies=[Depends(get_current_user)]
    )

    @router.post("/posts", response_model=Post)
    async def create_post(post: Post, request: Request):
        current_user: User = request.state.user
        post.post_id = uuid.uuid4()
        post.created_at = datetime.utcnow()
        post.user_id = current_user.user_id

        # Insert into posts_by_group
        insert_post_by_group_cql = """
        INSERT INTO posts_by_group (group_id, created_at, post_id, user_id, content)
        VALUES (%s, %s, %s, %s, %s)
        """
        session.execute(insert_post_by_group_cql, (
            post.group_id, post.created_at, post.post_id, post.user_id, post.content
        ))
        # Insert into posts_by_user
        insert_post_by_user_cql = """
        INSERT INTO posts_by_user (user_id, created_at, post_id, group_id, content)
        VALUES (%s, %s, %s, %s, %s)
        """
        session.execute(insert_post_by_user_cql, (
            post.user_id, post.created_at, post.post_id, post.group_id, post.content
        ))
        logger.info(f"Created post with ID: {post.post_id}")
        return post

    @router.get("/groups/{group_id}/posts", response_model=List[Post])
    async def get_posts_by_group(group_id: uuid.UUID):
        select_posts_cql = """
        SELECT * FROM posts_by_group WHERE group_id = %s ORDER BY created_at DESC LIMIT 50
        """
        posts_rows = session.execute(select_posts_cql, (group_id,))
        posts = []
        for row in posts_rows:
            post = Post(
                post_id=row.post_id,
                user_id=row.user_id,
                group_id=row.group_id,
                content=row.content,
                created_at=row.created_at
            )
            posts.append(post)
        logger.info(f"Retrieved {len(posts)} posts for group ID: {group_id}")
        return posts

    @router.get("/users/{user_id}/posts", response_model=List[Post])
    async def get_posts_by_user(user_id: uuid.UUID):
        select_posts_cql = """
        SELECT * FROM posts_by_user WHERE user_id = %s ORDER BY created_at DESC LIMIT 50
        """
        posts_rows = session.execute(select_posts_cql, (user_id,))
        posts = []
        for row in posts_rows:
            post = Post(
                post_id=row.post_id,
                user_id=row.user_id,
                group_id=row.group_id,
                content=row.content,
                created_at=row.created_at
            )
            posts.append(post)
        logger.info(f"Retrieved {len(posts)} posts for user ID: {user_id}")
        return posts

    return router
