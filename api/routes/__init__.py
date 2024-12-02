# api/routes/__init__.py

from fastapi import APIRouter
from cassandra.cluster import Session

from .users import get_user_routes
from .groups import get_group_routes
from .posts import get_post_routes
from .comments import get_comment_routes
from .likes import get_like_routes
from .followers import get_follower_routes
from .messages import get_message_routes

def get_all_routes(session: Session):
    router = APIRouter()
    router.include_router(get_user_routes(session), tags=["users"])
    router.include_router(get_group_routes(session), tags=["groups"])
    router.include_router(get_post_routes(session), tags=["posts"])
    router.include_router(get_comment_routes(session), tags=["comments"])
    router.include_router(get_like_routes(session), tags=["likes"])
    router.include_router(get_follower_routes(session), tags=["followers"])
    router.include_router(get_message_routes(session), tags=["messages"])
    return router
