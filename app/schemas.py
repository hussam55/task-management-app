from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime, date
from typing import Optional


# User schemas
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


# Workspace schemas
class WorkspaceCreate(BaseModel):
    name: str


class WorkspaceResponse(BaseModel):
    id: int
    name: str
    owner_id: int

    model_config = ConfigDict(from_attributes=True)


class MemberAdd(BaseModel):
    email: EmailStr


class MembershipResponse(BaseModel):
    id: int
    workspace_id: int
    user_id: int
    role: str

    model_config = ConfigDict(from_attributes=True)


class WorkspaceMemberResponse(BaseModel):
    user_id: int
    email: str
    username: str
    role: str


# Project schemas
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    workspace_id: int
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Task schemas
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "todo"
    priority: Optional[str] = "medium"
    due_date: Optional[date] = None
    assigned_to: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None
    assigned_to: Optional[int] = None


class TaskResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    due_date: Optional[date] = None
    created_by: int
    assigned_to: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Pagination
class PaginatedTasks(BaseModel):
    items: list[TaskResponse]
    total: int
    page: int
    page_size: int
