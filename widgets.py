# db_viewer/widgets.py
from tkinter import ttk

def setup_treeview(parent):
    """Creates and returns a styled Treeview with scrollbar"""
    frame = ttk.Frame(parent)
    frame.pack(fill="both", expand=True, padx=40, pady=20)

    tree = ttk.Treeview(frame, show="headings", height=22)
    tree.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set)

    style = ttk.Style()
    style.configure("Treeview", font=("Helvetica", 12), rowheight=35)
    style.configure("Treeview.Heading", font=("Helvetica", 14, "bold"), background="#0f172a", foreground="white")

    return tree