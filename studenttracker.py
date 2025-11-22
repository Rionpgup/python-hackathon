# modern_student_tracker.py - ULTRA MODERN GREEN UI 2025
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

class ModernStudentTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Tracker 2025")
        self.root.geometry("1200x750")
        self.root.configure(bg="#121212")  # Dark modern background
        self.root.state('zoomed')  # Fullscreen modern feel (optional)

        # Modern Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background="#1e1e1e", foreground="white",
                        rowheight=60, fieldbackground="#1e1e1e", font=("Segoe UI", 11))
        style.configure("Treeview.Heading", background="#0d3311", foreground="white",
                        font=("Segoe UI", 12, "bold"))
        style.map("Treeview", background=[('selected', '#2e7d32')])
        style.map("Treeview.Heading", background=[('active', '#1b5e20')])

        # Title
        title_frame = tk.Frame(root, bg="#121212")
        title_frame.pack(pady=30)
        tk.Label(title_frame, text="STUDENT TRACKER", font=("Montserrat", 36, "bold"),
                 bg="#121212", fg="#4caf50").pack()
        tk.Label(title_frame, text="Modern • Fast • Beautiful", font=("Segoe UI", 14),
                 bg="#121212", fg="#81c784").pack()

        # Buttons
        btn_frame = tk.Frame(root, bg="#121212")
        btn_frame.pack(pady=20)

        add_btn = tk.Button(btn_frame, text="+ ADD STUDENT", font=("Segoe UI", 14, "bold"),
                           bg="#4caf50", fg="white", relief="flat", bd=0, padx=30, pady=15,
                           command=self.add_student, cursor="hand2")
        add_btn.pack(side=tk.LEFT, padx=15)
        self.add_hover(add_btn, "#66bb6a", "#4caf50")

        refresh_btn = tk.Button(btn_frame, text="Refresh", font=("Segoe UI", 14, "bold"),
                               bg="#2e7d32", fg="white", relief="flat", bd=0, padx=30, pady=15,
                               command=self.load_students, cursor="hand2")
        refresh_btn.pack(side=tk.LEFT, padx=15)
        self.add_hover(refresh_btn, "#388e3c", "#2e7d32")

        # Treeview with modern hover
        columns = ("ID", "Name", "Grade", "Email", "Added")
        self.tree = ttk.Treeview(root, columns=columns, show="headings", selectmode="browse")
        self.tree.pack(fill="both", expand=True, padx=50, pady=20)

        # Column config
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Student Name")
        self.tree.heading("Grade", text="Grade")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Added", text="Added On")

        self.tree.column("ID", width=120, anchor="center")
        self.tree.column("Name", width=280, anchor="w")
        self.tree.column("Grade", width=150, anchor="center")
        self.tree.column("Email", width=300, anchor="w")
        self.tree.column("Added", width=180, anchor="center")

        # Tags for hover effect
        self.tree.tag_configure("oddrow", background="#1e1e1e")
        self.tree.tag_configure("evenrow", background="#252525")
        self.tree.tag_configure("hover", background="#2d2d2d")

        # Bind hover
        self.tree.bind("<Motion>", self.on_hover)
        self.tree.bind("<Leave>", self.on_leave)
        self.tree.bind("<Button-3>", self.show_context_menu)

        # Context menu
        self.menu = tk.Menu(root, tearoff=0, bg="#1e1e1e", fg="white", font=("Segoe UI", 10))
        self.menu.add_command(label="Edit Student", command=self.edit_student)
        self.menu.add_command(label="Delete Student", command=self.delete_student)

        # Status bar
        self.status = tk.Label(root, text="Ready • Modern Design Active", bg="#0d3311", fg="#81c784",
                               font=("Segoe UI", 11), anchor="w", padx=20)
        self.status.pack(fill="x", side="bottom", pady=0)

        self.current_hover = None
        self.load_students()

    def add_hover(self, widget, color_on_hover, color_on_leave):
        widget.bind("<Enter>", lambda e: widget.config(bg=color_on_hover))
        widget.bind("<Leave>", lambda e: widget.config(bg=color_on_leave))

    def on_hover(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id and row_id != self.current_hover:
            if self.current_hover:
                self.tree.detach(self.current_hover)
                self.tree.set(self.current_hover, "Grade", self.original_grade)
            self.current_hover = row_id
            # Apply hover style
            self.tree.item(row_id, tags=("hover",))
            # Highlight grade with badge effect
            values = self.tree.item(row_id, "values")
            grade = values[2] if values[2] != "N/A" else "—"
            self.original_grade = grade
            if grade != "—":
                self.tree.set(row_id, "Grade", f"{grade}")

    def on_leave(self, event):
        if self.current_hover:
            self.tree.item(self.current_hover, tags=("oddrow", "evenrow"))
            self.current_hover = None

    def load_students(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, grade, email, added_date FROM students ORDER BY name")
        rows = cursor.fetchall()
        conn.close()

        for idx, row in enumerate(rows):
            grade = f"{row[2]:.1f}" if row[2] else "N/A"
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=(row[0], row[1], grade, row[3] or "—", row[4]), tags=(tag,))

        self.status.config(text=f"Total Students: {len(rows)} • Hover for magic!")

    def show_context_menu(self, event):
        try:
            self.tree.selection_set(self.tree.identify_row(event.y))
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def add_student(self):
        self.show_form("Add New Student")

    def edit_student(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select a student!")
            return
        values = self.tree.item(sel[0])["values"]
        self.show_form("Edit Student", values)

    def delete_student(self):
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0])["values"]
        if messagebox.askyesno("Delete", f"Permanently delete\n{values[1]} (ID: {values[0]})?"):
            conn = sqlite3.connect(DB_NAME)
            conn.execute("DELETE FROM students WHERE id = ?", (values[0],))
            conn.commit()
            conn.close()
            messagebox.showinfo("Deleted", "Student removed successfully!")
            self.load_students()

    def show_form(self, title, data=None):
        form = tk.Toplevel(self.root)
        form.title(title)
        form.geometry("480x580")
        form.configure(bg="#121212")
        form.resizable(False, False)
        form.grab_set()

        tk.Label(form, text=title, font=("Montserrat", 20, "bold"), bg="#121212", fg="#4caf50").pack(pady=30)

        entries = {}
        fields = ["Student ID", "Full Name", "Grade (e.g. 95.5)", "Email (optional)"]
        for field in fields:
            tk.Label(form, text=field, font=("Segoe UI", 11), bg="#121212", fg="#81c784").pack(anchor="w", padx=60, pady=(20,5))
            entry = tk.Entry(form, font=("Segoe UI", 14), bg="#1e1e1e", fg="white", insertbackground="white",
                            relief="flat", bd=8, highlightthickness=2, highlightcolor="#4caf50")
            entry.pack(padx=60, fill="x", pady=5)
            entries[field] = entry

        if data:
            entries["Student ID"].insert(0, data[0])
            entries["Student ID"].config(state="disabled", disabledbackground="#333", disabledforeground="#aaa")
            entries["Full Name"].insert(0, data[1])
            entries["Grade (e.g. 95.5)"].insert(0, data[2] if data[2] != "N/A" else "")
            entries["Email (optional)"].insert(0, data[3] if data[3] != "—" else "")

        def save():
            sid = entries["Student ID"].get().strip()
            name = entries["Full Name"].get().strip()
            grade = entries["Grade (e.g. 95.5)"].get().strip()
            email = entries["Email (optional)"].get().strip()

            if not sid or not name:
                messagebox.showerror("Error", "ID and Name required!")
                return

            conn = sqlite3.connect(DB_NAME)
            try:
                if data:
                    old_grade = data[2] if data[2] != "N/A" else None
                    conn.execute("UPDATE students SET name=?, grade=?, email=? WHERE id=?",
                                (name, float(grade) if grade else None, email or None, sid))
                    change = self.calculate_change(old_grade, grade)
                    messagebox.showinfo("Success", f"Updated!\n{change}")
                else:
                    conn.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?)",
                                (sid, name, float(grade) if grade else None, email or None,
                                 datetime.now().strftime("%Y-%m-%d %H:%M")))
                    messagebox.showinfo("Success", f"Student '{name}' added!")
                conn.commit()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "ID already exists!")
            except ValueError:
                messagebox.showerror("Error", "Grade must be a number!")
            finally:
                conn.close()
                form.destroy()
                self.load_students()

        save_btn = tk.Button(form, text="SAVE STUDENT", font=("Segoe UI", 14, "bold"),
                            bg="#4caf50", fg="white", command=save, relief="flat", pady=15)
        save_btn.pack(fill="x", padx=60, pady=40)
        self.add_hover(save_btn, "#66bb6a", "#4caf50")

    def calculate_change(self, old, new):
        if not new:
            return "Grade cleared"
        try:
            old_val = float(old) if old else 0
            new_val = float(new)
            if old_val == 0:
                return f"First grade set: {new_val}"
            change = new_val - old_val
            percent = (change / old_val) * 100
            if change > 0:
                return f"UPGRADE +{change:.1f} (+{percent:+.1f}%)"
            elif change < 0:
                return f"DOWNGRADE {change:.1f} ({percent:+.1f}%)"
            else:
                return "No change"
        except:
            return "Grade updated"

# ============================
# LAUNCH MODERN APP
# ============================
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = ModernStudentTracker(root)
    root.mainloop()