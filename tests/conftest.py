import sqlite3
import sys
import pathlib
import pytest

# Ensure the project root (falsk_app) is on sys.path so imports like `import app` and `import DAL` work
project_root = pathlib.Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import app as myapp


@pytest.fixture(scope="session")
def tmp_db_path(tmp_path_factory):
    """Create a temporary sqlite database file and initialize the projects table."""
    p = tmp_path_factory.mktemp("data") / "test_projects.db"
    conn = sqlite3.connect(str(p))
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        image_filename TEXT NOT NULL
    );
    """
    conn.executescript(create_table_sql)
    conn.commit()
    conn.close()
    return str(p)


@pytest.fixture(autouse=True)
def patch_create_connection(tmp_db_path, monkeypatch):
    """Monkeypatch the Flask app's create_connection to use the temp DB file.

    The app module imported `create_connection` at import time; we replace that
    symbol on the `app` module so routes open the temporary database.
    """

    def _create_connection(_db_file=None):
        # return a new connection to the temp DB for each call
        return sqlite3.connect(tmp_db_path, check_same_thread=False)

    monkeypatch.setattr(myapp, "create_connection", _create_connection)
    yield


@pytest.fixture
def client():
    myapp.app.testing = True
    with myapp.app.test_client() as client:
        yield client
