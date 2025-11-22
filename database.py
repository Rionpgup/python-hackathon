# db_viewer/database.py
import sqlite3
import os

DB_STUDENTS = "students.db"
DB_USERS = "users.db"

def get_table_data(db_name):
    """Returns columns and rows from the selected database"""
    if not os.path.exists(db_name):
        raise FileNotFoundError(f"Database {db_name} not found!")

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    if db_name == DB_STUDENTS:
        cur.execute("SELECT * FROM students")
    else:  # users.db
        cur.execute("SELECT * FROM users")

    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    conn.close()

    return columns, rows, len(rows)