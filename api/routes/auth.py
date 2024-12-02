# api/routes/auth.py

from fastapi import APIRouter, Depends, HTTPException, status, Form
from datetime import timedelta
from cassandra.cluster import Session
from jose import JWTError, jwt
from api.routes.models import User, UserInDB, UserCreate
from api.routes.utils import (
    verify_password,
    get_password_hash,
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
import uuid
import logging

logger = logging.getLogger(__name__)

def get_auth_routes(session: Session):

    router = APIRouter()

    @router.post("/login")
    async def login(username: str = Form(...), password: str = Form(...)):
        # Fetch user from the database
        select_user_cql = "SELECT * FROM users_by_username WHERE username = %s"
        user_row = session.execute(select_user_cql, (username,)).one()
        if not user_row:
            logger.warning(f"Authentication failed for user: {username}")
            raise HTTPException(status_code=400, detail="Incorrect username or password")

        user_in_db = UserInDB(
            user_id=user_row.user_id,
            username=user_row.username,
            email=user_row.email,
            bio=user_row.bio,
            profile_pic=user_row.profile_pic,
            hashed_password=user_row.password,  # Stored hashed password
        )

        if not verify_password(password, user_in_db.hashed_password):
            logger.warning(f"Authentication failed for user: {username}")
            raise HTTPException(status_code=400, detail="Incorrect username or password")

        # Create JWT token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user_in_db.user_id)},
            expires_delta=access_token_expires
        )

        logger.info(f"User logged in: {username}")
        return {"access_token": access_token, "token_type": "bearer"}

    return router
