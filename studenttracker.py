# student_tracker_pure_python.py
# 100% Pure Python - Beautiful Green GUI Student Tracker
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime

# ============================
# Database Setup
# ============================
DB_NAME = "students.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute('''
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


# ============================
# Grade Change Calculator
# ============================
def calculate_grade_change(old, new):
    try:
        old_val = float(old) if old else 0
        new_val = float(new)
        if old_val == 0:
            return f"New grade: {new_val} SUCCESS"
        change = new_val - old_val
        percent = (change / old_val) * 100
        if change > 0:
            return f"UPGRADE +{change:.1f} ({percent:+.1f}%) SUCCESS"
        elif change < 0:
            return f"DOWNGRADE {change:.1f} ({percent:+.1f}%) WARNING"
        else:
            return "No change INFO"
    except:
        return "Invalid grade ERROR"


# ============================
# Main App Class
# ============================
class StudentTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Tracker Pro")
        self.root.geometry("1000x650")
        self.root.configure(bg="#e8f5e8")

        # Title
        title = tk.Label(root, text="STUDENT TRACKER PRO", font=("Arial", 28, "bold"),
                         bg="#e8f5e8", fg="#1b5e20")
        title.pack(pady=20)

        # Buttons Frame
        btn_frame = tk.Frame(root, bg="#e8f5e8")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add Student", font=("Arial", 14, "bold"), bg="#2e7d32", fg="white",
                  width=15, height=2, command=self.add_student).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Refresh List", font=("Arial", 14, "bold"), bg="#1b5e20", fg="white",
                  width=15, height=2, command=self.load_students).pack(side=tk.LEFT, padx=10)

        # Treeview (Table)
        columns = ("ID", "Name", "Grade", "Email", "Added")
        self.tree = ttk.Treeview(root, columns=columns, show="headings", height=18)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
        self.tree.column("Name", width=200)
        self.tree.column("Email", width=250)

        self.tree.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Right-click menu
        self.menu = tk.Menu(root, tearoff=0)
        self.menu.add_command(label="Edit Student", command=self.edit_student)
        self.menu.add_command(label="Delete Student", command=self.delete_student)
        self.tree.bind("<Button-3>", self.show_menu)  # Right click

        # Status bar
        self.status = tk.Label(root, text="Ready", bg="#c8e6c9", fg="#1b5e20", font=("Arial", 12), relief=tk.SUNKEN,
                               anchor=tk.W)
        self.status.pack(fill=tk.X)

        self.load_students()

    def load_students(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, grade, email, added_date FROM students ORDER BY name")
        for row in cursor.fetchall():
            grade = row[2] if row[2] is not None else "N/A"
            self.tree.insert("", "end", values=(row[0], row[1], grade, row[3] or "-", row[4]))
        conn.close()
        self.status.config(text=f"Total Students: {len(self.tree.get_children())}")

    def add_student(self):
        self.show_form("Add Student")

    def edit_student(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a student!")
            return
        values = self.tree.item(selected[0])["values"]
        self.show_form("Edit Student", values)

    def delete_student(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a student!")
            return
        sid = self.tree.item(selected[0])["values"][0]
        name = self.tree.item(selected[0])["values"][1]

        if messagebox.askyesno("Delete", f"Delete student '{name}' (ID: {sid})?"):
            conn = sqlite3.connect(DB_NAME)
            conn.execute("DELETE FROM students WHERE id = ?", (sid,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Deleted", f"Student '{name}' deleted!")
            self.load_students()

    def show_menu(self, event):
        try:
            self.tree.selection_set(self.tree.identify_row(event.y))
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def show_form(self, title, data=None):
        form = tk.Toplevel(self.root)
        form.title(title)
        form.geometry("400x500")
        form.configure(bg="#e8f5e8")
        form.grab_set()

        tk.Label(form, text=title, font=("Arial", 18, "bold"), bg="#e8f5e8", fg="#1b5e20").pack(pady=20)

        # Form fields
        tk.Label(form, text="Student ID:", font=("Arial", 12), bg="#e8f5e8", fg="#1b5e20").pack()
        id_entry = tk.Entry(form, font=("Arial", 12), width=30)
        id_entry.pack(pady=5)

        tk.Label(form, text="Full Name:", font=("Arial", 12), bg="#e8f5e8", fg="#1b5e20").pack()
        name_entry = tk.Entry(form, font=("Arial", 12), width=30)
        name_entry.pack(pady=5)

        tk.Label(form, text="Grade (e.g. 95.5):", font=("Arial", 12), bg="#e8f5e8", fg="#1b5e20").pack()
        grade_entry = tk.Entry(form, font=("Arial", 12), width=30)
        grade_entry.pack(pady=5)

        tk.Label(form, text="Email:", font=("Arial", 12), bg="#e8f5e8", fg="#1b5e20").pack()
        email_entry = tk.Entry(form, font=("Arial", 12), width=30)
        email_entry.pack(pady=5)

        if data:
            id_entry.insert(0, data[0])
            id_entry.config(state="disabled")  # Can't change ID
            name_entry.insert(0, data[1])
            grade_entry.insert(0, data[2] if data[2] != "N/A" else "")
            email_entry.insert(0, data[3] if data[3] != "-" else "")

        def save():
            sid = id_entry.get().strip()
            name = name_entry.get().strip()
            grade = grade_entry.get().strip()
            email = email_entry.get().strip()

            if not sid or not name:
                messagebox.showerror("Error", "ID and Name are required!")
                return

            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            if data:  # Update
                old_grade = data[2] if data[2] != "N/A" else None
                cursor.execute("UPDATE students SET name=?, grade=?, email=? WHERE id=?",
                               (name, grade or None, email or None, sid))
                change = calculate_grade_change(old_grade, grade) if grade else ""
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", f"Student updated!\n{change}")
            else:  # Add new
                try:
                    cursor.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?)",
                                   (sid, name, grade or None, email or None, datetime.now().strftime("%Y-%m-%d %H:%M")))
                    conn.commit()
                    conn.close()
                    messagebox.showinfo("Success", f"Student '{name}' added!")
                except sqlite3.IntegrityError:
                    conn.close()
                    messagebox.showerror("Error", f"Student ID '{sid}' already exists!")

            form.destroy()
            self.load_students()

        tk.Button(form, text="Save", font=("Arial", 14, "bold"), bg="#2e7d32", fg="white",
                  width=15, height=2, command=save).pack(pady=30)


# ============================
# Run the App
# ============================
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = StudentTracker(root)
    root.mainloop()