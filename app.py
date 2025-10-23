from flask import Flask, render_template, request, redirect, url_for
from DAL import create_connection, query_data, insert_data, initialize_database, get_table_columns
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure upload folder and allowed extensions
# Use app.root_path so paths are correct inside containers and when app is started
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "images")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure the upload folder exists so saving doesn't fail when no images yet
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Database path (use absolute path inside the app so the file is predictable)
DB_PATH = os.path.join(app.root_path, "projects.db")

# Ensure database and tables exist (creates the app DB file with Title/Description/ImageFileName)
initialize_database(DB_PATH)

# Column name mapping will be detected at runtime so the app can work with test DBs
# that use lowercase column names (title, description, image_filename).
COLUMN_MAP = None

def ensure_column_map():
    """Detect which column names the connected DB uses and cache the mapping.

    Returns a dict: {"title_col": ..., "desc_col": ..., "img_col": ...}
    """
    global COLUMN_MAP
    if COLUMN_MAP is not None:
        return COLUMN_MAP

    # Use the app-level create_connection so tests can monkeypatch it
    conn = None
    try:
        conn = create_connection(DB_PATH)
        cols = get_table_columns(conn, "projects")
    finally:
        if conn:
            conn.close()

    # Prefer capitalized names created by initialize_database, but fall back to lowercase
    title_col = "Title" if "Title" in cols else ("title" if "title" in cols else "Title")
    desc_col = "Description" if "Description" in cols else ("description" if "description" in cols else "Description")
    img_col = "ImageFileName" if "ImageFileName" in cols else ("image_filename" if "image_filename" in cols else "ImageFileName")

    COLUMN_MAP = {"title_col": title_col, "desc_col": desc_col, "img_col": img_col}
    return COLUMN_MAP

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Serve the home page
@app.route("/")     # Default page when you only type the Server URL
@app.route("/home") # Explicit name when you type the Server URL and the route name
# 4. Now let’s tell the website what we should send to the person's web browser who visited our page
def hello_world():
    return render_template("home.html")

# Serve the About Me page
@app.route("/aboutme")
def about_me():
    return render_template("about.html")

# Serve the Resume page
@app.route("/resume")
def resume():
    return render_template("resume.html")

# Serve the Projects page
@app.route("/projects")
def projectsPage():
    # Connect to the database and fetch all projects
    conn = create_connection(DB_PATH)
    projects = []
    if conn:
        colmap = ensure_column_map()
        query_sql = f"SELECT id, {colmap['title_col']}, {colmap['desc_col']}, {colmap['img_col']} FROM projects"
        rows = query_data(conn, query_sql)
        # Convert rows to dictionaries for easier access in the template
        projects = [
            {"id": row[0], "title": row[1], "description": row[2], "image_filename": row[3]} for row in rows
        ]
        conn.close()

    # Pass the projects data to the template
    return render_template("projects.html", projects=projects)

# Delete a project
@app.route("/delete_project/<int:project_id>", methods=["POST"])
def delete_project(project_id):
    # Connect to the database
    conn = create_connection(DB_PATH)
    if conn:
        delete_sql = "DELETE FROM projects WHERE id = ?"
        insert_data(conn, delete_sql, (project_id,))
        conn.close()

    # Redirect to the projects page
    return redirect(url_for("projectsPage"))

# Serve the Contact page
@app.route("/contact")
def contact():
    return render_template("contact.html")

# Serve the Thank You page
@app.route("/thankyou")
def thank_you():
    return render_template("thankyou.html")

# Serve the Add Project Form page
@app.route("/add_project", methods=["GET", "POST"])
def add_project():
    if request.method == "POST":
        # Extract form data
        title = request.form.get("title")
        description = request.form.get("description")
        image_file = request.files.get("image_file")

        # Handle file upload
        # Default to empty string for image filename so projects can be added without an upload
        image_filename = ""
        # Only save if a file was uploaded and it has an allowed extension
        if image_file and image_file.filename and allowed_file(image_file.filename):
            image_filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config["UPLOAD_FOLDER"], image_filename))

        # Connect to the database and insert the new project
        conn = create_connection(DB_PATH)
        if conn:
            colmap = ensure_column_map()
            insert_sql = f"INSERT INTO projects ({colmap['title_col']}, {colmap['desc_col']}, {colmap['img_col']}) VALUES (?, ?, ?)"
            insert_data(conn, insert_sql, (title, description, image_filename))
            conn.close()

        # Redirect to the projects page
        return redirect(url_for("projectsPage"))

    return render_template("project_form.html")

if __name__ == "__main__":
    # Listen on all interfaces so the container can accept external traffic
    app.run(host="0.0.0.0", port=5000, debug=True)