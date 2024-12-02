# api/routes/dependencies.py

from fastapi import Request, HTTPException, status, Depends
from api.routes.models import User
from cassandra.cluster import Session

async def get_current_user(request: Request) -> User:
    user = request.state.user
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_session() -> Session:
    # Placeholder function; overridden in main.py
    pass
