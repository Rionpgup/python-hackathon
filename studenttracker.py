import sqlite3
from datetime import datetime

DB_NAME = "students.db"


# ----------------------------
# Database Setup
# ----------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            grade REAL,
            email TEXT,
            added_date TEXT
        )
    ''')
    conn.commit()
    conn.close()


# ----------------------------
# Helper: Grade Change Calculator
# ----------------------------
def calculate_grade_change(old_grade, new_grade):
    try:
        old = float(old_grade) if old_grade else 0
        new = float(new_grade)
        if old == 0:
            return "New grade assigned!", "blue"
        change = new - old
        percent = (change / old) * 100
        if change > 0:
            return f"UPGRADE: +{change} ({percent:+.1f}%)", "green"
        elif change < 0:
            return f"DOWNGRADE: {change} ({percent:+.1f}%)", "red"
        else:
            return "No change", "gray"
    except:
        return "Invalid grade", "red"


# ----------------------------
# CRUD Operations
# ----------------------------
def add_student():
    print("\n" + "—" * 40)
    print("        ADD NEW STUDENT")
    print("—" * 40)

    sid = input("Student ID: ").strip()
    if not sid:
        print("Error: ID cannot be empty!")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM students WHERE id = ?", (sid,))
    if cursor.fetchone():
        print(f"Error: Student ID '{sid}' already exists! Duplicates not allowed.")
        conn.close()
        return

    name = input("Student Name: ").strip()
    grade = input("Grade (e.g. 95.5): ").strip()
    email = input("Email: ").strip()

    if not name:
        print("Error: Name is required!")
        conn.close()
        return

    added_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute('''
        INSERT INTO students (id, name, grade, email, added_date)
        VALUES (?, ?, ?, ?, ?)
    ''', (sid, name, grade or None, email, added_date))

    conn.commit()
    conn.close()
    print(f"SUCCESS: Student '{name}' (ID: {sid}) added successfully!\n")


def view_students():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, grade, email, added_date FROM students ORDER BY name")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No students in database yet.\n")
        return

    print("\n" + "═" * 100)
    print("                               ALL STUDENTS")
    print("═" * 100)
    print(f"{'ID':<8} {'Name':<20} {'Grade':<8} {'Email':<25} {'Added'}")
    print("—" * 100)
    for row in rows:
        grade = row[2] if row[2] is not None else "N/A"
        print(f"{row[0]:<8} {row[1]:<20} {str(grade):<8} {row[3]:<25} {row[4]}")
    print("═" * 100 + "\n")


def search_students():
    term = input("\nSearch by Name or ID: ").strip().lower()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, grade, email FROM students
        WHERE LOWER(id) LIKE ? OR LOWER(name) LIKE ?
    ''', (f"%{term}%", f"%{term}%"))
    results = cursor.fetchall()
    conn.close()

    if not results:
        print("No students found matching your search.\n")
        return

    print(f"\nSearch Results for '{term}':\n")
    for r in results:
        grade = r[2] if r[2] else "N/A"
        print(f" → {r[0]} | {r[1]} | Grade: {grade} | {r[3]}")
    print()


def update_student():
    sid = input("\nEnter Student ID to update: ").strip()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name, grade, email FROM students WHERE id = ?", (sid,))
    student = cursor.fetchone()

    if not student:
        print("Error: Student not found!")
        conn.close()
        return

    name, old_grade, email = student
    print(f"\nFound: {name} | Current Grade: {old_grade or 'N/A'}")
    print("Leave blank to keep current value.\n")

    new_name = input(f"New name [{name}]: ").strip() or name
    new_email = input(f"New email [{email or 'None'}]: ").strip() or email
    new_grade_input = input(f"New grade [{old_grade or 'None'}]: ").strip()

    if new_grade_input:
        try:
            float(new_grade_input)
        except ValueError:
            print("Error: Grade must be a number!")
            conn.close()
            return

    # Update only changed fields
    cursor.execute('''
        UPDATE students SET name=?, email=? WHERE id=?
    ''', (new_name, new_email or None, sid))

    if new_grade_input:
        cursor.execute("UPDATE students SET grade=? WHERE id=?", (new_grade_input, sid))
        change_text, _ = calculate_grade_change(old_grade, new_grade_input)
        print(f"\nGrade updated: {old_grade or 0} → {new_grade_input}")
        print(f"   {change_text}\n")
    else:
        print("\nStudent info updated (grade unchanged)\n")

    conn.commit()
    conn.close()


def delete_student():
    sid = input("\nEnter Student ID to delete: ").strip()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM students WHERE id = ?", (sid,))
    student = cursor.fetchone()

    if not student:
        print("Error: Student not found!")
        conn.close()
        return

    confirm = input(f"Delete student '{student[0]}' (ID: {sid})? Type 'yes' to confirm: ")
    if confirm.lower() != "yes":
        print("Deletion cancelled.\n")
        conn.close()
        return

    cursor.execute("DELETE FROM students WHERE id = ?", (sid,))
    conn.commit()
    conn.close()
    print(f"Student '{student[0]}' has been permanently deleted.\n")


# ----------------------------
# Main Menu
# ----------------------------
def main():
    init_db()  # Create DB and table if not exists
    print("Student Grade Tracker with Database")
    print("Data saved permanently in 'students.db'")

    while True:
        print("\n" + "═" * 50)
        print("        STUDENT DATABASE MANAGER")
        print("═" * 50)
        print("1. Add Student")
        print("2. View All Students")
        print("3. Search Students")
        print("4. Update Student")
        print("5. Delete Student")
        print("6. Exit")
        print("─" * 50)

        choice = input("Choose option (1-6): ").strip()

        if choice == "1":
            add_student()
        elif choice == "2":
            view_students()
        elif choice == "3":
            search_students()
        elif choice == "4":
            update_student()
        elif choice == "5":
            delete_student()
        elif choice == "6":
            print("Thank you! Goodbye!")
            break
        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()