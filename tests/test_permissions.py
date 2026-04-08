


def register_and_login(client, email, username, password):
    """Helper to register and login a user"""
    client.post(
        "/auth/register",
        json={"email": email, "username": username, "password": password}
    )
    response = client.post(
        "/auth/login",
        data={"username": username, "password": password}
    )
    return response.json()["access_token"]


def test_non_member_cannot_access_workspace(client):
    """Test that non-members cannot access workspace"""
    # Create two users
    owner_token = register_and_login(client, "owner@example.com", "owner", "pass123")
    non_member_token = register_and_login(client, "nonmember@example.com", "nonmember", "pass123")
    
    # Owner creates workspace
    response = client.post(
        "/workspaces",
        json={"name": "Test Workspace"},
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    workspace_id = response.json()["id"]
    
    # Non-member tries to access workspace
    response = client.get(
        f"/workspaces/{workspace_id}",
        headers={"Authorization": f"Bearer {non_member_token}"}
    )
    assert response.status_code == 403
    assert "not a member" in response.json()["detail"]


def test_non_member_cannot_access_projects(client):
    """Test that non-members cannot access projects"""
    # Create two users
    owner_token = register_and_login(client, "owner@example.com", "owner", "pass123")
    non_member_token = register_and_login(client, "nonmember@example.com", "nonmember", "pass123")
    
    # Owner creates workspace
    workspace_response = client.post(
        "/workspaces",
        json={"name": "Test Workspace"},
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    workspace_id = workspace_response.json()["id"]
    
    # Non-member tries to access projects
    response = client.get(
        f"/workspaces/{workspace_id}/projects",
        headers={"Authorization": f"Bearer {non_member_token}"}
    )
    assert response.status_code == 403


def test_member_can_access_workspace(client):
    """Test that members can access workspace"""
    # Create two users
    owner_token = register_and_login(client, "owner@example.com", "owner", "pass123")
    member_token = register_and_login(client, "member@example.com", "member", "pass123")
    
    # Owner creates workspace
    workspace_response = client.post(
        "/workspaces",
        json={"name": "Test Workspace"},
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    workspace_id = workspace_response.json()["id"]
    
    # Owner adds member
    client.post(
        f"/workspaces/{workspace_id}/members",
        json={"email": "member@example.com"},
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    
    # Member can now access workspace
    response = client.get(
        f"/workspaces/{workspace_id}",
        headers={"Authorization": f"Bearer {member_token}"}
    )
    assert response.status_code == 200


def test_only_owner_can_add_members(client):
    """Test that only workspace owner can add members"""
    # Create three users
    owner_token = register_and_login(client, "owner@example.com", "owner", "pass123")
    member_token = register_and_login(client, "member@example.com", "member", "pass123")
    new_user_token = register_and_login(client, "newuser@example.com", "newuser", "pass123")
    
    # Owner creates workspace
    workspace_response = client.post(
        "/workspaces",
        json={"name": "Test Workspace"},
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    workspace_id = workspace_response.json()["id"]
    
    # Owner adds member
    response = client.post(
        f"/workspaces/{workspace_id}/members",
        json={"email": "member@example.com"},
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    assert response.status_code == 201
    
    # Member tries to add another user (should fail)
    response = client.post(
        f"/workspaces/{workspace_id}/members",
        json={"email": "newuser@example.com"},
        headers={"Authorization": f"Bearer {member_token}"}
    )
    assert response.status_code == 403
    assert "owner" in response.json()["detail"].lower()


def test_only_owner_can_delete_workspace(client):
    """Test that only workspace owner can delete workspace"""
    # Create two users
    owner_token = register_and_login(client, "owner@example.com", "owner", "pass123")
    member_token = register_and_login(client, "member@example.com", "member", "pass123")
    
    # Owner creates workspace
    workspace_response = client.post(
        "/workspaces",
        json={"name": "Test Workspace"},
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    workspace_id = workspace_response.json()["id"]
    
    # Owner adds member
    client.post(
        f"/workspaces/{workspace_id}/members",
        json={"email": "member@example.com"},
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    
    # Member tries to delete workspace (should fail)
    response = client.delete(
        f"/workspaces/{workspace_id}",
        headers={"Authorization": f"Bearer {member_token}"}
    )
    assert response.status_code == 403
    
    # Owner can delete workspace
    response = client.delete(
        f"/workspaces/{workspace_id}",
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    assert response.status_code == 204


def test_only_owner_can_delete_project(client):
    """Test that only workspace owner can delete project"""
    # Create two users
    owner_token = register_and_login(client, "owner@example.com", "owner", "pass123")
    member_token = register_and_login(client, "member@example.com", "member", "pass123")
    
    # Owner creates workspace
    workspace_response = client.post(
        "/workspaces",
        json={"name": "Test Workspace"},
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    workspace_id = workspace_response.json()["id"]
    
    # Owner adds member
    client.post(
        f"/workspaces/{workspace_id}/members",
        json={"email": "member@example.com"},
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    
    # Member creates a project
    project_response = client.post(
        f"/workspaces/{workspace_id}/projects",
        json={"name": "Test Project", "description": "A test project"},
        headers={"Authorization": f"Bearer {member_token}"}
    )
    project_id = project_response.json()["id"]
    
    # Member tries to delete project (should fail)
    response = client.delete(
        f"/projects/{project_id}",
        headers={"Authorization": f"Bearer {member_token}"}
    )
    assert response.status_code == 403
    
    # Owner can delete project
    response = client.delete(
        f"/projects/{project_id}",
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    assert response.status_code == 204


def test_member_can_update_project(client):
    """Test that workspace members can update projects"""
    # Create two users
    owner_token = register_and_login(client, "owner@example.com", "owner", "pass123")
    member_token = register_and_login(client, "member@example.com", "member", "pass123")
    
    # Owner creates workspace
    workspace_response = client.post(
        "/workspaces",
        json={"name": "Test Workspace"},
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    workspace_id = workspace_response.json()["id"]
    
    # Owner adds member
    client.post(
        f"/workspaces/{workspace_id}/members",
        json={"email": "member@example.com"},
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    
    # Owner creates a project
    project_response = client.post(
        f"/workspaces/{workspace_id}/projects",
        json={"name": "Test Project"},
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    project_id = project_response.json()["id"]
    
    # Member can update project
    response = client.patch(
        f"/projects/{project_id}",
        json={"name": "Updated Project Name"},
        headers={"Authorization": f"Bearer {member_token}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Project Name"


def test_task_creator_can_delete_task(client):
    """Test that task creator can delete their own task"""
    # Create two users
    owner_token = register_and_login(client, "owner@example.com", "owner", "pass123")
    member_token = register_and_login(client, "member@example.com", "member", "pass123")
    
    # Owner creates workspace
    workspace_response = client.post(
        "/workspaces",
        json={"name": "Test Workspace"},
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    workspace_id = workspace_response.json()["id"]
    
    # Owner adds member
    client.post(
        f"/workspaces/{workspace_id}/members",
        json={"email": "member@example.com"},
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    
    # Owner creates a project
    project_response = client.post(
        f"/workspaces/{workspace_id}/projects",
        json={"name": "Test Project"},
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    project_id = project_response.json()["id"]
    
    # Member creates a task
    task_response = client.post(
        f"/projects/{project_id}/tasks",
        json={"title": "Member's Task"},
        headers={"Authorization": f"Bearer {member_token}"}
    )
    task_id = task_response.json()["id"]
    
    # Member can delete their own task
    response = client.delete(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {member_token}"}
    )
    assert response.status_code == 204


def test_workspace_owner_can_delete_any_task(client):
    """Test that workspace owner can delete any task"""
    # Create two users
    owner_token = register_and_login(client, "owner@example.com", "owner", "pass123")
    member_token = register_and_login(client, "member@example.com", "member", "pass123")
    
    # Owner creates workspace
    workspace_response = client.post(
        "/workspaces",
        json={"name": "Test Workspace"},
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    workspace_id = workspace_response.json()["id"]
    
    # Owner adds member
    client.post(
        f"/workspaces/{workspace_id}/members",
        json={"email": "member@example.com"},
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    
    # Owner creates a project
    project_response = client.post(
        f"/workspaces/{workspace_id}/projects",
        json={"name": "Test Project"},
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    project_id = project_response.json()["id"]
    
    # Member creates a task
    task_response = client.post(
        f"/projects/{project_id}/tasks",
        json={"title": "Member's Task"},
        headers={"Authorization": f"Bearer {member_token}"}
    )
    task_id = task_response.json()["id"]
    
    # Owner can delete member's task
    response = client.delete(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    assert response.status_code == 204
