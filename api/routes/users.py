# api/routes/users.py

from fastapi import APIRouter, HTTPException, Depends
from cassandra.cluster import Session
from typing import List
from api.routes.dependencies import get_current_user
from api.routes.models import User, UserCreate, UserInDB
from api.routes.utils import get_password_hash
import uuid
import logging

logger = logging.getLogger(__name__)


def get_user_routes(session: Session):

    router = APIRouter()

    @router.post("/users", response_model=User)
    async def create_user(user: UserCreate):
        # Check if username already exists
        select_user_cql = "SELECT * FROM users_by_username WHERE username = %s"
        existing_user = session.execute(select_user_cql, (user.username,)).one()
        if existing_user:
            logger.warning(f"Username already taken: {user.username}")
            raise HTTPException(status_code=400, detail="Username already taken")

        user_id = uuid.uuid4()
        hashed_password = get_password_hash(user.password)

        # Insert into users_by_username table
        insert_user_by_username_cql = """
        INSERT INTO users_by_username (username, bio, email, password, profile_pic, user_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        session.execute(insert_user_by_username_cql, (
            user.username, user.bio, user.email, hashed_password, user.profile_pic, user_id
        ))

        # Insert into users table
        insert_user_cql = """
        INSERT INTO users (user_id, username, email, password, bio, profile_pic)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        session.execute(insert_user_cql, (
            user_id, user.username, user.email, hashed_password, user.bio, user.profile_pic
        ))

        logger.info(f"Created user with ID: {user_id}")

        return User(
            user_id=user_id,
            username=user.username,
            email=user.email,
            bio=user.bio,
            profile_pic=user.profile_pic
        )

    @router.get("/users/{user_id}", response_model=User, dependencies=[Depends(get_current_user)])
    async def get_user(user_id: uuid.UUID):
        select_user_cql = "SELECT * FROM users WHERE user_id = %s"
        user_row = session.execute(select_user_cql, (user_id,)).one()
        if user_row:
            user = User(
                user_id=user_row.user_id,
                username=user_row.username,
                # email=user_row.email,
                bio=user_row.bio,
                profile_pic=user_row.profile_pic
            )
            return user
        else:
            logger.warning(f"User not found: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")

    return router
