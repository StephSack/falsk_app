import io
import os


def test_add_and_delete_project_with_image(client, tmp_path, monkeypatch):
    # Use a temporary images directory so the test doesn't write into the repo
    temp_images = tmp_path / "images"
    temp_images.mkdir()

    # Monkeypatch the app's UPLOAD_FOLDER to the temp dir
    import app as myapp

    # Set module-level var (if present) and the Flask config key for uploads
    monkeypatch.setattr(myapp, "UPLOAD_FOLDER", str(temp_images), raising=False)
    monkeypatch.setitem(myapp.app.config, "UPLOAD_FOLDER", str(temp_images))

    # Create a fake image file
    fake_image = (io.BytesIO(b"fake-image-data"), "photo.png")

    # Post a new project with an image
    resp = client.post(
        "/add_project",
        data={"title": "Photo Project", "description": "Has image", "image_file": fake_image},
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "Photo Project" in html
    assert "Has image" in html

    # Ensure the uploaded file exists in the temporary images folder
    files = list(temp_images.iterdir())
    assert any(f.name.endswith("photo.png") for f in files)

    # Now delete the project; find its id by locating the section for this title
    resp2 = client.get("/projects")
    assert resp2.status_code == 200
    page = resp2.get_data(as_text=True)
    # Look for the section that contains this project's title and extract delete id inside it
    import re

    title = "Photo Project"
    # Capture from the title's <h3> through the end of the section
    sec_re = re.compile(rf"<h3>\s*{re.escape(title)}\s*</h3>(.*?)</section>", re.DOTALL)
    sec_m = sec_re.search(page)
    assert sec_m, f"No section found for project title '{title}'"
    section_html = sec_m.group(1)
    m = re.search(r"/delete_project/(\d+)", section_html)
    assert m, "No delete link found in project's section"
    proj_id = int(m.group(1))

    # Post delete
    resp3 = client.post(f"/delete_project/{proj_id}", follow_redirects=True)
    assert resp3.status_code == 200
    page_after = resp3.get_data(as_text=True)
    assert "Photo Project" not in page_after

