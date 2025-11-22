import json
import os

DATA_FILE = "students.json"

# ----------------------------
# Load & Save Student Data
# ----------------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print("Warning: Corrupted data file. Starting fresh.")
            return []

def save_data(students):
    with open(DATA_FILE, "w") as f:
        json.dump(students, f, indent=4)

# ----------------------------
# Helper: Calculate grade change
# ----------------------------
def calculate_grade_change(old_grade, new_grade):
    try:
        old = float(old_grade)
        new = float(new_grade)
        if old == 0:
            return "New grade set!", ""
        change = new - old
        percent_change = (change / old) * 100
        if change > 0:
            return f"Upgrade: +{change} ({percent_change:+.1f}%)", "green"
        elif change < 0:
            return f"Downgrade: {change} ({percent_change:+.1f}%)", "red"
        else:
            return "No change", "gray"
    except ValueError:
        return "Invalid grade format", "red"

# ----------------------------
# Check if ID already exists
# ----------------------------
def is_id_exists(student_id):
    students = load_data()
    return any(s["id"] == student_id for s in students)

# ----------------------------
# CRUD FUNCTIONS (Enhanced + No Duplicates)
# ----------------------------
def add_student():
    print("\n--- Add New Student ---")
    student_id = input("Student ID: ").strip()

    # Check for duplicate ID
    if is_id_exists(student_id):
        print(f"Error: Student ID '{student_id}' already exists! Duplicate IDs are not allowed.")
        return

    student = {
        "id": student_id,
        "name": input("Student Name: ").strip(),
        "grade": input("Grade (e.g. 85.5): ").strip(),
        "email": input("Email: ").strip()
    }

    # Basic validation
    if not student["id"] or not student["name"]:
        print("Error: ID and Name cannot be empty!")
        return

    students = load_data()
    students.append(student)
    save_data(students)
    print(f"Success: Student '{student['name']}' added with ID {student['id']}!\n")

def view_students():
    students = load_data()
    if not students:
        print("No students found.\n")
        return

    print("\n" + "═" * 80)
    print("                           STUDENT LIST")
    print("═" * 80)
    print(f"{'ID':<8} {'Name':<20} {'Grade':<10} {'Email'}")
    print("─" * 80)
    for s in students:
        grade = s.get("grade", "N/A")
        print(f"{s['id']:<8} {s['name']:<20} {grade:<10} {s['email']}")
    print("═" * 80 + "\n")

def update_student():
    students = load_data()
    sid = input("\nEnter Student ID to update: ").strip()

    for s in students:
        if s["id"] == sid:
            print(f"\nFound: {s['name']} | Current Grade: {s['grade']}")
            print("Leave blank to keep current value.\n")

            name = input(f"New name [{s['name']}]: ").strip() or s["name"]
            email = input(f"New email [{s['email']}]: ").strip() or s["email"]
            new_grade_input = input(f"New grade [{s['grade']}]: ").strip()

            old_grade = s["grade"]

            s["name"] = name
            s["email"] = email

            if new_grade_input:
                s["grade"] = new_grade_input
                change_text, _ = calculate_grade_change(old_grade, new_grade_input)
                print(f"\nSuccess: Grade updated: {old_grade} → {new_grade_input}")
                print(f"   {change_text}\n")
            else:
                print(f"\nSuccess: Student info updated (grade unchanged)\n")

            save_data(students)
            return

    print("Error: Student not found with that ID.\n")

def delete_student():
    students = load_data()
    sid = input("\nEnter Student ID to delete: ").strip()

    if not is_id_exists(sid):
        print("Error: No student found with that ID.\n")
        return

    confirm = input(f"Are you sure you want to delete student ID {sid}? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Deletion cancelled.\n")
        return

    updated = [s for s in students if s["id"] != sid]
    save_data(updated)
    print(f"Success: Student ID {sid} has been deleted.\n")

# ----------------------------
# Main Menu
# ----------------------------
def main():
    print("Welcome to Student Grade Tracker!")
    while True:
        print("\n" + "═" * 45)
        print("       STUDENT GRADE TRACKER")
        print("═" * 45)
        print("1. Add Student")
        print("2. View All Students")
        print("3. Update Student")
        print("4. Delete Student")
        print("5. Exit")
        print("─" * 45)

        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            add_student()
        elif choice == "2":
            view_students()
        elif choice == "3":
            update_student()
        elif choice == "4":
            delete_student()
        elif choice == "5":
            print("Thank you for using Student Grade Tracker! Goodbye!")
            break
        else:
            print("Error: Invalid choice. Please enter 1–5.\n")

if __name__ == "__main__":
    main()