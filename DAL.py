import sqlite3

def create_connection(db_file):
    """ Create a database connection to the SQLite database specified by db_file """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connection to {db_file} established.")
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
    return conn

def create_table(conn, create_table_sql):
    """ Create a table from the create_table_sql statement """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
        print("Table created successfully.")
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")

def insert_data(conn, insert_sql, data):
    """ Insert data into a table """
    try:
        c = conn.cursor()
        c.execute(insert_sql, data)
        conn.commit()
        print("Data inserted successfully.")
    except sqlite3.Error as e:
        print(f"Error inserting data: {e}")

def query_data(conn, query_sql):
    """ Query data from a table """
    try:
        c = conn.cursor()
        c.execute(query_sql)
        rows = c.fetchall()
        return rows
    except sqlite3.Error as e:
        print(f"Error querying data: {e}")
        return []

def initialize_database():
    """ Initialize the database and create the projects table """
    database = "projects.db"

    # SQL statement to create the projects table
    create_projects_table = """
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        image_filename TEXT NOT NULL
    );
    """

    # Create a database connection
    conn = create_connection(database)

    # Create the projects table
    if conn is not None:
        create_table(conn, create_projects_table)
        conn.close()
    else:
        print("Error! Cannot create the database connection.")

# Initialize the database when this script is run
if __name__ == "__main__":
    initialize_database()
    # Check the contents of the projects table
    conn = create_connection("projects.db")
    if conn:
        query = "SELECT * FROM projects"
        rows = query_data(conn, query)
        print("Projects Table Contents:")
        for row in rows:
            print(row)
        conn.close()