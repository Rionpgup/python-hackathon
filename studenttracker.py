import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import hashlib

DB_NAME = "students.db"
USERS_DB = "users.db"

# ==================== DATABASE SETUP ====================
def init_databases():
    conn = sqlite3.connect(USERS_DB)
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY, password TEXT NOT NULL, role TEXT NOT NULL)''')
    if not conn.execute("SELECT 1 FROM users WHERE username='admin'").fetchone():
        conn.execute("INSERT INTO users VALUES ('admin', ?, 'admin')", (hash_pwd('admin'),))
    conn.commit()
    conn.close()

    conn = sqlite3.connect(DB_NAME)
    conn.execute('''CREATE TABLE IF NOT EXISTS students (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    surname TEXT NOT NULL,
                    email TEXT,
                    english REAL, history REAL, math REAL, science REAL, art REAL,
                    added_date TEXT)''')
    conn.commit()
    conn.close()

def hash_pwd(p): return hashlib.sha256(p.encode()).hexdigest()

def get_next_id():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id FROM students ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return "S001" if not row else f"S{int(row[0][1:]) + 1:03d}"

# ==================== MAIN APP ====================
class StudentManagerApp:
    def __init__(self, username, role):
        self.username = username
        self.role = role

        self.root = tk.Tk()
        self.root.title("Student Manager Pro")
        self.root.state('zoomed')
        self.root.configure(bg="#f1f5f9")

        # Big Beautiful Tabs Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Big.TNotebook", background="#f1f5f9")
        style.configure("Big.TNotebook.Tab",
                        font=("Helvetica", 18, "bold"),
                        padding=[60, 25],
                        background="#cbd5e1")
        style.map("Big.TNotebook.Tab",
                  background=[("selected", "#00d4aa")],
                  foreground=[("selected", "white")])

        # ==================== HEADER WITH + ADD STUDENT BUTTON ====================
        header = tk.Frame(self.root, bg="#0f172a", height=130)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Left: Title + Add Button
        left_frame = tk.Frame(header, bg="#0f172a")
        left_frame.pack(side="left", padx=60, pady=30)

        tk.Label(left_frame, text="STUDENT MANAGER PRO", font=("Helvetica", 42, "bold"),
                 bg="#0f172a", fg="#00d4aa").pack(anchor="w")

        tk.Label(left_frame, text=f"Teacher: {username}", font=("Helvetica", 20),
                 bg="#0f172a", fg="#94a3b8").pack(anchor="w", pady=(5,0))

        # BIG GREEN ADD BUTTON
        self.add_btn = tk.Button(left_frame, text="+ Add Student", font=("Helvetica", 20, "bold"),
                                 bg="#10b981", fg="white", relief="flat", cursor="hand2",
                                 padx=30, pady=18, command=self.open_add_student_popup)
        self.add_btn.pack(pady=20, anchor="w")

        # Right: Logout
        tk.Button(header, text="LOGOUT", bg="#ef4444", fg="white", font=("Helvetica", 16, "bold"),
                  padx=40, pady=15, command=self.logout).pack(side="right", padx=70, pady=40)

        # Tabs
        self.notebook = ttk.Notebook(self.root, style="Big.TNotebook")
        self.notebook.pack(fill="both", expand=True, padx=50, pady=40)

        if role == "admin":
            self.create_admin_tabs()
        else:
            self.create_student_tab()

        self.root.mainloop()

    def logout(self):
        self.root.destroy()
        WelcomeApp()

    # ==================== ADMIN TABS (NO "Add Student" tab anymore) ====================
    def create_admin_tabs(self):
        self.tab_list = ttk.Frame(self.notebook)
        self.tab_grades = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_list, text="  All Students  ")
        self.notebook.add(self.tab_grades, text="  Update Grades  ")

        self.show_all_students()
        self.show_update_grades_tab()

    def create_student_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="  My Grades  ")
        self.show_student_grades(tab)

    # ==================== POPUP: ADD STUDENT ====================
    def open_add_student_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Add New Student")
        popup.geometry("900x900")
        popup.configure(bg="white")
        popup.grab_set()  # Modal

        tk.Label(popup, text="ADD NEW STUDENT", font=("Helvetica", 40, "bold"), bg="white", fg="#1e293b").pack(pady=60)

        # Auto ID
        student_id = get_next_id()
        tk.Label(popup, text=f"Student ID: {student_id}", font=("Helvetica", 28, "bold"), bg="white", fg="#00d4aa").pack(pady=20)

        # Form fields
        labels = ["Name", "Surname", "Email (optional)", "English Grade", "History Grade", "Math Grade", "Science Grade", "Art Grade", "Password (for login)"]
        entries = {}

        for label in labels:
            row = tk.Frame(popup, bg="white")
            row.pack(fill="x", padx=150, pady=18)
            tk.Label(row, text=label + ":", font=("Helvetica", 20), bg="white", width=22, anchor="w").pack(side="left")
            entry = tk.Entry(row, font=("Helvetica", 22), bg="#f8fafc", relief="flat", highlightthickness=2, highlightcolor="#00d4aa")
            entry.pack(side="right", fill="x", expand=True, ipady=14)
            entries[label] = entry

        def save_student():
            name = entries["Name"].get().strip()
            surname = entries["Surname"].get().strip()
            pwd = entries["Password (for login)"].get().strip()
            if not name or not surname or not pwd:
                return messagebox.showerror("Error", "Name, Surname, and Password are required!")

            try:
                grades = [float(entries[f"{s} Grade"].get() or 0) for s in ["English","History","Math","Science","Art"]]
            except:
                return messagebox.showerror("Error", "Grades must be numbers!")

            # Save to DB
            conn = sqlite3.connect(DB_NAME)
            conn.execute('''INSERT INTO students 
                (id, name, surname, email, english, history, math, science, art, added_date)
                VALUES (?,?,?,?,?,?,?,?,?,?)''',
                (student_id, name, surname, entries["Email (optional)"].get(),
                 *grades, datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
            conn.close()

            conn = sqlite3.connect(USERS_DB)
            conn.execute("INSERT INTO users VALUES (?,?, 'student')", (student_id, hash_pwd(pwd)))
            conn.commit()
            conn.close()

            messagebox.showinfo("SUCCESS", f"Student added!\n\n{name} {surname}\nID: {student_id}\nPassword: {pwd}")
            popup.destroy()
            self.show_all_students()
            self.show_update_grades_tab()

        tk.Button(popup, text="ADD STUDENT", font=("Helvetica", 26, "bold"), bg="#10b981", fg="white",
                  command=save_student, height=2, width=25).pack(pady=80)

    # ==================== ALL STUDENTS ====================
    def show_all_students(self):
        for widget in self.tab_list.winfo_children():
            widget.destroy()

        canvas = tk.Canvas(self.tab_list)
        scrollbar = ttk.Scrollbar(self.tab_list, command=canvas.yview)
        scrollframe = ttk.Frame(canvas)
        canvas.create_window((0,0), window=scrollframe, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        conn = sqlite3.connect(DB_NAME)
        students = conn.execute("SELECT id, name, surname, english, history, math, science, art FROM students").fetchall()
        conn.close()

        for s in students:
            sid, name, surname, e,h,m,sci,a = s
            avg = sum(filter(None,[e,h,m,sci,a])) / len([x for x in [e,h,m,sci,a] if x]) if any([e,h,m,sci,a]) else 0
            card = tk.Frame(scrollframe, bg="white", relief="solid", bd=2, pady=30, padx=60)
            card.pack(fill="x", pady=18, padx=100)
            tk.Label(card, text=f"{name} {surname}", font=("Helvetica", 28, "bold"), bg="white").pack(anchor="w")
            tk.Label(card, text=f"ID: {sid} | Average: {avg:.1f}", font=("Helvetica", 20), bg="white", fg="#475569").pack(anchor="w")
            tk.Label(card, text=f"Eng:{e} Hist:{h} Math:{m} Sci:{sci} Art:{a}", font=("Helvetica", 22), bg="white").pack(pady=10)

    # ==================== UPDATE GRADES TAB ====================
    def show_update_grades_tab(self):
        for widget in self.tab_grades.winfo_children():
            widget.destroy()

        tk.Label(self.tab_grades, text="UPDATE STUDENT GRADES", font=("Helvetica", 38, "bold")).pack(pady=50)

        canvas = tk.Canvas(self.tab_grades)
        scrollbar = ttk.Scrollbar(self.tab_grades, command=canvas.yview)
        frame = ttk.Frame(canvas)
        canvas.create_window((0,0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=80)
        scrollbar.pack(side="right", fill="y")

        conn = sqlite3.connect(DB_NAME)
        students = conn.execute("SELECT id, name, surname, english, history, math, science, art FROM students").fetchall()
        conn.close()

        for s in students:
            sid, name, surname, e,h,m,sci,a = s
            avg = sum(filter(None,[e,h,m,sci,a])) / len([x for x in [e,h,m,sci,a] if x]) if any([e,h,m,sci,a]) else 0
            card = tk.Frame(frame, bg="white", relief="solid", bd=2, pady=35, padx=70)
            card.pack(fill="x", pady=20, padx=120)
            tk.Label(card, text=f"{name} {surname}", font=("Helvetica", 28, "bold"), bg="white").pack(anchor="w")
            tk.Label(card, text=f"ID: {sid} | Avg: {avg:.1f}", font=("Helvetica", 20), bg="white", fg="#475569").pack(anchor="w")
            tk.Label(card, text=f"Eng:{e} Hist:{h} Math:{m} Sci:{sci} Art:{a}", font=("Helvetica", 22), bg="white").pack(pady=10)
            tk.Button(card, text="UPDATE GRADES", font=("Helvetica", 18, "bold"), bg="#3b82f6", fg="white",
                      command=lambda sid=sid: self.open_grade_editor(sid)).pack(pady=10)

    def open_grade_editor(self, sid):
        # Same as before — grade editor popup
        conn = sqlite3.connect(DB_NAME)
        data = conn.execute("SELECT name, surname, english, history, math, science, art FROM students WHERE id=?", (sid,)).fetchone()
        conn.close()
        name, surname, e,h,m,sci,a = data

        win = tk.Toplevel(self.root)
        win.title("Update Grades")
        win.geometry("700x800")
        win.configure(bg="white")

        tk.Label(win, text=f"Update Grades\n{name} {surname}", font=("Helvetica", 34, "bold"), bg="white").pack(pady=60)
        tk.Label(win, text=f"ID: {sid}", font=("Helvetica", 22), bg="white", fg="#00d4aa").pack(pady=20)

        subjects = ["English", "History", "Math", "Science", "Art"]
        current = [e,h,m,sci,a]
        entries = {}

        for subj, val in zip(subjects, current):
            f = tk.Frame(win, bg="white")
            f.pack(pady=22)
            tk.Label(f, text=f"{subj}:", font=("Helvetica", 24), bg="white").pack(side="left", padx=40)
            ent = tk.Entry(f, font=("Helvetica", 30), width=8, justify="center")
            ent.insert(0, val if val else "")
            ent.pack(side="right")
            entries[subj] = ent

        def save():
            try:
                grades = [float(entries[s].get()) if entries[s].get().strip() else None for s in subjects]
            except:
                messagebox.showerror("Error", "Grades must be numbers!")
                return
            conn = sqlite3.connect(DB_NAME)
            conn.execute("UPDATE students SET english=?, history=?, math=?, science=?, art=? WHERE id=?", (*grades, sid))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Grades updated!")
            win.destroy()
            self.show_update_grades_tab()
            self.show_all_students()

        tk.Button(win, text="SAVE", font=("Helvetica", 26, "bold"), bg="#10b981", fg="white", command=save, height=2, width=20).pack(pady=80)

    # ==================== STUDENT VIEW ====================
    def show_student_grades(self, tab):
        conn = sqlite3.connect(DB_NAME)
        s = conn.execute("SELECT name, surname, english, history, math, science, art FROM students WHERE id=?", (self.username,)).fetchone()
        conn.close()

        if not s:
            tk.Label(tab, text="Not in class yet.\nAsk your teacher.", font=("Helvetica", 40), fg="red").pack(expand=True)
            return

        name, surname, e,h,m,sci,a = s
        grades = [x for x in [e,h,m,sci,a] if x]
        avg = sum(grades)/len(grades) if grades else 0
        color = "#10b981" if avg >= 90 else "#3b82f6" if avg >= 80 else "#f59e0b" if avg >= 70 else "#ef4444"

        f = tk.Frame(tab, bg="white")
        f.pack(fill="both", expand=True, padx=200, pady=150)
        tk.Label(f, text=f"{name} {surname}", font=("Helvetica", 44, "bold"), bg="white").pack(pady=80)
        tk.Label(f, text=f"{avg:.1f}/100", font=("Helvetica", 120, "bold"), bg="white", fg=color).pack(pady=60)
        tk.Label(f, text=f"English: {e} | History: {h} | Math: {m} | Science: {sci} | Art: {a}",
                 font=("Helvetica", 30), bg="white", fg="#475569").pack(pady=60)

# ==================== LOGIN ====================
class WelcomeApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Student Manager Pro")
        self.root.geometry("600x800")
        self.root.configure(bg="#0f172a")
        self.root.eval('tk::PlaceWindow . center')

        tk.Label(self.root, text="STUDENT MANAGER PRO", font=("Helvetica", 40, "bold"), bg="#0f172a", fg="#00d4aa").pack(pady=120)
        tk.Label(self.root, text="Admin → admin / admin", font=("Helvetica", 18), bg="#0f172a", fg="#94a3b8").pack(pady=20)

        card = tk.Frame(self.root, bg="white", padx=100, pady=120)
        card.pack(padx=100, fill="both", expand=True)

        tk.Label(card, text="Student ID", font=("Helvetica", 22), bg="white").pack(pady=30)
        self.id_entry = tk.Entry(card, font=("Helvetica", 26), justify="center")
        self.id_entry.pack(pady=15, ipady=20, fill="x")

        tk.Label(card, text="Password", font=("Helvetica", 22), bg="white").pack(pady=30)
        self.pwd_entry = tk.Entry(card, font=("Helvetica", 26), show="*", justify="center")
        self.pwd_entry.pack(pady=15, ipady=20, fill="x")

        tk.Button(card, text="LOGIN", bg="#00d4aa", fg="black", font=("Helvetica", 24, "bold"),
                  width=20, height=2, command=self.login).pack(pady=100)

        self.root.bind('<Return>', lambda e: self.login())
        self.root.mainloop()

    def login(self):
        uid = self.id_entry.get().strip()
        pwd = self.pwd_entry.get().strip()
        if not uid or not pwd:
            return messagebox.showerror("Error", "Fill both fields")

        conn = sqlite3.connect(USERS_DB)
        user = conn.execute("SELECT role FROM users WHERE username=? AND password=?", (uid, hash_pwd(pwd))).fetchone()
        conn.close()

        if user:
            self.root.destroy()
            StudentManagerApp(uid, user[0])
        else:
            messagebox.showerror("Failed", "Wrong ID or Password")

# ==================== START ====================
if __name__ == "__main__":
    init_databases()
    WelcomeApp()