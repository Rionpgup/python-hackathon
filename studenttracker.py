# teacher_dashboard_2025.py - THE ULTIMATE GREEN TEACHER DASHBOARD
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import math

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


class TeacherDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Teacher Dashboard 2025")
        self.root.geometry("1400x900")
        self.root.configure(bg="#0f0f0f")
        self.root.state('zoomed')

        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background="#1a1a1a", foreground="#e0e0e0",
                        fieldbackground="#1a1a1a", rowheight=50, font=("Segoe UI", 11))
        style.configure("Treeview.Heading", background="#1b5e20", foreground="white", font=("Segoe UI", 12, "bold"))
        style.map("Treeview", background=[('selected', '#2e7d32')])

        # Header
        header = tk.Frame(root, bg="#1b5e20", height=100)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="TEACHER DASHBOARD", font=("Montserrat", 32, "bold"),
                 bg="#1b5e20", fg="#c8e6c9").pack(side="left", padx=40, pady=20)
        tk.Label(header, text=f"{datetime.now().strftime('%A, %B %d, %Y')}",
                 font=("Segoe UI", 14), bg="#1b5e20", fg="#81c784").pack(side="right", padx=40, pady=30)

        # Main Content
        content = tk.Frame(root, bg="#0f0f0f")
        content.pack(fill="both", expand=True, padx=30, pady=20)

        # Stats Cards
        stats_frame = tk.Frame(content, bg="#0f0f0f")
        stats_frame.pack(fill="x", pady=20)

        self.stats = {
            "total": self.create_stat_card(stats_frame, "Total Students", "0", "#4caf50"),
            "average": self.create_stat_card(stats_frame, "Average Grade", "0.0", "#66bb6a"),
            "top": self.create_stat_card(stats_frame, "Top Performer", "None", "#81c784"),
            "lowest": self.create_stat_card(stats_frame, "Lowest Grade", "N/A", "#43a047")
        }
        for widget in stats_frame.winfo_children():
            widget.pack(side="left", expand=True, fill="x", padx=15)

        # Chart + Recent Activity
        middle = tk.Frame(content, bg="#0f0f0f")
        middle.pack(fill="both", expand=True)

        # Grade Distribution Chart
        chart_frame = tk.LabelFrame(middle, text=" Grade Distribution ", font=("Segoe UI", 14, "bold"),
                                    bg="#1e1e1e", fg="#81c784", bd=2, relief="flat")
        chart_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))
        self.canvas = tk.Canvas(chart_frame, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=20, pady=20)

        # Recent Students Table
        recent_frame = tk.LabelFrame(middle, text=" Recent Students ", font=("Segoe UI", 14, "bold"),
                                     bg="#1e1e1e", fg="#81c784")
        recent_frame.pack(side="right", fill="both", expand=True)

        columns = ("ID", "Name", "Grade", "Added")
        self.recent_tree = ttk.Treeview(recent_frame, columns=columns, show="headings", height=10)
        for col in columns:
            self.recent_tree.heading(col, text=col)
            self.recent_tree.column(col, width=120, anchor="center")
        self.recent_tree.column("Name", width=180)
        self.recent_tree.pack(fill="both", expand=True, padx=20, pady=20)

        # Quick Actions
        actions = tk.Frame(content, bg="#0f0f0f")
        actions.pack(pady=30)

        tk.Button(actions, text="ADD STUDENT", font=("Segoe UI", 16, "bold"), bg="#4caf50", fg="white",
                  command=self.add_student, width=20, height=2, relief="flat").pack(side="left", padx=20)
        tk.Button(actions, text="VIEW ALL STUDENTS", font=("Segoe UI", 16, "bold"), bg="#2e7d32", fg="white",
                  command=self.open_full_list, width=20, height=2, relief="flat").pack(side="left", padx=20)
        tk.Button(actions, text="REFRESH DASHBOARD", font=("Segoe UI", 16, "bold"), bg="#1b5e20", fg="white",
                  command=self.refresh_all, width=20, height=2, relief="flat").pack(side="left", padx=20)

        self.refresh_all()

    def create_stat_card(self, parent, title, value, color):
        frame = tk.Frame(parent, bg="#1e1e1e", relief="flat", bd=3)
        frame.pack_propagate(False)
        frame.configure(height=150)

        tk.Label(frame, text=title, font=("Segoe UI", 14), bg="#1e1e1e", fg="#81c784").pack(pady=20)
        val_label = tk.Label(frame, text=value, font=("Montserrat", 28, "bold"), bg="#1e1e1e", fg=color)
        val_label.pack()
        return val_label

    def refresh_all(self):
        self.update_stats()
        self.draw_chart()
        self.load_recent()

    def update_stats(self):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*), AVG(grade), MAX(grade), MIN(grade) FROM students")
        total, avg, max_g, min_g = cur.fetchone()

        cur.execute("SELECT name FROM students WHERE grade = ?", (max_g,))
        top_name = cur.fetchone()
        top_name = top_name[0] if top_name else "None"

        conn.close()

        self.stats["total"].config(text=str(total or 0))
        self.stats["average"].config(text=f"{avg:.1f}" if avg else "0.0")
        self.stats["top"].config(text=f"{top_name}\n({max_g or 0})")
        self.stats["lowest"].config(text=str(min_g or "N/A"))

    def draw_chart(self):
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width < 100 or height < 100:
            self.root.after(100, self.draw_chart)
            return

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT grade FROM students WHERE grade IS NOT NULL")
        grades = [row[0] for row in cur.fetchall()]
        conn.close()

        if not grades:
            self.canvas.create_text(width // 2, height // 2, text="No grades yet!", fill="#666", font=("Segoe UI", 20))
            return

        # Grade ranges
        ranges = [(90, 100), (80, 89), (70, 79), (60, 69), (0, 59)]
        labels = ["A (90-100)", "B (80-89)", "C (70-79)", "D (60-69)", "F (<60)"]
        colors = ["#4caf50", "#66bb6a", "#81c784", "#a5d6a7", "#c8e6c9"]
        counts = [sum(1 for g in grades if low <= g <= high) for low, high in ranges]
        max_count = max(counts) if counts else 1

        bar_width = (width - 100) // len(counts)
        start_x = 50

        for i, (count, label, color) in enumerate(zip(counts, labels, colors)):
            x0 = start_x + i * bar_width
            x1 = x0 + bar_width - 20
            y0 = height - 80
            y1 = y0 - (count / max_count) * (height - 150) if max_count > 0 else y0

            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="#333")
            self.canvas.create_text((x0 + x1) // 2, y1 - 20, text=str(count), fill="white", font=("bold", 16))
            self.canvas.create_text((x0 + x1) // 2, height - 50, text=label, fill="#81c784", angle=15,
                                    font=("Segoe UI", 10))

    def load_recent(self):
        for i in self.recent_tree.get_children():
            self.recent_tree.delete(i)
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT id, name, grade, added_date FROM students ORDER BY added_date DESC LIMIT 8")
        for row in cur.fetchall():
            grade = f"{row[2]:.1f}" if row[2] else "N/A"
            self.recent_tree.insert("", "end", values=(row[0], row[1], grade, row[3]))
        conn.close()

    def add_student(self):
        # Reuse your previous add form (simplified here)
        self.show_add_form()

    def show_add_form(self):
        form = tk.Toplevel(self.root)
        form.title("Add Student")
        form.geometry("500x600")
        form.configure(bg="#0f0f0f")

        entries = {}
        fields = ["Student ID", "Full Name", "Grade", "Email"]
        for field in fields:
            tk.Label(form, text=field, font=("Segoe UI", 14), bg="#0f0f0f", fg="#81c784").pack(pady=10)
            e = tk.Entry(form, font=("Segoe UI", 14), bg="#1e1e1e", fg="white", insertbackground="white")
            e.pack(pady=5, padx=50, fill="x")
            entries[field] = e

        def save():
            data = {k: v.get().strip() for k, v in entries.items()}
            if not data["Student ID"] or not data["Full Name"]:
                messagebox.showerror("Error", "ID and Name required!")
                return
            try:
                conn = sqlite3.connect(DB_NAME)
                conn.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?)",
                             (data["Student ID"], data["Full Name"],
                              float(data["Grade"]) if data["Grade"] else None,
                              data["Email"] or None, datetime.now().strftime("%Y-%m-%d %H:%M")))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Student added!")
                form.destroy()
                self.refresh_all()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "ID already exists!")
            except ValueError:
                messagebox.showerror("Error", "Invalid grade!")

        tk.Button(form, text="SAVE", font=("bold", 16), bg="#4caf50", fg="white",
                  command=save, pady=15).pack(pady=40, fill="x", padx=50)

    def open_full_list(self):
        # Open full student list in new window
        FullListWindow(self.root)

    def refresh_all(self):
        self.update_stats()
        self.draw_chart()
        self.load_recent()


class FullListWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("All Students")
        self.window.geometry("1200x800")
        self.window.configure(bg="#0f0f0f")

        # Add your full treeview from previous version here
        tk.Label(self.window, text="Full Student List Coming Soon!",
                 font=("Segoe UI", 24), bg="#0f0f0f", fg="#81c784").pack(expand=True)


# ============================
# LAUNCH THE DASHBOARD
# ============================
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = TeacherDashboard(root)
    root.mainloop()