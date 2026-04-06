from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional

from app import models, schemas
from app.auth import get_password_hash


# === User Operations ===

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get user by email"""
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Get user by username"""
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user"""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()
    

def delete_user_by_id(db: Session, user_id: int) -> None:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()

# === Permission Helpers ===

def get_membership(db: Session, user_id: int, workspace_id: int) -> Optional[models.Membership]:
    """Get membership for a user in a workspace"""
    return db.query(models.Membership).filter(
        models.Membership.user_id == user_id,
        models.Membership.workspace_id == workspace_id
    ).first()


def require_workspace_member(db: Session, user: models.User, workspace_id: int) -> models.Membership:
    """Require that user is a member of the workspace"""
    membership = get_membership(db, user.id, workspace_id)
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace"
        )
    return membership


def require_workspace_owner(db: Session, user: models.User, workspace_id: int) -> models.Membership:
    """Require that user is the owner of the workspace"""
    membership = require_workspace_member(db, user, workspace_id)
    if membership.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only workspace owner can perform this action"
        )
    return membership


def get_project_workspace_id(db: Session, project_id: int) -> int:
    """Get workspace_id for a project"""
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project.workspace_id


def get_task_workspace_id(db: Session, task_id: int) -> int:
    """Get workspace_id for a task"""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return get_project_workspace_id(db, task.project_id)


# === Workspace Operations ===

def create_workspace(db: Session, workspace: schemas.WorkspaceCreate, owner: models.User) -> models.Workspace:
    """Create a new workspace and add owner as member"""
    db_workspace = models.Workspace(name=workspace.name, owner_id=owner.id)
    db.add(db_workspace)
    db.flush()  # Get the workspace ID

    # Create owner membership
    db_membership = models.Membership(
        workspace_id=db_workspace.id,
        user_id=owner.id,
        role="owner"
    )
    db.add(db_membership)
    db.commit()
    db.refresh(db_workspace)
    return db_workspace


def get_user_workspaces(db: Session, user: models.User) -> list[models.Workspace]:
    """Get all workspaces where user is a member"""
    memberships = db.query(models.Membership).filter(
        models.Membership.user_id == user.id
    ).all()
    workspace_ids = [m.workspace_id for m in memberships]
    return db.query(models.Workspace).filter(models.Workspace.id.in_(workspace_ids)).all()


def get_workspace(db: Session, workspace_id: int) -> Optional[models.Workspace]:
    """Get workspace by ID"""
    return db.query(models.Workspace).filter(models.Workspace.id == workspace_id).first()


def add_workspace_member(db: Session, workspace_id: int, email: str) -> models.Membership:
    """Add a member to a workspace by email"""
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Check if already a member
    existing = get_membership(db, user.id, workspace_id)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already a member")
    
    db_membership = models.Membership(
        workspace_id=workspace_id,
        user_id=user.id,
        role="member"
    )
    db.add(db_membership)
    db.commit()
    db.refresh(db_membership)
    return db_membership


def get_workspace_members(db: Session, workspace_id: int) -> list[dict]:
    """List workspace members with basic user info and role"""
    memberships = db.query(models.Membership).filter(
        models.Membership.workspace_id == workspace_id
    ).all()

    members: list[dict] = []
    for membership in memberships:
        user = db.query(models.User).filter(models.User.id == membership.user_id).first()
        if user:
            members.append(
                {
                    "user_id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "role": membership.role,
                }
            )
    return members


def delete_workspace(db: Session, workspace_id: int):
    """Delete a workspace (cascade will delete projects, tasks, memberships)"""
    workspace = get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    db.delete(workspace)
    db.commit()


# === Project Operations ===

def create_project(db: Session, workspace_id: int, project: schemas.ProjectCreate) -> models.Project:
    """Create a new project in a workspace"""
    db_project = models.Project(
        workspace_id=workspace_id,
        name=project.name,
        description=project.description
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def get_workspace_projects(db: Session, workspace_id: int) -> list[models.Project]:
    """Get all projects in a workspace"""
    return db.query(models.Project).filter(models.Project.workspace_id == workspace_id).all()


def get_project(db: Session, project_id: int) -> Optional[models.Project]:
    """Get project by ID"""
    return db.query(models.Project).filter(models.Project.id == project_id).first()


def update_project(db: Session, project_id: int, project_update: schemas.ProjectUpdate) -> models.Project:
    """Update a project"""
    db_project = get_project(db, project_id)
    if not db_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project


def delete_project(db: Session, project_id: int):
    """Delete a project"""
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    db.delete(project)
    db.commit()


# === Task Operations ===

def create_task(db: Session, project_id: int, task: schemas.TaskCreate, creator: models.User) -> models.Task:
    """Create a new task in a project"""
    if task.assigned_to is not None and not get_user_by_id(db, task.assigned_to):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User you are assigning to not found")
    
    db_task = models.Task(
        project_id=project_id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        created_by=creator.id,
        assigned_to=task.assigned_to
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_project_tasks(
    db: Session,
    project_id: int,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    page: int = 1,
    page_size: int = 50
) -> tuple[list[models.Task], int]:
    """Get tasks in a project with filtering and pagination"""
    query = db.query(models.Task).filter(models.Task.project_id == project_id)
    
    if status:
        query = query.filter(models.Task.status == status)
    if priority:
        query = query.filter(models.Task.priority == priority)
    
    total = query.count()
    tasks = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return tasks, total


def get_task(db: Session, task_id: int) -> Optional[models.Task]:
    """Get task by ID"""
    return db.query(models.Task).filter(models.Task.id == task_id).first()


def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate) -> models.Task:
    """Update a task"""
    db_task = get_task(db, task_id)
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int):
    """Delete a task"""
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    db.delete(task)
    db.commit()
