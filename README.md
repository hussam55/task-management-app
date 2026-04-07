# Task Management API

A minimal and clean task management API built with FastAPI, PostgreSQL, SQLAlchemy, and JWT authentication. This is a simplified Trello-like system with workspaces, projects, and tasks.

## Features

- **User Authentication**: JWT-based authentication with bcrypt password hashing
- **Workspaces**: Create and manage workspaces with owner/member roles
- **Projects**: Organize tasks into projects within workspaces
- **Tasks**: Create, update, and track tasks with status, priority, and assignments
- **Authorization**: Fine-grained permission control for workspace operations
- **Database Migrations**: Alembic for database schema management
- **Docker Support**: Containerized deployment with Docker Compose
- **Testing**: Pytest-based test suite

## Tech Stack

- **Python 3.11+**
- **FastAPI** - Modern web framework
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM (sync)
- **Alembic** - Database migrations
- **Pydantic** - Data validation
- **JWT** - Authentication
- **passlib[bcrypt]** - Password hashing
- **Docker & Docker Compose** - Containerization

## Project Structure

```
app/
  main.py           # FastAPI application
  db.py             # Database engine and session
  models.py         # SQLAlchemy models
  schemas.py        # Pydantic schemas
  auth.py           # JWT and password handling
  crud.py           # Database operations
  routes.py         # API endpoints
tests/
  test_auth.py      # Authentication tests
  test_permissions.py # Authorization tests
alembic/
  versions/         # Migration files
  env.py            # Alembic environment
Dockerfile
docker-compose.yml
requirements.txt
README.md
```

## Quick Start with Docker

### Prerequisites

- Docker
- Docker Compose

### Setup and Run

1. **Clone the repository**
   ```bash
   cd c:\Projects\app
   ```

2. **Start the services**
   ```bash
   docker-compose up --build
   ```

   This will:
   - Start PostgreSQL database
   - Build the API container
   - Run Alembic migrations
   - Start the FastAPI server on http://localhost:8000

3. **Access the API**
   - API: http://localhost:8000
   - Interactive API docs: http://localhost:8000/docs
   - Alternative API docs: http://localhost:8000/redoc

4. **Stop the services**
   ```bash
   docker-compose down
   ```

   To remove volumes (database data):
   ```bash
   docker-compose down -v
   ```

## Local Development Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+

### Setup

1. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   
   Copy `.env.example` to `.env` and update:
   ```bash
   DATABASE_URL=postgresql://user:password@localhost:5432/taskdb
   SECRET_KEY=your-secret-key-min-32-chars-change-in-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   ```

4. **Create database**
   ```bash
   # Using psql or your PostgreSQL client
   createdb taskdb
   ```

5. **Run migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the server**
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at http://localhost:8000

## Running Tests

### With Docker

```bash
docker-compose run api pytest
```

### Local

```bash
pytest
```

Or with coverage:
```bash
pytest --cov=app tests/
```

## API Usage Examples

### 1. Register a User

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "securepass123"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=securepass123"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Save the access token for subsequent requests.

### 3. Get Current User

```bash
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Create Workspace

```bash
curl -X POST "http://localhost:8000/workspaces" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Workspace"
  }'
```

### 5. List Workspaces

```bash
curl -X GET "http://localhost:8000/workspaces" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 6. Add Member to Workspace

```bash
curl -X POST "http://localhost:8000/workspaces/1/members" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "member@example.com"
  }'
```

### 7. Create Project

```bash
curl -X POST "http://localhost:8000/workspaces/1/projects" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Project Alpha",
    "description": "First project"
  }'
```

### 8. List Projects

```bash
curl -X GET "http://localhost:8000/workspaces/1/projects" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 9. Create Task

```bash
curl -X POST "http://localhost:8000/projects/1/tasks" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement login feature",
    "description": "Add JWT authentication",
    "status": "todo",
    "priority": "high",
    "due_date": "2026-03-01"
  }'
```

### 10. List Tasks (with filters)

```bash
# All tasks
curl -X GET "http://localhost:8000/projects/1/tasks" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Filter by status
curl -X GET "http://localhost:8000/projects/1/tasks?status=todo" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Filter by priority with pagination
curl -X GET "http://localhost:8000/projects/1/tasks?priority=high&page=1&page_size=20" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 11. Update Task

