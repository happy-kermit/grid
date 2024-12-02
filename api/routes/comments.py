# api/routes/comments.py

from fastapi import APIRouter, HTTPException, Depends, Request
from cassandra.cluster import Session
from typing import List
from api.routes.models import Comment, User
from api.routes.dependencies import get_current_user
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def get_comment_routes(session: Session):

    router = APIRouter(
        dependencies=[Depends(get_current_user)]
    )

    @router.post("/posts/{post_id}/comments", response_model=Comment)
    async def add_comment(post_id: uuid.UUID, comment: Comment, request: Request):
        current_user: User = request.state.user
        comment.comment_id = uuid.uuid4()
        comment.created_at = datetime.utcnow()
        comment.user_id = current_user.user_id

        insert_comment_cql = """
        INSERT INTO post_comments (post_id, created_at, comment_id, user_id, content)
        VALUES (%s, %s, %s, %s, %s)
        """
        session.execute(insert_comment_cql, (
            post_id, comment.created_at, comment.comment_id, comment.user_id, comment.content
        ))
        logger.info(f"Added comment ID: {comment.comment_id} to post ID: {post_id}")
        return comment

    @router.get("/posts/{post_id}/comments", response_model=List[Comment])
    async def get_comments(post_id: uuid.UUID):
        select_comments_cql = """
        SELECT * FROM post_comments WHERE post_id = %s ORDER BY created_at ASC
        """
        comments_rows = session.execute(select_comments_cql, (post_id,))
        comments = []
        for row in comments_rows:
            comment = Comment(
                comment_id=row.comment_id,
                post_id=row.post_id,
                user_id=row.user_id,
                content=row.content,
                created_at=row.created_at
            )
            comments.append(comment)
        logger.info(f"Retrieved {len(comments)} comments for post ID: {post_id}")
        return comments

    return router
