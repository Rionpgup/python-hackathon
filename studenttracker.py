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
        return json.load(f)

def save_data(students):
    with open(DATA_FILE, "w") as f:
        json.dump(students, f, indent=4)

# ----------------------------
# CRUD FUNCTIONS
# ----------------------------

def add_student():
    students = load_data()
    student = {
        "id": input("Student ID: "),
        "name": input("Student Name: "),
        "grade": input("Grade: "),
        "email": input("Email: ")
    }
    students.append(student)
    save_data(students)
    print("✅ Student added!\n")

def view_students():
    students = load_data()
    if not students:
        print("No students found.\n")
        return
    print("\n--- Student List ---")
    for s in students:
        print(f"ID: {s['id']} | Name: {s['name']} | Grade: {s['grade']} | Email: {s['email']}")
    print()

def update_student():
    students = load_data()
    sid = input("Enter Student ID to update: ")

    for s in students:
        if s["id"] == sid:
            print("Leave blank to skip updating a field.")
            name = input(f"New name ({s['name']}): ") or s["name"]
            grade = input(f"New grade ({s['grade']}): ") or s["grade"]
            email = input(f"New email ({s['email']}): ") or s["email"]

            s["name"] = name
            s["grade"] = grade
            s["email"] = email

            save_data(students)
            print("✅ Student updated!\n")
            return

    print("❌ Student not found.\n")

def delete_student():
    students = load_data()
    sid = input("Enter Student ID to delete: ")

    updated = [s for s in students if s["id"] != sid]

    if len(updated) == len(students):
        print("❌ Student not found.\n")
    else:
        save_data(updated)
        print("🗑️ Student deleted!\n")



def main():
    while True:
        print("\n=== STUDENT TRACKER ===")
        print("1. Add Student")
        print("2. View Students")
        print("3. Update Student")
        print("4. Delete Student")
        print("5. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            add_student()
        elif choice == "2":
            view_students()
        elif choice == "3":
            update_student()
        elif choice == "4":
            delete_student()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.\n")


if __name__ == "__main__":
    main()
