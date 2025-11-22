import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os
import hashlib

DB_NAME = "students.db"
USERS_DB = "users.db"

# ==================== DATABASE SETUP ====================
def init_databases():
    conn = sqlite3.connect(USERS_DB)
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY, 
                    password TEXT NOT NULL, 
                    role TEXT NOT NULL DEFAULT "student")''')
    if not conn.execute("SELECT 1 FROM users WHERE username='admin'").fetchone():
        conn.execute("INSERT INTO users VALUES ('admin', ?, 'admin')", (hash_pwd('admin'),))
    conn.commit()
    conn.close()

    conn = sqlite3.connect(DB_NAME)
    conn.execute('''CREATE TABLE IF NOT EXISTS students (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    english_grade REAL, history_grade REAL, math_grade REAL,
                    science_grade REAL, art_grade REAL,
                    email TEXT, added_date TEXT, photo_source TEXT)''')
    conn.commit()
    conn.close()

def hash_pwd(p): return hashlib.sha256(p.encode()).hexdigest()

# ==================== MAIN FULL-SCREEN APP WITH BIG TABS ====================
class StudentManagerApp:
    def __init__(self, username, role):
        self.username = username
        self.role = role

        # FULL SCREEN WINDOW
        self.root = tk.Tk()
        self.root.title(f"Student Manager Pro - {username} ({'Teacher' if role=='admin' else 'Student'})")
        self.root.state('zoomed')                    # FULL SCREEN
        self.root.configure(bg="#f8fafc")

        # ==================== MODERN STYLE FOR BIG TABS ====================
        style = ttk.Style()
        style.theme_use('clam')

        # BIG, BOLD, BEAUTIFUL TABS
        style.configure("Big.TNotebook", background="#f8fafc", borderwidth=0)
        style.configure("Big.TNotebook.Tab",
                        font=("Helvetica", 16, "bold"),
                        padding=[40, 18],
                        background="#e2e8f0",
                        foreground="#1e293b")
        style.map("Big.TNotebook.Tab",
                  background=[("selected", "#00d4aa"), ("active", "#94a3b8")],
                  foreground=[("selected", "white"), ("active", "white")])

        # ==================== HEADER ====================
        header = tk.Frame(self.root, bg="#0f172a", height=100)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="STUDENT MANAGER PRO", font=("Helvetica", 38, "bold"),
                 bg="#0f172a", fg="#00d4aa").pack(side="left", padx=50, pady=20)
        tk.Label(header, text=f"Welcome, {username}!", font=("Helvetica", 20),
                 bg="#0f172a", fg="#94a3b8").pack(side="left", pady=35)

        tk.Button(header, text="LOGOUT", bg="#ef4444", fg="white", font=("Helvetica", 14, "bold"),
                  padx=30, pady=12, command=self.logout, cursor="hand2").pack(side="right", padx=50, pady=25)

        # ==================== FULL-SIZE TABS ====================
        self.notebook = ttk.Notebook(self.root, style="Big.TNotebook")
        self.notebook.pack(fill="both", expand=True, padx=30, pady=30)  # FULL SIZE!

        if role == "admin":
            self.create_admin_tabs()
        else:
            self.create_student_tabs()

        self.root.mainloop()

    def logout(self):
        self.root.destroy()
        WelcomeApp()

    def create_admin_tabs(self):
        self.tab_dashboard = ttk.Frame(self.notebook)
        self.tab_add = ttk.Frame(self.notebook)
        self.tab_all = ttk.Frame(self.notebook)
        self.tab_passwords = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_dashboard, text="  Dashboard  ")
        self.notebook.add(self.tab_add, text="  Add Student  ")
        self.notebook.add(self.tab_all, text="  All Students  ")
        self.notebook.add(self.tab_passwords, text="  Passwords  ")

        self.show_admin_dashboard()
        self.show_add_student_form()
        self.show_all_students()
        self.show_passwords()

    def create_student_tabs(self):
        self.tab_grades = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_grades, text="  My Grades  ")
        self.show_student_grades()

    # ==================== ADMIN DASHBOARD ====================
    def show_admin_dashboard(self):
        for w in self.tab_dashboard.winfo_children(): w.destroy()
        f = tk.Frame(self.tab_dashboard, bg="white")
        f.pack(fill="both", expand=True, padx=100, pady=80)

        conn = sqlite3.connect(DB_NAME)
        students = conn.execute("SELECT * FROM students").fetchall()
        conn.close()

        total = len(students)
        if total == 0:
            avg = "N/A"
            color = "#64748b"
        else:
            avgs = []
            for s in students:
                grades = [g for g in s[2:7] if g]
                if grades: avgs.append(sum(grades)/len(grades))
            avg = sum(avgs)/len(avgs) if avgs else 0
            avg = f"{avg:.1f}"
            color = "#10b981" if float(avg) >= 90 else "#3b82f6" if float(avg) >= 80 else "#f59e0b" if float(avg) >= 70 else "#ef4444"

        tk.Label(f, text="TEACHER DASHBOARD", font=("Helvetica", 40, "bold"), bg="white", fg="#1e293b").pack(pady=60)
        tk.Label(f, text=f"{avg}/100", font=("Helvetica", 80, "bold"), bg="white", fg=color).pack(pady=30)
        tk.Label(f, text=f"Overall Class Average • {total} Students", font=("Helvetica", 24), bg="white", fg="#475569").pack(pady=20)

    # ==================== ADD STUDENT ====================
    def show_add_student_form(self):
        for w in self.tab_add.winfo_children(): w.destroy()
        f = tk.Frame(self.tab_add, bg="white")
        f.pack(fill="both", expand=True, padx=150, pady=80)

        tk.Label(f, text="Add New Student", font=("Helvetica", 32, "bold"), bg="white").pack(pady=40)

        fields = ["Student ID", "Full Name", "Password", "Email", "English", "History", "Math", "Science", "Art"]
        self.entries = {}
        for field in fields:
            tk.Label(f, text=field + ":", font=("Helvetica", 16), bg="white").pack(anchor="w", padx=200, pady=5)
            e = tk.Entry(f, font=("Helvetica", 18), bg="#f1f5f9", relief="flat", highlightthickness=2, highlightcolor="#00d4aa")
            e.pack(fill="x", padx=200, pady=8, ipady=12)
            self.entries[field] = e

        tk.Button(f, text="ADD STUDENT", font=("Helvetica", 20, "bold"), bg="#10b981", fg="white",
                  command=self.add_student, height=2, width=25, cursor="hand2").pack(pady=50)

    def add_student(self):
        data = {k: v.get().strip() for k, v in self.entries.items()}
        if not all(data[x] for x in ["Student ID", "Full Name", "Password"]):
            return messagebox.showerror("Error", "Fill required fields!")

        try:
            grades = [float(data[s]) if data[s] else None for s in ["English","History","Math","Science","Art"]]
        except:
            return messagebox.showerror("Error", "Grades must be numbers!")

        conn = sqlite3.connect(DB_NAME)
        try:
            conn.execute("""INSERT INTO students 
                (id, name, english_grade, history_grade, math_grade, science_grade, art_grade, email, added_date)
                VALUES (?,?,?, ?,?,?,?, ?,?)""",
                (data["Student ID"], data["Full Name"], *grades, data["Email"], datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return messagebox.showerror("Error", "Student ID already exists!")
        conn.close()

        conn = sqlite3.connect(USERS_DB)
        conn.execute("INSERT INTO users VALUES (?,?, 'student')", (data["Student ID"], hash_pwd(data["Password"])))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Student added!")
        self.show_add_student_form()
        self.show_admin_dashboard()

    # ==================== ALL STUDENTS ====================
    def show_all_students(self):
        for w in self.tab_all.winfo_children(): w.destroy()
        canvas = tk.Canvas(self.tab_all)
        scrollbar = ttk.Scrollbar(self.tab_all, command=canvas.yview)
        scrollframe = ttk.Frame(canvas)
        canvas.create_window((0,0), window=scrollframe, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        conn = sqlite3.connect(DB_NAME)
        students = conn.execute("SELECT * FROM students").fetchall()
        conn.close()

        for s in students:
            sid, name, e,h,m,sci,a,*_ = s
            avg = sum(filter(None,[e,h,m,sci,a])) / len(list(filter(None,[e,h,m,sci,a]))) if any([e,h,m,sci,a]) else 0
            card = tk.Frame(scrollframe, bg="white", relief="solid", bd=1, pady=15, padx=30)
            card.pack(fill="x", pady=10, padx=50)
            tk.Label(card, text=f"{name} ({sid})", font=("Helvetica", 20, "bold"), bg="white").pack(anchor="w")
            tk.Label(card, text=f"Avg: {avg:.1f} | Eng:{e} Hist:{h} Math:{m} Sci:{sci} Art:{a}", bg="white").pack(anchor="w")
            tk.Button(card, text="Delete", bg="#ef4444", fg="white", command=lambda sid=sid:self.delete_student(sid)).pack(side="right")

    def delete_student(self, sid):
        if messagebox.askyesno("Delete", "Delete this student?"):
            sqlite3.connect(DB_NAME).execute("DELETE FROM students WHERE id=?", (sid,)).connection.commit()
            sqlite3.connect(USERS_DB).execute("DELETE FROM users WHERE username=?", (sid,)).connection.commit()
            self.show_all_students()

    def show_passwords(self):
        for w in self.tab_passwords.winfo_children(): w.destroy()
        tk.Label(self.tab_passwords, text="Student Login List", font=("Helvetica", 32, "bold")).pack(pady=50)
        conn = sqlite3.connect(USERS_DB)
        users = conn.execute("SELECT username FROM users WHERE role='student'").fetchall()
        conn.close()
        for (u,) in users:
            tk.Label(self.tab_passwords, text=f"Username: {u} → Password: Check your records or reset", font=("Helvetica", 18)).pack(pady=8)

    # ==================== STUDENT GRADES ====================
    def show_student_grades(self):
        for w in self.tab_grades.winfo_children(): w.destroy()
        conn = sqlite3.connect(DB_NAME)
        s = conn.execute("SELECT name, english_grade, history_grade, math_grade, science_grade, art_grade FROM students WHERE id=?", (self.username,)).fetchone()
        conn.close()
        if not s:
            tk.Label(self.tab_grades, text="No grades yet!", font=("Helvetica", 40)).pack(expand=True)
            return

        name, e,h,m,sci,a = s
        grades = [x for x in [e,h,m,sci,a] if x is not None]
        avg = sum(grades)/len(grades) if grades else 0
        color = "#10b981" if avg>=90 else "#3b82f6" if avg>=80 else "#f59e0b" if avg>=70 else "#ef4444"

        f = tk.Frame(self.tab_grades, bg="white")
        f.pack(fill="both", expand=True, padx=200, pady=100)
        tk.Label(f, text=f"Hello, {name}!", font=("Helvetica", 40, "bold"), bg="white").pack(pady=60)
        tk.Label(f, text=f"{avg:.1f}/100", font=("Helvetica", 90, "bold"), bg="white", fg=color).pack(pady=40)
        tk.Label(f, text=f"English: {e}  |  History: {h}  |  Math: {m}  |  Science: {sci}  |  Art: {a}",
                 font=("Helvetica", 24), bg="white", fg="#475569").pack(pady=40)

# ==================== WELCOME SCREEN ====================
class WelcomeApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Student Manager Pro")
        self.root.geometry("600x750")
        self.root.configure(bg="#0f172a")
        self.root.eval('tk::PlaceWindow . center')

        tk.Label(self.root, text="STUDENT MANAGER PRO", font=("Helvetica", 36, "bold"), bg="#0f172a", fg="#00d4aa").pack(pady=100)
        tk.Label(self.root, text="Admin → admin / admin", font=("Helvetica", 16), bg="#0f172a", fg="#94a3b8").pack(pady=10)

        card = tk.Frame(self.root, bg="white", padx=80, pady=80)
        card.pack(padx=80, pady=50, fill="both", expand=True)

        tk.Label(card, text="Username", font=("Helvetica", 16), bg="white").pack(pady=(20,10))
        self.user = tk.Entry(card, font=("Helvetica", 20), justify="center")
        self.user.pack(pady=10, ipady=15, fill="x")

        tk.Label(card, text="Password", font=("Helvetica", 16), bg="white").pack(pady=(20,10))
        self.pwd = tk.Entry(card, font=("Helvetica", 20), show="*", justify="center")
        self.pwd.pack(pady=10, ipady=15, fill="x")

        btns = tk.Frame(card, bg="white")
        btns.pack(pady=50)
        tk.Button(btns, text="SIGN UP (Student)", bg="#10b981", fg="white", font=("Helvetica", 16, "bold"), width=20, height=2,
                  command=self.signup).pack(side="left", padx=20)
        tk.Button(btns, text="SIGN IN", bg="#00d4aa", fg="black", font=("Helvetica", 16, "bold"), width=15, height=2,
                  command=self.signin).pack(side="right", padx=20)

        self.root.mainloop()

    def signin(self):
        u, p = self.user.get().strip(), self.pwd.get().strip()
        if not u or not p: return messagebox.showerror("Error", "Fill all fields")
        conn = sqlite3.connect(USERS_DB)
        user = conn.execute("SELECT role FROM users WHERE username=? AND password=?", (u, hash_pwd(p))).fetchone()
        conn.close()
        if user:
            self.root.destroy()
            StudentManagerApp(u, user[0])
        else:
            messagebox.showerror("Error", "Wrong login")

    def signup(self):
        u, p = self.user.get().strip(), self.pwd.get().strip()
        if len(p) < 4: return messagebox.showerror("Error", "Password too short")
        conn = sqlite3.connect(USERS_DB)
        try:
            conn.execute("INSERT INTO users VALUES (?,?, 'student')", (u, hash_pwd(p)))
            conn.commit()
            sqlite3.connect(DB_NAME).execute("INSERT INTO students (id, name, added_date) VALUES (?,?,?)",
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