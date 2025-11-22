# dbeaver.py  ← Save exactly this name in your project folder
# Professional Database Viewer — ONE FILE, works instantly!

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os

DB_STUDENTS = "students.db"
DB_USERS = "users.db"

class DBViewer:
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

        tk.Label(control_frame, text="Select Database:", font=("Helvetica", 18), bg="#1e293b", fg="white").pack(side="left", padx=20)
        self.db_var = tk.StringVar(value=DB_STUDENTS)
        combo = ttk.Combobox(control_frame, textvariable=self.db_var,
                             values=[DB_STUDENTS, DB_USERS], state="readonly", font=("Helvetica", 16), width=20)
        combo.pack(side="left", padx=10)

        tk.Button(control_frame, text="Refresh", bg="#3b82f6", fg="white",
                  font=("Helvetica", 16, "bold"), command=self.load_data, padx=30, pady=12).pack(side="left", padx=30)

        # Treeview
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill="both", expand=True, padx=50, pady=20)

        self.tree = ttk.Treeview(tree_frame, show="headings", height=22)
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Style
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Helvetica", 14, "bold"), background="#0f172a", foreground="white")
        style.configure("Treeview", font=("Helvetica", 12), rowheight=40)

        # Footer
        tk.Label(self.root, text="students.db → Student records | users.db → Login credentials",
                 font=("Helvetica", 13), bg="#1e293b", fg="#94a3b8").pack(pady=20)

        self.load_data()
        self.root.mainloop()

    def load_data(self):
        db_name = self.db_var.get()
        if not os.path.exists(db_name):
            messagebox.showwarning("Not Found", f"{db_name} not found!\nRun your main app first to create it.")
            self.tree["columns"] = ()
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.root.title("DB Viewer - No Database")
            return

        try:
            conn = sqlite3.connect(db_name)
            cur = conn.cursor()
            cur.execute("SELECT * FROM students" if db_name == DB_STUDENTS else "SELECT * FROM users")
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            conn.close()

            # Setup columns
            self.tree["columns"] = columns
            for col in columns:
                self.tree.heading(col, text=col.title())
                self.tree.column(col, width=180, anchor="center")

            # Clear & insert data
            for item in self.tree.get_children():
                self.tree.delete(item)
            for row in rows:
                self.tree.insert("", "end", values=row)

            self.root.title(f"DB Viewer • {db_name} ({len(rows)} records)")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data:\n{e}")

# === RUN IT ===
if __name__ == "__main__":
    DBViewer()