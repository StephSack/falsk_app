import DAL


def test_create_table_and_insert(tmp_path):
    # Create a temporary database path
    db_path = tmp_path / "test_projects.db"
    conn = DAL.create_connection(str(db_path))
    assert conn is not None

    # Create the projects table using the same SQL as the app
    create_projects_table = """
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        image_filename TEXT NOT NULL
    );
    """

    DAL.create_table(conn, create_projects_table)

    # Insert a sample project
    insert_sql = "INSERT INTO projects (title, description, image_filename) VALUES (?, ?, ?)"
    DAL.insert_data(conn, insert_sql, ("DB Test", "Testing DB insert", "test.png"))

    rows = DAL.query_data(conn, "SELECT title, description, image_filename FROM projects")
    assert len(rows) == 1
    assert rows[0][0] == "DB Test"
    assert rows[0][1] == "Testing DB insert"
    assert rows[0][2] == "test.png"

    conn.close()
