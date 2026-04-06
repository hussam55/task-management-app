from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional

from app import models, schemas, crud
from app.db import get_db
from app.auth import get_current_user, verify_password, create_access_token

router = APIRouter(
    tags=["projects"]
)

@router.post("/workspaces/{workspace_id}/projects", response_model=schemas.ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    workspace_id: int,
    project: schemas.ProjectCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new project in a workspace (members can create)"""
    crud.require_workspace_member(db, current_user, workspace_id)
    return crud.create_project(db, workspace_id, project)


@router.get("/workspaces/{workspace_id}/projects", response_model=list[schemas.ProjectResponse])
def list_projects(
    workspace_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all projects in a workspace (members only)"""
    crud.require_workspace_member(db, current_user, workspace_id)
    return crud.get_workspace_projects(db, workspace_id)


@router.patch("/projects/{project_id}", response_model=schemas.ProjectResponse)
def update_project(
    project_id: int,
    project_update: schemas.ProjectUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a project (members can update)"""
    workspace_id = crud.get_project_workspace_id(db, project_id)
    crud.require_workspace_member(db, current_user, workspace_id)
    return crud.update_project(db, project_id, project_update)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a project (owner only)"""
    workspace_id = crud.get_project_workspace_id(db, project_id)
    crud.require_workspace_owner(db, current_user, workspace_id)
    crud.delete_project(db, project_id)
    return None