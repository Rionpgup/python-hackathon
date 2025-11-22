# student_manager_circular_photos.py - CIRCULAR PHOTOS + RANDOM DEFAULT + DASHBOARD PHOTO!
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
import os
import shutil
import random

DB_NAME = "students.db"
PHOTO_DIR = "student_photos"
DEFAULT_PHOTOS = "default_avatars"  # Put 5-10 cute avatar images here

os.makedirs(PHOTO_DIR, exist_ok=True)
os.makedirs(DEFAULT_PHOTOS, exist_ok=True)

# Try to import PIL (for circular mask & resize)
try:
    from PIL import Image, ImageTk, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Pillow not installed → using square photos (still works!)")

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

class StudentManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Manager • Circular Photos")
        self.root.geometry("1600x950")
        self.root.configure(bg="#f0f9ff")
        self.root.state('zoomed')

        self.history = []
        self.current_page = None
        self.selected_photo = None

        # Load default avatars
        self.default_photos = [f for f in os.listdir(DEFAULT_PHOTOS)
                              if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]

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

        search_frame = tk.Frame(header, bg="white", relief="flat", bd=2, highlightbackground="#00d4aa", highlightthickness=3)
        search_frame.place(x=80, y=15, width=500, height=55)
        tk.Label(search_frame, text="Search by ID or Name:", font=("Helvetica", 13, "bold"), bg="white", fg="black").place(x=15, y=13)
        self.search_var = tk.StringVar()
        entry = tk.Entry(search_frame, textvariable=self.search_var, font=("Helvetica", 16),
                        bg="white", fg="black", insertbackground="#00d4aa", relief="flat")
        entry.place(x=210, y=12, width=270, height=32)
        entry.focus()
        self.search_var.trace_add("write", self.live_search)

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
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])
        if file_path:
            self.selected_photo = file_path
            self.photo_preview.config(text=f"Selected: {os.path.basename(file_path)}", fg="#0066cc")

    def make_circular_photo(self, path, size=180):
        if not PIL_AVAILABLE or not path or not os.path.exists(path):
            return None
        try:
            img = Image.open(path).convert("RGBA")
            img = img.resize((size, size), Image.Resampling.LANCZOS)
            mask = Image.new("L", (size, size), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size, size), fill=255)
            circular = Image.composite(img, Image.new("RGBA", (size, size), (240,249,255,255)), mask)
            return ImageTk.PhotoImage(circular)
        except:
            return None

    def get_random_default_photo(self):
        if not self.default_photos:
            return None
        photo_name = random.choice(self.default_photos)
        return os.path.join(DEFAULT_PHOTOS, photo_name)

    def display_circular_photo(self, frame, photo_path=None):
        if not photo_path or not os.path.exists(photo_path):
            photo_path = self.get_random_default_photo()
        photo = self.make_circular_photo(photo_path)
        if photo:
            label = tk.Label(frame, image=photo, bg="#f8fdff", bd=0)
            label.image = photo
        else:
            # Fallback: simple circle with initial
            canvas = tk.Canvas(frame, width=180, height=180, bg="#f8fdff", highlightthickness=0)
            canvas.create_oval(10, 10, 170, 170, fill="#00d4aa", outline="#00a388", width=4)
            canvas.create_text(90, 90, text="?", font=("Helvetica", 60, "bold"), fill="white")
        canvas.pack() if 'canvas' in locals() else label.pack()

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
            tk.Label(self.content_frame, text="No student found", font=("Helvetica", 32), bg="#f8fdff", fg="#666").pack(expand=True, pady=200)
            return

        for student in results:
            card = tk.Frame(self.content_frame, bg="white", relief="flat", bd=2, highlightbackground="#00d4aa", highlightthickness=3)
            card.pack(fill="x", pady=20, padx=120)

            photo_frame = tk.Frame(card, bg="white", width=200, height=200)
            photo_frame.pack(side="left", padx=40, pady=30)
            photo_frame.pack_propagate(False)
            self.display_circular_photo(photo_frame, student[5])

            info = tk.Frame(card, bg="white")
            info.pack(side="left", fill="both", expand=True, padx=30, pady=40)
            tk.Label(info, text=student[1], font=("Helvetica", 26, "bold"), bg="white", fg="black", anchor="w").pack(fill="x", pady=8)
            tk.Label(info, text=f"ID: {student[0]}", font=("Helvetica", 16), bg="white", fg="#333", anchor="w").pack(fill="x")
            tk.Label(info, text=f"Grade: {student[2] or 'N/A'} | Email: {student[3] or '—'}", font=("Helvetica", 16), bg="white", fg="#333", anchor="w").pack(fill="x")
            tk.Label(info, text=f"Added: {student[4]}", font=("Helvetica", 14), bg="white", fg="#666", anchor="w").pack(fill="x", pady=10)

    def show_dashboard(self):
        frame = tk.Frame(self.content_frame, bg="#f8fdff")
        frame.pack(fill="both", expand=True)

        # Big welcome with random student photo
        top_frame = tk.Frame(frame, bg="#f8fdff")
        top_frame.pack(pady=80)

        photo_big = tk.Frame(top_frame, bg="#f8fdff", width=250, height=250)
        photo_big.pack()
        photo_big.pack_propagate(False)

        conn = sqlite3.connect(DB_NAME)
        students = conn.execute("SELECT * FROM students ORDER BY RANDOM() LIMIT 1").fetchone()
        conn.close()

        if students:
            self.display_circular_photo(photo_big, students[5])
            name = students[1]
        else:
            # No students yet → show default
            self.display_circular_photo(photo_big, self.get_random_default_photo())
            name = "No students yet"

        tk.Label(top_frame, text=f"Welcome back!\n{name}", font=("Helvetica", 40, "bold"), bg="#f8fdff", fg="black").pack(pady=30)

        total = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0] if students else 0
        card = tk.Frame(frame, bg="white", relief="flat", bd=2, highlightbackground="#00d4aa", highlightthickness=3)
        card.pack(pady=50, padx=500)
        tk.Label(card, text="Total Students", font=("Helvetica", 20), bg="white", fg="#555").pack(pady=20)
        tk.Label(card, text=str(total), font=("Helvetica", 80, "bold"), bg="white", fg="#00d4aa").pack(pady=10)

    def show_add_student(self):
        self.clear_content()
        frame = tk.Frame(self.content_frame, bg="#f8fdff")
        frame.pack(fill="both", expand=True)

        card = tk.Frame(frame, bg="white", relief="flat", bd=2, highlightbackground="#00d4aa", highlightthickness=3)
        card.pack(pady=60, padx=400)

        tk.Label(card, text="ADD NEW STUDENT", font=("Helvetica", 28, "bold"), bg="white", fg="black").pack(pady=40)

        entries = {}
        for field in ["Student ID *", "Full Name *", "Grade", "Email"]:
            tk.Label(card, text=field, font=("Helvetica", 14), bg="white", fg="#555").pack(pady=(20,8), anchor="w", padx=100)
            e = tk.Entry(card, font=("Helvetica", 16), bg="#f0f9ff", fg="black")
            e.pack(padx=100, fill="x", pady=5)
            entries[field] = e

        preview_frame = tk.Frame(card, bg="#f0f9ff", relief="sunken", bd=2)
        preview_frame.pack(pady=30, padx=100, fill="x")
        preview_frame.pack_propagate(False)
        preview_frame.config(height=200)
        self.photo_preview = tk.Label(preview_frame, text="No photo selected", font=("Helvetica", 14), bg="#f0f9ff", fg="#888")
        self.photo_preview.pack(expand=True)

        tk.Button(card, text="Choose Photo (Optional)", font=("Helvetica", 14, "bold"),
                  bg="#00d4aa", fg="black", command=self.choose_photo, pady=12).pack(pady=15)

        def save():
            sid = entries["Student ID *"].get().strip()
            name = entries["Full Name *"].get().strip()
            if not sid or not name:
                messagebox.showerror("Error", "ID and Name required!")
                return

            photo_path = None
            if self.selected_photo:
                ext = os.path.splitext(self.selected_photo)[1]
                photo_path = os.path.join(PHOTO_DIR, f"{sid}{ext}")
                shutil.copy(self.selected_photo, photo_path)
            else:
                # Assign random default avatar
                default = self.get_random_default_photo()
                if default:
                    ext = os.path.splitext(default)[1]
                    photo_path = os.path.join(PHOTO_DIR, f"{sid}_default{ext}")
                    shutil.copy(default, photo_path)

            try:
                grade = float(entries["Grade"].get() or 0) if entries["Grade"].get().strip() else None
                email = entries["Email"].get().strip() or None
                conn = sqlite3.connect(DB_NAME)
                conn.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?)",
                            (sid, name, grade, email, datetime.now().strftime("%Y-%m-%d %H:%M"), photo_path))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success!", f"Student '{name}' added with photo!")
                self.selected_photo = None
                self.show_dashboard()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Student ID already exists!")

        tk.Button(card, text="SAVE STUDENT", font=("Helvetica", 18, "bold"),
                  bg="#00d4aa", fg="black", command=save, pady=18).pack(fill="x", padx=100, pady=40)

    def show_all_students(self):
        self.clear_content()
        frame = tk.Frame(self.content_frame, bg="#f8fdff")
        frame.pack(fill="both", expand=True)
        tk.Label(frame, text="ALL STUDENTS", font=("Helvetica", 36, "bold"), bg="#f8fdff", fg="black").pack(pady=40)

        conn = sqlite3.connect(DB_NAME)
        for student in conn.execute("SELECT * FROM students ORDER BY name").fetchall():
            card = tk.Frame(frame, bg="white", relief="flat", bd=2, highlightbackground="#00d4aa", highlightthickness=3)
            card.pack(fill="x", pady=20, padx=120)

            photo_frame = tk.Frame(card, bg="white", width=200, height=200)
            photo_frame.pack(side="left", padx=40, pady=30)
            photo_frame.pack_propagate(False)
            self.display_circular_photo(photo_frame, student[5])

            info = tk.Frame(card, bg="white")
            info.pack(side="left", fill="both", expand=True, padx=30, pady=40)
            tk.Label(info, text=student[1], font=("Helvetica", 26, "bold"), bg="white", fg="black", anchor="w").pack(fill="x", pady=8)
            tk.Label(info, text=f"ID: {student[0]} • Grade: {student[2] or 'N/A'} • {student[3] or 'No email'}",
                     font=("Helvetica", 16), bg="white", fg="#333", anchor="w").pack(fill="x")

# CREATE FOLDER FOR DEFAULT AVATARS
if not os.path.exists("default_avatars"):
    os.makedirs("default_avatars")
    print("Created 'default_avatars' folder! Add some cute PNG/JPG avatars there for random default photos!")

# LAUNCH
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = StudentManager(root)
    root.mainloop()