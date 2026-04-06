from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional

from app import models, schemas, crud
from app.db import get_db
from app.auth import get_current_user, verify_password, create_access_token

router = APIRouter(
    prefix="/workspaces",
    tags=["workspaces"]
)




@router.post("", response_model=schemas.WorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_workspace(
    workspace: schemas.WorkspaceCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new workspace (creator becomes owner)"""
    return crud.create_workspace(db, workspace, current_user)


@router.get("", response_model=list[schemas.WorkspaceResponse])
def list_workspaces(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all workspaces where current user is a member"""
    return crud.get_user_workspaces(db, current_user)


@router.get("/{workspace_id}", response_model=schemas.WorkspaceResponse)
def get_workspace(
    workspace_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get workspace details (members only)"""
    crud.require_workspace_member(db, current_user, workspace_id)
    workspace = crud.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    return workspace

@router.get("/{workspace_id}/members", response_model=list[schemas.WorkspaceMemberResponse])
def list_workspace_members(
    workspace_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List workspace members (workspace members only)"""
    crud.require_workspace_member(db, current_user, workspace_id)
    return crud.get_workspace_members(db, workspace_id)



@router.post("/{workspace_id}/members", response_model=schemas.MembershipResponse, status_code=status.HTTP_201_CREATED)
def add_member(
    workspace_id: int,
    member: schemas.MemberAdd,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a member to workspace (owner only)"""
    crud.require_workspace_owner(db, current_user, workspace_id)
    return crud.add_workspace_member(db, workspace_id, member.email)


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workspace(
    workspace_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a workspace (owner only)"""
    crud.require_workspace_owner(db, current_user, workspace_id)
    crud.delete_workspace(db, workspace_id)
    return None