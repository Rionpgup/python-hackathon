# db_viewer/app.py
import tkinter as tk
from tkinter import ttk, messagebox
from .database import get_table_data, DB_STUDENTS, DB_USERS
from .widgets import setup_treeview

class DBViewerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DB Viewer - Student Manager Pro")
        self.root.geometry("1300x900")
        self.root.configure(bg="#1e293b")

        # Title
        tk.Label(self.root, text="DATABASE EXPLORER", font=("Helvetica", 36, "bold"),
                 bg="#1e293b", fg="#00d4aa").pack(pady=40)

        # Controls
        control_frame = tk.Frame(self.root, bg="#1e293b")
        control_frame.pack(pady=15)

        tk.Label(control_frame, text="Database:", font=("Helvetica", 18), bg="#1e293b", fg="white").pack(side="left", padx=20)
        self.db_var = tk.StringVar(value=DB_STUDENTS)
        db_combo = ttk.Combobox(control_frame, textvariable=self.db_var,
                                values=[DB_STUDENTS, DB_USERS], state="readonly", font=("Helvetica", 16), width=20)
        db_combo.pack(side="left", padx=10)

        tk.Button(control_frame, text="Refresh Data", bg="#3b82f6", fg="white",
                  font=("Helvetica", 16, "bold"), command=self.refresh, padx=30, pady=12).pack(side="left", padx=30)

        # Treeview
        self.tree = setup_treeview(self.root)

        # Footer
        footer = tk.Frame(self.root, bg="#1e293b")
        footer.pack(fill="x", pady=30)
        tk.Label(footer, text="students.db → Student records | users.db → Login credentials",
                 font=("Helvetica", 13), bg="#1e293b", fg="#94a3b8").pack()

        # Initial load
        self.refresh()

        self.root.mainloop()

    def refresh(self):
        try:
            db_name = self.db_var.get()
            columns, rows, count = get_table_data(db_name)

            # Clear & setup columns
            for col in self.tree["columns"]:
                self.tree.delete(col)
            self.tree["columns"] = columns

            for col in columns:
                self.tree.heading(col, text=col.title())
                self.tree.column(col, width=160, anchor="center")

            # Clear old data
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Insert new data
            for row in rows:
                self.tree.insert("", "end", values=row)

            self.root.title(f"DB Viewer • {db_name} ({count} records)")

        except Exception as e:
            messagebox.showerror("Database Error", str(e))