```bash
curl -X PATCH "http://localhost:8000/tasks/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "assigned_to": 2
  }'
```

### 12. Delete Task

```bash
curl -X DELETE "http://localhost:8000/tasks/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Data Model

### User
- `id`: Integer (Primary Key)
- `email`: String (Unique)
- `username`: String (Unique)
- `hashed_password`: String
- `created_at`: DateTime

### Workspace
- `id`: Integer (Primary Key)
- `name`: String
- `owner_id`: Integer (FK to User)

### Membership
- `id`: Integer (Primary Key)
- `workspace_id`: Integer (FK to Workspace)
- `user_id`: Integer (FK to User)
- `role`: String ("owner" or "member")
- Unique constraint on (workspace_id, user_id)

### Project
- `id`: Integer (Primary Key)
- `workspace_id`: Integer (FK to Workspace)
- `name`: String
- `description`: String (Nullable)

### Task
- `id`: Integer (Primary Key)
- `project_id`: Integer (FK to Project)
- `title`: String
- `description`: String (Nullable)
- `status`: String ("todo", "in_progress", "done")
- `priority`: String ("low", "medium", "high")
- `due_date`: Date (Nullable)
- `created_by`: Integer (FK to User)
- `assigned_to`: Integer (FK to User, Nullable)
- `created_at`: DateTime

## Authorization Rules

- All endpoints (except `/auth/register` and `/auth/login`) require authentication
- Users can only access workspaces where they are members
- Only workspace **owner** can:
  - Add members to workspace
  - Delete workspace
  - Delete projects
- Workspace **members** can:
  - View workspace and projects
  - Create projects
  - Update projects
  - Create tasks
  - Update tasks
- Only workspace **owner** OR task **creator** can delete tasks

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get access token
- `GET /users/me` - Get current user info

### Workspaces
- `POST /workspaces` - Create workspace
- `GET /workspaces` - List user's workspaces
- `GET /workspaces/{id}` - Get workspace details
- `POST /workspaces/{id}/members` - Add member (owner only)
- `DELETE /workspaces/{id}` - Delete workspace (owner only)

### Projects
- `POST /workspaces/{id}/projects` - Create project
- `GET /workspaces/{id}/projects` - List projects
- `PATCH /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project (owner only)

### Tasks
- `POST /projects/{id}/tasks` - Create task
- `GET /projects/{id}/tasks` - List tasks (with filters and pagination)
- `PATCH /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task (owner or creator)

## Database Migrations

### Create a new migration

```bash
alembic revision --autogenerate -m "description"
```

### Apply migrations

```bash
alembic upgrade head
```

### Rollback migration

```bash
alembic downgrade -1
```

### View migration history

```bash
alembic history
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:password@localhost:5432/taskdb` |
| `SECRET_KEY` | JWT secret key (min 32 chars) | - |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `60` |

## Development Notes

- This is a **minimal** implementation focused on core features and correctness
- Uses synchronous SQLAlchemy for simplicity
- JWT tokens contain user ID in the `sub` claim
- Passwords are hashed using bcrypt
- Database cascading deletes are configured (deleting workspace deletes projects and tasks)
- Tests use SQLite in-memory database for speed

## Production Considerations

For production deployment, consider:

1. **Security**
   - Use strong SECRET_KEY (min 32 random characters)
   - Enable HTTPS/TLS
   - Configure CORS properly
   - Add rate limiting
   - Use refresh tokens

2. **Database**
   - Use connection pooling
   - Set up database backups
   - Monitor query performance
   - Add indexes for frequently queried fields

3. **Infrastructure**
   - Use environment-specific configs
   - Add logging and monitoring
   - Set up health checks
   - Use a production WSGI server (Gunicorn)
   - Add caching (Redis)

4. **Code**
   - Add input validation limits
   - Implement soft deletes
   - Add audit logging
   - Implement API versioning

## License

MIT

## Support

For issues and questions, please open an issue in the repository.
