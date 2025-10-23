import os


def test_projects_page_empty(client):
    # When DB is empty, projects page should render and contain no project titles
    resp = client.get("/projects")
    assert resp.status_code == 200
    data = resp.get_data(as_text=True)
    # There should be a projects container even if empty
    assert "Projects" in data or "projects" in data


def test_add_project(client):
    # Post a new project (no image) and ensure redirect to /projects
    resp = client.post(
        "/add_project",
        data={"title": "Test Project", "description": "A project added by pytest"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    data = resp.get_data(as_text=True)
    assert "Test Project" in data
    assert "A project added by pytest" in data
