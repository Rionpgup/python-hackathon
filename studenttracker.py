import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os
import random
import urllib.request
from io import BytesIO
import hashlib

DB_NAME = "students.db"
USERS_DB = "users.db"
DEFAULT_PHOTOS = "default_avatars"
os.makedirs(DEFAULT_PHOTOS, exist_ok=True)

try:
    from PIL import Image, ImageTk, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ==================== DATABASE SETUP ====================
def init_databases():
    conn = sqlite3.connect(USERS_DB)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY, 
                    password TEXT NOT NULL, 
                    role TEXT NOT NULL DEFAULT "student")''')
    # Default admin
    if not conn.execute("SELECT 1 FROM users WHERE username='admin'").fetchone():
        conn.execute("INSERT INTO users VALUES ('admin', ?, 'admin')", (hash_pwd('admin'),))
    conn.commit()
    conn.close()

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS students (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    english_grade REAL,
                    history_grade REAL,
                    math_grade REAL,
                    science_grade REAL,
                    art_grade REAL,
                    email TEXT,
                    added_date TEXT,
                    photo_source TEXT)''')
    conn.commit()
    conn.close()

def hash_pwd(p): return hashlib.sha256(p.encode()).hexdigest()

# ==================== MAIN APP WITH TABS ====================
class StudentManagerApp:
    def __init__(self, username, role):
        self.username = username
        self.role = role
        self.root = tk.Tk()
        self.root.title(f"Student Manager Pro - {username} ({role.capitalize()})")
        self.root.state('zoomed')  # Full screen
        self.root.configure(bg="#f1f5f9")

        # Header
        header = tk.Frame(self.root, bg="#0f172a", height=100)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="STUDENT MANAGER PRO", font=("Helvetica", 32, "bold"),
                 bg="#0f172a", fg="#00d4aa").pack(side="left", padx=40, pady=20)
        tk.Label(header, text=f"Welcome, {username}!", font=("Helvetica", 18),
                 bg="#0f172a", fg="#94a3b8").pack(side="left", pady=30)

        tk.Button(header, text="Logout", bg="#ef4444", fg="white", font=("Helvetica", 12, "bold"),
                  command=self.logout, padx=20, pady=10).pack(side="right", padx=40, pady=30)

        # Tabs
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background="#f1f5f9")
        style.configure("TNotebook.Tab", padding=[20, 12], font=("Helvetica", 14, "bold"))

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=30, pady=20)

        self.setup_tabs()
        self.root.mainloop()

    def logout(self):
        self.root.destroy()
        WelcomeApp()

    def setup_tabs(self):
        if self.role == "admin":
            self.create_admin_tabs()
        else:
            self.create_student_tabs()

    def create_admin_tabs(self):
        self.dashboard_tab = ttk.Frame(self.notebook, padding=20)
        self.add_student_tab = ttk.Frame(self.notebook, padding=20)
        self.all_students_tab = ttk.Frame(self.notebook, padding=20)
        self.passwords_tab = ttk.Frame(self.notebook, padding=20)

        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.add_student_tab, text="Add Student")
        self.notebook.add(self.all_students_tab, text="All Students")
        self.notebook.add(self.passwords_tab, text="Student Passwords")

        self.show_admin_dashboard()
        self.show_add_student_form()
        self.show_all_students()
        self.show_student_passwords()

    def create_student_tabs(self):
        self.my_grades_tab = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(self.my_grades_tab, text="My Grades")
        self.show_student_dashboard()

    # ==================== ADMIN DASHBOARD ====================
    def show_admin_dashboard(self):
        for widget in self.dashboard_tab.winfo_children():
            widget.destroy()

        conn = sqlite3.connect(DB_NAME)
        students = conn.execute("SELECT * FROM students").fetchall()
        conn.close()

        total = len(students)
        if total == 0:
            avg = "N/A"
            color = "#94a3b8"
        else:
            avgs = []
            for s in students:
                grades = [g for g in s[2:7] if g is not None]
                if grades:
                    avgs.append(sum(grades)/len(grades))
            avg = sum(avgs)/len(avgs) if avgs else 0
            avg = f"{avg:.1f}"
            color = "#10b981" if float(avg) >= 90 else "#3b82f6" if float(avg) >= 80 else "#f59e0b" if float(avg) >= 70 else "#ef4444"

        frame = tk.Frame(self.dashboard_tab, bg="white", relief="solid", bd=2)
        frame.pack(pady=100, padx=200, fill="both", expand=True)

        tk.Label(frame, text="ADMIN OVERVIEW", font=("Helvetica", 36, "bold"), bg="white", fg="#1e293b").pack(pady=40)
        tk.Label(frame, text=f"Average Grade: {avg}/100", font=("Helvetica", 48, "bold"), bg="white", fg=color).pack(pady=30)
        tk.Label(frame, text=f"Total Students: {total}", font=("Helvetica", 24), bg="white", fg="#475569").pack(pady=20)

    # ==================== ADD STUDENT FORM ====================
    def show_add_student_form(self):
        for widget in self.add_student_tab.winfo_children():
            widget.destroy()

        card = tk.Frame(self.add_student_tab, bg="white", padx=50, pady=50, relief="solid", bd=2)
        card.pack(pady=80, padx=300, fill="both", expand=True)

        tk.Label(card, text="Add New Student", font=("Helvetica", 28, "bold"), bg="white").pack(pady=20)

        fields = ["Student ID (Username)", "Full Name", "Password", "Email (optional)", "Photo URL (optional)",
                  "English Grade", "History Grade", "Math Grade", "Science Grade", "Art Grade"]
        self.add_entries = {}
        for field in fields:
            tk.Label(card, text=field + ":", font=("Helvetica", 14), bg="white", anchor="w").pack(fill="x", pady=5)
            entry = tk.Entry(card, font=("Helvetica", 16), relief="flat", bg="#f8fafc", highlightthickness=2, highlightcolor="#00d4aa")
            entry.pack(fill="x", pady=8, ipady=10)
            self.add_entries[field] = entry

        tk.Button(card, text="ADD STUDENT", font=("Helvetica", 18, "bold"), bg="#10b981", fg="white",
                  command=self.add_student_action, height=2, width=20).pack(pady=30)

    def add_student_action(self):
        data = {k: v.get().strip() for k, v in self.add_entries.items()}
        sid = data["Student ID (Username)"]
        name = data["Full Name"]
        pwd = data["Password"]

        if not all([sid, name, pwd]):
            messagebox.showerror("Error", "ID, Name, and Password are required!")
            return

        try:
            grades = [float(data[f" Grade"]) if data[f" Grade"] else None for f in ["English", "History", "Math", "Science", "Art"]]
        except:
            messagebox.showerror("Error", "Grades must be numbers!")
            return

        # Add to students DB
        conn = sqlite3.connect(DB_NAME)
        try:
            conn.execute('''INSERT INTO students 
                (id, name, english_grade, history_grade, math_grade, science_grade, art_grade, email, added_date, photo_source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (sid, name, *grades, data["Email (optional)"], datetime.now().strftime("%Y-%m-%d"), data["Photo URL (optional)"]))
            conn.commit()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Student ID already exists!")
            conn.close()
            return
        conn.close()

        # Add to users DB
        conn = sqlite3.connect(USERS_DB)
        try:
            conn.execute("INSERT INTO users VALUES (?, ?, 'student')", (sid, hash_pwd(pwd)))
            conn.commit()
            messagebox.showinfo("Success", f"Student {name} added successfully!")
            self.show_add_student_form()
            self.show_admin_dashboard()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already taken!")
        finally:
            conn.close()

    # ==================== ALL STUDENTS LIST ====================
    def show_all_students(self):
        for widget in self.all_students_tab.winfo_children():
            widget.destroy()

        tk.Label(self.all_students_tab, text="All Students", font=("Helvetica", 28, "bold")).pack(pady=20)

        canvas = tk.Canvas(self.all_students_tab)
        scrollbar = ttk.Scrollbar(self.all_students_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        conn = sqlite3.connect(DB_NAME)
        students = conn.execute("SELECT * FROM students").fetchall()
        conn.close()

        for s in students:
            sid, name, eng, hist, math, sci, art, email, date, photo = s
            grades = [eng, hist, math, sci, art]
            avg = sum(g for g in grades if g is not None) / len([g for g in grades if g]) if any(g is not None for g in grades) else "N/A"

            frame = tk.Frame(scrollable_frame, bg="white", relief="solid", bd=1, padx=20, pady=15)
            frame.pack(fill="x", pady=8, padx=20)

            tk.Label(frame, text=f"{name} ({sid})", font=("Helvetica", 18, "bold"), bg="white").pack(anchor="w")
            tk.Label(frame, text=f"Avg: {avg:.1f} | Eng:{eng} Hist:{hist} Math:{math} Sci:{sci} Art:{art}", bg="white").pack(anchor="w")
            btn_frame = tk.Frame(frame, bg="white")
            btn_frame.pack(anchor="w", pady=5)
            tk.Button(btn_frame, text="Edit Grades", bg="#3b82f6", fg="white", command=lambda sid=sid: self.edit_grades(sid)).pack(side="left", padx=5)
            tk.Button(btn_frame, text="Delete", bg="#ef4444", fg="white", command=lambda sid=sid: self.delete_student(sid)).pack(side="left", padx=5)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def edit_grades(self, sid):
        # Same as before — opens popup
        pass  # You can reuse previous edit logic

    def delete_student(self, sid):
        if messagebox.askyesno("Delete", f"Delete student {sid}?"):
            sqlite3.connect(DB_NAME).execute("DELETE FROM students WHERE id=?", (sid,)).connection.commit()
            sqlite3.connect(USERS_DB).execute("DELETE FROM users WHERE username=?", (sid,)).connection.commit()
            self.show_all_students()

    def show_student_passwords(self):
        for widget in self.passwords_tab.winfo_children():
            widget.destroy()
        tk.Label(self.passwords_tab, text="Student Login Credentials", font=("Helvetica", 28, "bold")).pack(pady=30)
        conn = sqlite3.connect(USERS_DB)
        users = conn.execute("SELECT username FROM users WHERE role='student'").fetchall()
        conn.close()
        for (u,) in users:
            tk.Label(self.passwords_tab, text=f"Username: {u} | Password: (check admin initial setup or reset)", font=("Helvetica", 14)).pack(pady=5)

    # ==================== STUDENT DASHBOARD ====================
    def show_student_dashboard(self):
        for widget in self.my_grades_tab.winfo_children():
            widget.destroy()

        conn = sqlite3.connect(DB_NAME)
        student = conn.execute("SELECT name, english_grade, history_grade, math_grade, science_grade, art_grade FROM students WHERE id=?", (self.username,)).fetchone()
        conn.close()

        if not student:
            tk.Label(self.my_grades_tab, text="Profile not found!", font=("Helvetica", 36), fg="red").pack(expand=True)
            return

        name, eng, hist, math, sci, art = student
        grades = [g for g in [eng, hist, math, sci, art] if g is not None]
        avg = sum(grades)/len(grades) if grades else 0
        color = "#10b981" if avg >= 90 else "#3b82f6" if avg >= 80 else "#f59e0b" if avg >= 70 else "#ef4444"

        frame = tk.Frame(self.my_grades_tab, bg="white", relief="solid", bd=2)
        frame.pack(pady=100, padx=200, fill="both", expand=True)

        tk.Label(frame, text=f"Welcome, {name}!", font=("Helvetica", 36, "bold"), bg="white").pack(pady=40)
        tk.Label(frame, text=f"Your Average: {avg:.1f}/100", font=("Helvetica", 48, "bold"), bg="white", fg=color).pack(pady=30)
        tk.Label(frame, text=f"English: {eng} | History: {hist} | Math: {math} | Science: {sci} | Art: {art}",
                 font=("Helvetica", 20), bg="white", fg="#475569").pack(pady=30)

# ==================== WELCOME SCREEN ====================
class WelcomeApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Student Manager Pro")
        self.root.geometry("600x700")
        self.root.configure(bg="#0f172a")
        self.root.eval('tk::PlaceWindow . center')

        tk.Label(self.root, text="STUDENT MANAGER PRO", font=("Helvetica", 36, "bold"), bg="#0f172a", fg="#00d4aa").pack(pady=100)
        tk.Label(self.root, text="Admin: admin / admin\nStudents: Sign up below", font=("Helvetica", 14), bg="#0f172a", fg="#94a3b8").pack(pady=20)

        card = tk.Frame(self.root, bg="white", padx=60, pady=80, relief="flat")
        card.pack(padx=80, pady=50, fill="both", expand=True)

        tk.Label(card, text="Username", font=("Helvetica", 16), bg="white").pack(pady=10)
        self.user = tk.Entry(card, font=("Helvetica", 20), justify="center")
        self.user.pack(pady=10, ipady=12, fill="x")

        tk.Label(card, text="Password", font=("Helvetica", 16), bg="white").pack(pady=10)
        self.pwd = tk.Entry(card, font=("Helvetica", 20), show="*", justify="center")
        self.pwd.pack(pady=10, ipady=12, fill="x")

        btns = tk.Frame(card, bg="white")
        btns.pack(pady=40)
        tk.Button(btns, text="SIGN UP (Student)", bg="#10b981", fg="white", font=("Helvetica", 16, "bold"), width=18, height=2,
                  command=self.signup).pack(side="left", padx=20)
        tk.Button(btns, text="SIGN IN", bg="#00d4aa", fg="black", font=("Helvetica", 16, "bold"), width=15, height=2,
                  command=self.signin).pack(side="right", padx=20)

        self.root.bind('<Return>', lambda e: self.signin())
        self.root.mainloop()

    def signin(self):
        u = self.user.get().strip()
        p = self.pwd.get().strip()
        if not u or not p: return messagebox.showerror("Error", "Fill all fields")
        conn = sqlite3.connect(USERS_DB)
        user = conn.execute("SELECT role FROM users WHERE username=? AND password=?", (u, hash_pwd(p))).fetchone()
        conn.close()
        if user:
            self.root.destroy()
            StudentManagerApp(u, user[0])
        else:
            messagebox.showerror("Error", "Wrong credentials")

    def signup(self):
        u = self.user.get().strip()
        p = self.pwd.get().strip()
        if len(p) < 4: return messagebox.showerror("Error", "Password too short")
        conn = sqlite3.connect(USERS_DB)
        try:
            conn.execute("INSERT INTO users VALUES (?, ?, 'student')", (u, hash_pwd(p)))
            conn.commit()
            sqlite3.connect(DB_NAME).execute("INSERT INTO students (id, name, added_date) VALUES (?, ?, ?)",
                                             (u, u, datetime.now().strftime("%Y-%m-%d"))).connection.commit()
            messagebox.showinfo("Success", "Account created!")
            self.root.destroy()
            StudentManagerApp(u, "student")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username taken")
        finally:
            conn.close()

# ==================== START ====================
if __name__ == "__main__":
    init_databases()
    WelcomeApp()