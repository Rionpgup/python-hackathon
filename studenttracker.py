# student_manager_with_photos.py - FULLY WORKING WITH STUDENT PHOTOS!
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
import os
from PIL import Image, ImageTk
import shutil

DB_NAME = "students.db"
PHOTO_DIR = "student_photos"
os.makedirs(PHOTO_DIR, exist_ok=True)  # Create folder for photos

def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            grade REAL,
            email TEXT,
            added_date TEXT,
            photo_path TEXT
        )
    ''')
    conn.commit()
    conn.close()

class StudentManagerWithPhotos:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Manager • With Photos")
        self.root.geometry("1600x950")
        self.root.configure(bg="#f0f9ff")
        self.root.state('zoomed')

        self.history = []
        self.current_page = None
        self.selected_photo = None  # For adding photo

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

        # Search bar
        search_frame = tk.Frame(header, bg="white", relief="flat", bd=2, highlightbackground="#00d4aa", highlightthickness=3)
        search_frame.place(x=80, y=15, width=500, height=55)

        tk.Label(search_frame, text="Search by ID or Name:", font=("Helvetica", 13, "bold"), bg="white", fg="black").place(x=15, y=13)
        self.search_var = tk.StringVar()
        entry = tk.Entry(search_frame, textvariable=self.search_var, font=("Helvetica", 16),
                        bg="white", fg="black", insertbackground="#00d4aa", relief="flat")
        entry.place(x=210, y=12, width=270, height=32)
        entry.focus()
        self.search_var.trace_add("write", self.live_search)

        # Nav buttons
        btn_x = 720
        for text, cmd in [("Dashboard", self.show_dashboard), ("Add Student", self.show_add_student), ("View All", self.show_all_students)]:
            btn = tk.Button(header, text=text, font=("Helvetica", 14, "bold"),
                           bg="#00d4aa", fg="black", relief="flat", padx=32, pady=15,
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

    def choose_photo(self):
        file_path = filedialog.askopenfilename(
            title="Select Student Photo",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if file_path:
            self.selected_photo = file_path
            messagebox.showinfo("Photo Selected", "Photo ready! Now save the student.")

    def live_search(self, *args):
        query = self.search_var.get().strip().lower()
        self.clear_content()

        if not query:
            self.show_dashboard()
            return

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM students WHERE LOWER(id) LIKE ? OR LOWER(name) LIKE ?", (f"%{query}%", f"%{query}%"))
        results = cur.fetchall()
        conn.close()

        if not results:
            tk.Label(self.content_frame, text=f"No student found for '{self.search_var.get()}'",
                     font=("Helvetica", 30), bg="#f8fdff", fg="#666").pack(expand=True, pady=200)
            return

        # Show results with photos
        for student in results:
            self.display_student_card(student)

    def display_student_card(self, student):
        card = tk.Frame(self.content_frame, bg="white", relief="flat", bd=2, highlightbackground="#00d4aa", highlightthickness=3)
        card.pack(fill="x", pady=15, padx=100)

        # Photo
        photo_frame = tk.Frame(card, bg="white", width=180, height=180)
        photo_frame.pack(side="left", padx=30, pady=30)
        photo_frame.pack_propagate(False)

        if student[5] and os.path.exists(student[5]):
            try:
                img = Image.open(student[5])
                img = img.resize((160, 160), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                label = tk.Label(photo_frame, image=photo, bg="white")
                label.image = photo
                label.pack(expand=True)
            except:
                tk.Label(photo_frame, text="No Photo", font=("Helvetica", 12), bg="white", fg="#aaa").pack(expand=True)
        else:
            tk.Label(photo_frame, text="No Photo", font=("Helvetica", 12), bg="white", fg="#aaa").pack(expand=True)

        # Info
        info_frame = tk.Frame(card, bg="white")
        info_frame.pack(side="left", fill="both", expand=True, padx=30, pady=40)

        tk.Label(info_frame, text=f"Name: {student[1]}", font=("Helvetica", 22, "bold"), bg="white", fg="black", anchor="w").pack(fill="x", pady=8)
        tk.Label(info_frame, text=f"ID: {student[0]}", font=("Helvetica", 16), bg="white", fg="#333", anchor="w").pack(fill="x", pady=5)
        tk.Label(info_frame, text=f"Grade: {student[2]:.1f}" if student[2] else "Grade: N/A", font=("Helvetica", 16), bg="white", fg="#333", anchor="w").pack(fill="x", pady=5)
        tk.Label(info_frame, text=f"Email: {student[3] or '—'}", font=("Helvetica", 16), bg="white", fg="#333", anchor="w").pack(fill="x", pady=5)
        tk.Label(info_frame, text=f"Added: {student[4]}", font=("Helvetica", 14), bg="white", fg="#666", anchor="w").pack(fill="x", pady=5)

    def show_dashboard(self):
        frame = tk.Frame(self.content_frame, bg="#f8fdff")
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Welcome to Student Manager", font=("Helvetica", 44, "bold"),
                bg="#f8fdff", fg="black").pack(pady=120)
        tk.Label(frame, text="Search by Name or ID above", font=("Helvetica", 20), bg="#f8fdff", fg="#555").pack(pady=20)

        conn = sqlite3.connect(DB_NAME)
        total = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        conn.close()

        card = tk.Frame(frame, bg="white", relief="flat", bd=2, highlightbackground="#00d4aa", highlightthickness=3)
        card.pack(pady=100, padx=500)
        tk.Label(card, text="Total Students", font=("Helvetica", 20), bg="white", fg="#555").pack(pady=25)
        tk.Label(card, text=str(total), font=("Helvetica", 72, "bold"), bg="white", fg="#00d4aa").pack(pady=15)

    def show_add_student(self):
        self.clear_content()
        frame = tk.Frame(self.content_frame, bg="#f8fdff")
        frame.pack(fill="both", expand=True)

        card = tk.Frame(frame, bg="white", relief="flat", bd=2, highlightbackground="#00d4aa", highlightthickness=3)
        card.pack(pady=60, padx=400)

        tk.Label(card, text="ADD NEW STUDENT", font=("Helvetica", 28, "bold"), bg="white", fg="black").pack(pady=40)

        entries = {}
        fields = ["Student ID *", "Full Name *", "Grade", "Email"]
        for field in fields:
            tk.Label(card, text=field, font=("Helvetica", 14), bg="white", fg="#555").pack(pady=(20,8), anchor="w", padx=100)
            e = tk.Entry(card, font=("Helvetica", 16), bg="#f0f9ff", fg="black")
            e.pack(padx=100, fill="x", pady=5)
            entries[field] = e

        # Photo section
        photo_frame = tk.Frame(card, bg="white")
        photo_frame.pack(pady=30)
        self.photo_label = tk.Label(photo_frame, text="No photo selected", font=("Helvetica", 14), bg="#f0f9ff", width=30, height=10)
        self.photo_label.pack(pady=10)

        tk.Button(photo_frame, text="Choose Photo", font=("Helvetica", 14, "bold"),
                  bg="#00d4aa", fg="black", command=self.choose_photo, pady=12).pack(pady=10)

        def save():
            sid = entries["Student ID *"].get().strip()
            name = entries["Full Name *"].get().strip()
            grade = entries["Grade"].get().strip()
            email = entries["Email"].get().strip()

            if not sid or not name:
                messagebox.showerror("Error", "ID and Name required!")
                return

            photo_path = None
            if self.selected_photo:
                ext = os.path.splitext(self.selected_photo)[1]
                photo_path = os.path.join(PHOTO_DIR, f"{sid}{ext}")
                shutil.copy(self.selected_photo, photo_path)

            try:
                grade_val = float(grade) if grade else None
                conn = sqlite3.connect(DB_NAME)
                conn.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?)",
                            (sid, name, grade_val, email or None, datetime.now().strftime("%Y-%m-%d %H:%M"), photo_path))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success!", f"Student '{name}' added with photo!")
                self.selected_photo = None
                self.search_var.set("")
                self.show_dashboard()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Student ID already exists!")

        tk.Button(card, text="SAVE STUDENT", font=("Helvetica", 18, "bold"),
                  bg="#00d4aa", fg="black", command=save, pady=18).pack(fill="x", padx=100, pady=40)
        self.hover_effect(card.winfo_children()[-1], "#00e6b8", "#00d4aa")

    def show_all_students(self):
        self.clear_content()
        frame = tk.Frame(self.content_frame, bg="#f8fdff")
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="ALL STUDENTS", font=("Helvetica", 32, "bold"), bg="#f8fdff", fg="black").pack(pady=30)

        conn = sqlite3.connect(DB_NAME)
        students = conn.execute("SELECT * FROM students ORDER BY name").fetchall()
        conn.close()

        for student in students:
            self.display_student_card(student)

# LAUNCH THE MASTERPIECE
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = StudentManagerWithPhotos(root)
    root.mainloop()