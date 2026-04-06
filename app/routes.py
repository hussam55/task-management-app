'''
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional

from app import models, schemas, crud
from app.db import get_db
from app.auth import get_current_user, verify_password, create_access_token

router = APIRouter()


# === Auth Endpoints ===

@router.post("/auth/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if email exists
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    # Check if username exists
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    return crud.create_user(db, user)


@router.post("/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login with username and password to get access token"""
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(get_current_user)):
    """Get current user info"""
    return current_user
'''


'''
# === Workspace Endpoints ===

@router.post("/workspaces", response_model=schemas.WorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_workspace(
    workspace: schemas.WorkspaceCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new workspace (creator becomes owner)"""
    return crud.create_workspace(db, workspace, current_user)


@router.get("/workspaces", response_model=list[schemas.WorkspaceResponse])
def list_workspaces(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all workspaces where current user is a member"""
    return crud.get_user_workspaces(db, current_user)


@router.get("/workspaces/{workspace_id}", response_model=schemas.WorkspaceResponse)
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


@router.post("/workspaces/{workspace_id}/members", response_model=schemas.MembershipResponse, status_code=status.HTTP_201_CREATED)
def add_member(
    workspace_id: int,
    member: schemas.MemberAdd,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a member to workspace (owner only)"""
    crud.require_workspace_owner(db, current_user, workspace_id)
    return crud.add_workspace_member(db, workspace_id, member.email)


@router.get("/workspaces/{workspace_id}/members", response_model=list[schemas.WorkspaceMemberResponse])
def list_workspace_members(
    workspace_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List workspace members (workspace members only)"""
    crud.require_workspace_member(db, current_user, workspace_id)
    return crud.get_workspace_members(db, workspace_id)


@router.delete("/workspaces/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workspace(
    workspace_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a workspace (owner only)"""
    crud.require_workspace_owner(db, current_user, workspace_id)
    crud.delete_workspace(db, workspace_id)
    return None
'''

# === Project Endpoints ===
'''
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


# === Task Endpoints ===

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
'''