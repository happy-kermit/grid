# middleware/auth.py

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from jose import JWTError, jwt
from api.routes.utils import SECRET_KEY, ALGORITHM
from cassandra.cluster import Session
from api.routes.models import User
import uuid
import logging

class AuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, session: Session):
        super().__init__(app)
        self.session = session

    async def dispatch(self, request: Request, call_next):
        authorization: str = request.headers.get("Authorization")

        if authorization:
            scheme, _, param = authorization.partition(" ")
            if scheme.lower() == "bearer":
                token = param
                try:
                    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                    user_id_str: str = payload.get("sub")
                    if user_id_str is None:
                        request.state.user = None
                    else:
                        user_id = uuid.UUID(user_id_str)
                        # Fetch user from database
                        select_user_cql = "SELECT * FROM users WHERE user_id = %s"
                        user_row = self.session.execute(select_user_cql, (user_id,)).one()
                        if user_row:
                            user = User(
                                user_id=user_row.user_id,
                                username=user_row.username,
                                email=user_row.email,
                                bio=user_row.bio,
                                profile_pic=user_row.profile_pic
                            )
                            request.state.user = user
                        else:
                            request.state.user = None
                except JWTError:
                    request.state.user = None
            else:
                request.state.user = None
        else:
            request.state.user = None

        response = await call_next(request)
        return response
