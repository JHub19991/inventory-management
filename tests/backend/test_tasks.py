"""
Tests for task API endpoints (GET/POST/PATCH/DELETE /api/tasks).
"""
import pytest


class TestTasksEndpoints:
    """Test suite for task-related endpoints."""

    def test_get_tasks_returns_list(self, client):
        """The tasks endpoint always returns a list."""
        response = client.get("/api/tasks")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_task(self, client):
        """Posting a task creates it with a generated id and pending status."""
        response = client.post("/api/tasks", json={
            "title": "Review Q4 inventory levels",
            "priority": "high",
            "dueDate": "2025-12-01",
        })
        assert response.status_code == 201

        task = response.json()
        for field in ["id", "title", "priority", "dueDate", "status"]:
            assert field in task
        assert task["title"] == "Review Q4 inventory levels"
        assert task["priority"] == "high"
        assert task["dueDate"] == "2025-12-01"
        assert task["status"] == "pending"

    def test_create_task_defaults_priority(self, client):
        """Priority defaults to medium when omitted."""
        response = client.post("/api/tasks", json={
            "title": "Task without priority",
            "dueDate": "2025-11-15",
        })
        assert response.status_code == 201
        assert response.json()["priority"] == "medium"

    def test_created_task_appears_in_list_newest_first(self, client):
        """A newly created task is returned at the front of the list."""
        created = client.post("/api/tasks", json={
            "title": "Newest task",
            "dueDate": "2025-11-20",
        }).json()

        listing = client.get("/api/tasks").json()
        assert listing[0]["id"] == created["id"]

    def test_toggle_task(self, client):
        """Patching a task flips it between pending and completed."""
        created = client.post("/api/tasks", json={
            "title": "Toggle me",
            "dueDate": "2025-11-25",
        }).json()

        toggled = client.patch(f"/api/tasks/{created['id']}")
        assert toggled.status_code == 200
        assert toggled.json()["status"] == "completed"

        toggled_back = client.patch(f"/api/tasks/{created['id']}")
        assert toggled_back.status_code == 200
        assert toggled_back.json()["status"] == "pending"

    def test_delete_task(self, client):
        """Deleting a task removes it from the list."""
        created = client.post("/api/tasks", json={
            "title": "Delete me",
            "dueDate": "2025-11-30",
        }).json()

        response = client.delete(f"/api/tasks/{created['id']}")
        assert response.status_code == 200

        listing = client.get("/api/tasks").json()
        assert all(t["id"] != created["id"] for t in listing)

    def test_toggle_nonexistent_task(self, client):
        """Toggling a task that does not exist returns 404."""
        response = client.patch("/api/tasks/task-does-not-exist")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_nonexistent_task(self, client):
        """Deleting a task that does not exist returns 404."""
        response = client.delete("/api/tasks/task-does-not-exist")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_create_task_blank_title_rejected(self, client):
        """A whitespace-only title is a client error."""
        response = client.post("/api/tasks", json={
            "title": "   ",
            "dueDate": "2025-12-05",
        })
        assert response.status_code == 400
        assert "detail" in response.json()

    def test_create_task_missing_title_is_validation_error(self, client):
        """Omitting the title field is a 422 validation error."""
        response = client.post("/api/tasks", json={"dueDate": "2025-12-05"})
        assert response.status_code == 422
