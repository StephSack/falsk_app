def test_multiple_projects_listed(client):
    # Add two projects
    resp1 = client.post(
        "/add_project",
        data={"title": "Proj One", "description": "First"},
        follow_redirects=True,
    )
    assert resp1.status_code == 200

    resp2 = client.post(
        "/add_project",
        data={"title": "Proj Two", "description": "Second"},
        follow_redirects=True,
    )
    assert resp2.status_code == 200

    # Get projects page and verify both titles are present
    resp = client.get("/projects")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "Proj One" in html
    assert "Proj Two" in html
