from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional

from app import models, schemas, crud
from app.db import get_db
from app.auth import get_current_user, verify_password, create_access_token

router = APIRouter(
    tags=["tasks"]
)




@router.post("/projects/{project_id}/tasks", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    project_id: int,
    task: schemas.TaskCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new task in a project (members can create)"""
    workspace_id = crud.get_project_workspace_id(db, project_id)
    crud.require_workspace_member(db, current_user, workspace_id)
    return crud.create_task(db, project_id, task, current_user)


@router.get("/projects/{project_id}/tasks", response_model=schemas.PaginatedTasks)
def list_tasks(
    project_id: int,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List tasks in a project with filtering and pagination (members only)"""
    workspace_id = crud.get_project_workspace_id(db, project_id)
    crud.require_workspace_member(db, current_user, workspace_id)
    
    tasks, total = crud.get_project_tasks(db, project_id, status, priority, page, page_size)
    return schemas.PaginatedTasks(
        items=tasks,
        total=total,
        page=page,
        page_size=page_size
    )


@router.patch("/tasks/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a task (members can update)"""
    workspace_id = crud.get_task_workspace_id(db, task_id)
    crud.require_workspace_member(db, current_user, workspace_id)
    return crud.update_task(db, task_id, task_update)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a task (owner OR task creator can delete)"""
    workspace_id = crud.get_task_workspace_id(db, task_id)
    membership = crud.require_workspace_member(db, current_user, workspace_id)
    
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    # Allow deletion if user is workspace owner OR task creator
    if membership.role != "owner" and task.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only workspace owner or task creator can delete this task"
        )
    
    crud.delete_task(db, task_id)
    return None