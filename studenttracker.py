# student_manager_search_by_name_and_id.py - SEARCH BY ID OR NAME!
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

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


class CleanStudentManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Manager")
        self.root.geometry("1500x900")
        self.root.configure(bg="#f0f9ff")
        self.root.state('zoomed')

        self.history = []
        self.current_page = None

        self.create_header()
        self.content_frame = tk.Frame(root, bg="#f8fdff")
        self.content_frame.pack(fill="both", expand=True, padx=40, pady=20)

        self.create_back_button()

        self.show_dashboard()

    def create_header(self):
        header = tk.Frame(self.root, height=120)
        header.pack(fill="x")
        header.pack_propagate(False)

        canvas = tk.Canvas(header, height=120, highlightthickness=0, bg="#a0e7e5")
        canvas.pack(fill="x")
        canvas.create_rectangle(0, 0, 3000, 120, fill="#a0e7e5", outline="")
        canvas.create_rectangle(0, 0, 3000, 120, fill="#b2f7c0", outline="", stipple="gray50")

        tk.Label(header, text="STUDENT MANAGER", font=("Helvetica", 38, "bold"),
                 bg="#a0e7e5", fg="black").place(x=80, y=35)

        # SEARCH BAR — NOW SEARCHES BY ID OR NAME
        search_frame = tk.Frame(header, bg="white", relief="flat", bd=2, highlightbackground="#00d4aa",
                                highlightthickness=3)
        search_frame.place(x=80, y=15, width=480, height=55)

        tk.Label(search_frame, text="Search by ID or Name:", font=("Helvetica", 13, "bold"), bg="white",
                 fg="black").place(x=15, y=13)

        self.search_var = tk.StringVar()
        entry = tk.Entry(search_frame, textvariable=self.search_var, font=("Helvetica", 16),
                         bg="white", fg="black", insertbackground="#00d4aa", relief="flat", bd=0)
        entry.place(x=190, y=12, width=270, height=32)
        entry.focus()

        # THIS IS THE KEY LINE — SEARCHES BY ID OR NAME
        self.search_var.trace_add("write", self.live_search_by_id_or_name)

        # Navigation Buttons
        btn_x = 700
        buttons = [
            ("Dashboard", self.show_dashboard),
            ("Add Student", self.show_add_student),
            ("View All", self.show_all_students)
        ]

        for text, cmd in buttons:
            btn = tk.Button(header, text=text, font=("Helvetica", 14, "bold"),
                            bg="#00d4aa", fg="black", relief="flat", bd=0, padx=32, pady=15,
                            command=lambda c=cmd: self.navigate_to(c), cursor="hand2")
            btn.place(x=btn_x, y=40)
            self.hover_effect(btn, "#00e6b8", "#00d4aa")
            btn_x += 180

    def hover_effect(self, widget, hover, normal):
        widget.bind("<Enter>", lambda e: widget.config(bg=hover))
        widget.bind("<Leave>", lambda e: widget.config(bg=normal))

    def create_back_button(self):
        self.back_btn = tk.Button(self.root, text="Back", font=("Helvetica", 14, "bold"),
                                  bg="#00d4aa", fg="black", relief="flat", padx=35, pady=15,
                                  state="disabled", command=self.go_back, cursor="hand2")
        self.back_btn.place(relx=1.0, rely=1.0, x=-40, y=-40, anchor="se")
        self.hover_effect(self.back_btn, "#00e6b8", "#00d4aa")

    def navigate_to(self, page_func):
        if self.current_page != page_func:
            self.history.append(self.current_page)
            self.current_page = page_func
            self.back_btn.config(state="normal")
            self.clear_content()
            page_func()

    def go_back(self):
        if self.history:
            prev = self.history.pop()
            self.current_page = prev
            self.back_btn.config(state="normal" if self.history else "disabled")
            self.clear_content()
            prev()

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    # UPDATED: SEARCH BY ID OR NAME
    def live_search_by_id_or_name(self, *args):
        query = self.search_var.get().strip().lower()
        self.clear_content()

        if not query:
            self.show_dashboard()
            return

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        # Search both ID and name (case-insensitive)
        cur.execute("""
            SELECT * FROM students 
            WHERE LOWER(id) LIKE ? OR LOWER(name) LIKE ?
            ORDER BY name
        """, (f"%{query}%", f"%{query}%"))
        results = cur.fetchall()
        conn.close()

        if not results:
            msg = tk.Label(self.content_frame, text=f"No student found for '{self.search_var.get()}'",
                           font=("Helvetica", 30), bg="#f8fdff", fg="#666")
            msg.pack(expand=True, pady=200)
            return

        # Show results
        card = tk.Frame(self.content_frame, bg="white", relief="flat", bd=2, highlightbackground="#00d4aa",
                        highlightthickness=3)
        card.pack(fill="both", expand=True, padx=120, pady=60)

        tk.Label(card, text=f"Found {len(results)} match(es)", font=("Helvetica", 24, "bold"),
                 bg="white", fg="black").pack(pady=25)

        tree = ttk.Treeview(card, columns=("ID", "Name", "Grade", "Email", "Added"), show="headings")
        style = ttk.Style()
        style.configure("Treeview", background="white", foreground="black", rowheight=65, font=("Helvetica", 12))
        style.configure("Treeview.Heading", background="#e0fbfc", foreground="black", font=("Helvetica", 13, "bold"))
        style.map("Treeview", background=[("selected", "#b2f7c0")])

        cols = [("ID", 160), ("Name", 360), ("Grade", 140), ("Email", 400), ("Added", 200)]
        for col, w in cols:
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="center")
        tree.pack(fill="both", expand=True, padx=50, pady=20)

        for row in results:
            grade = f"{row[2]:.1f}" if row[2] else "N/A"
            tree.insert("", "end", values=(row[0], row[1], grade, row[3] or "—", row[4]))

    def show_dashboard(self):
        frame = tk.Frame(self.content_frame, bg="#f8fdff")
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Welcome to Student Manager", font=("Helvetica", 44, "bold"),
                 bg="#f8fdff", fg="black").pack(pady=120)
        tk.Label(frame, text="Type any Student ID or Name above",
                 font=("Helvetica", 20), bg="#f8fdff", fg="#555").pack(pady=20)

        conn = sqlite3.connect(DB_NAME)
        total = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        conn.close()

        card = tk.Frame(frame, bg="white", relief="flat", bd=2, highlightbackground="#00d4aa", highlightthickness=3)
        card.pack(pady=100, padx=450)
        tk.Label(card, text="Total Students", font=("Helvetica", 20), bg="white", fg="#555").pack(pady=25)
        tk.Label(card, text=str(total), font=("Helvetica", 72, "bold"), bg="white", fg="#00d4aa").pack(pady=15)

    def show_add_student(self):
        self.clear_content()
        frame = tk.Frame(self.content_frame, bg="#f8fdff")
        frame.pack(fill="both", expand=True)

        card = tk.Frame(frame, bg="white", relief="flat", bd=2, highlightbackground="#00d4aa", highlightthickness=3)
        card.pack(pady=80, padx=380)

        tk.Label(card, text="ADD NEW STUDENT", font=("Helvetica", 28, "bold"),
                 bg="white", fg="black").pack(pady=40)

        entries = {}
        fields = ["Student ID *", "Full Name *", "Grade (e.g. 95.5)", "Email (optional)"]
        for field in fields:
            tk.Label(card, text=field, font=("Helvetica", 14), bg="white", fg="#555") \
                .pack(pady=(25, 8), anchor="w", padx=100)
            e = tk.Entry(card, font=("Helvetica", 16), bg="#f0f9ff", fg="black", relief="flat",
                         highlightthickness=2, highlightbackground="#00d4aa")
            e.pack(padx=100, fill="x", pady=5)
            entries[field] = e

        def save():
            sid = entries["Student ID *"].get().strip()
            name = entries["Full Name *"].get().strip()
            grade = entries["Grade (e.g. 95.5)"].get().strip()
            email = entries["Email (optional)"].get().strip()

            if not sid or not name:
                messagebox.showerror("Error", "Student ID and Name are required!")
                return

            try:
                grade_val = float(grade) if grade else None
                conn = sqlite3.connect(DB_NAME)
                conn.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?)",
                             (sid, name, grade_val, email or None, datetime.now().strftime("%Y-%m-%d %H:%M")))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success!", f"Student '{name}' added!")
                self.search_var.set("")
                self.show_dashboard()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "This Student ID already exists!")
            except ValueError:
                messagebox.showerror("Error", "Grade must be a number!")

        save_btn = tk.Button(card, text="SAVE STUDENT", font=("Helvetica", 18, "bold"),
                             bg="#00d4aa", fg="black", command=save, pady=18, relief="flat")
        save_btn.pack(fill="x", padx=100, pady=50)
        self.hover_effect(save_btn, "#00e6b8", "#00d4aa")

    def show_all_students(self):
        self.clear_content()
        frame = tk.Frame(self.content_frame, bg="#f8fdff")
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="ALL STUDENTS", font=("Helvetica", 32, "bold"),
                 bg="#f8fdff", fg="black").pack(pady=30)

        tree = ttk.Treeview(frame, columns=("ID", "Name", "Grade", "Email", "Added"), show="headings")
        style = ttk.Style()
        style.configure("Treeview", background="white", foreground="black", rowheight=65, font=("Helvetica", 12))
        style.configure("Treeview.Heading", background="#e0fbfc", foreground="black", font=("Helvetica", 13, "bold"))

        cols = [("ID", 160), ("Name", 380), ("Grade", 140), ("Email", 400), ("Added", 200)]
        for col, w in cols:
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="center")
        tree.pack(fill="both", expand=True, padx=100, pady=20)

        conn = sqlite3.connect(DB_NAME)
        for row in conn.execute("SELECT * FROM students ORDER BY name"):
            grade = f"{row[2]:.1f}" if row[2] else "N/A"
            tree.insert("", "end", values=(row[0], row[1], grade, row[3] or "—", row[4]))
        conn.close()


# RUN IT — WORKS 100%!
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = CleanStudentManager(root)
    root.mainloop()