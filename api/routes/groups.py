# api/routes/groups.py

from fastapi import APIRouter, HTTPException, Depends, Request
from cassandra.cluster import Session
from typing import List
from api.routes.models import Group, User
from datetime import datetime
import uuid
import logging
from api.routes.dependencies import get_current_user

logger = logging.getLogger(__name__)

def get_group_routes(session: Session):

    router = APIRouter(
        dependencies=[Depends(get_current_user)]
    )

    @router.post("/groups", response_model=Group)
    async def create_group(group: Group, request: Request):
        current_user: User = request.state.user
        group.group_id = uuid.uuid4()
        group.created_at = datetime.utcnow()
        group.created_by = current_user.user_id

        insert_group_cql = """
        INSERT INTO groups (group_id, group_name, description, created_at, created_by)
        VALUES (%s, %s, %s, %s, %s)
        """
        session.execute(insert_group_cql, (
            group.group_id, group.group_name, group.description, group.created_at, group.created_by
        ))
        logger.info(f"Created group with ID: {group.group_id}")
        return group

    @router.get("/groups/{group_id}", response_model=Group)
    async def get_group(group_id: uuid.UUID):
        select_group_cql = "SELECT * FROM groups WHERE group_id = %s"
        group_row = session.execute(select_group_cql, (group_id,)).one()
        if group_row:
            group = Group(
                group_id=group_row.group_id,
                group_name=group_row.group_name,
                description=group_row.description,
                created_at=group_row.created_at,
                created_by=group_row.created_by
            )
            return group
        else:
            logger.warning(f"Group not found: {group_id}")
            raise HTTPException(status_code=404, detail="Group not found")

    return router
