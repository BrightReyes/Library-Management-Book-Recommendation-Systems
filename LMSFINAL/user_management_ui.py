# user_management_ui.py
import tkinter as tk
from tkinter import ttk, messagebox

# --- NO IMPORTS FROM adminDashboardUI.py HERE TO AVOID CIRCULAR DEPENDENCY ---


# Global reference to the table (used by adminDashboardUI to force a refresh)
user_management_table = None


def get_current_user_table():
    global user_management_table
    return user_management_table


# ----------------- MODAL UI CREATION -----------------

def open_add_user_modal(parent_app_root, save_cmd):
    """
    Creates and displays the 'Add New User' modal window.

    :param parent_app_root: The root Tk object (app) for Toplevel window.
    :param save_cmd: The callback function (defined in adminDashboardUI.py) that handles saving logic.
    """
    win = tk.Toplevel(parent_app_root)
    win.title("Add New User")
    win.config(bg="white", padx=30, pady=20)
    win.geometry("450x420")
    win.transient(parent_app_root)
    win.grab_set()

    # --- Header ---
    tk.Label(
        win,
        text="Add New User",
        font=("Segoe UI", 16, "bold"),
        bg="white",
        fg="#2c3e50"
    ).pack(anchor="w", pady=(0, 5))

    tk.Label(
        win,
        text="Register a new user in the library system",
        font=("Segoe UI", 10),
        bg="white",
        fg="#7f8c8d"
    ).pack(anchor="w", pady=(0, 20))

    # --- Input Fields ---
    labels = ["Full Name", "Student ID", "Email"]
    placeholders = ["Enter full name", "STU12345", "user@university.edu"]
    entries = {}

    # Placeholder logic helper (Local function for modal)
    def setup_placeholder_logic(widget, default_text):
        def on_focus_in(event):
            if widget.get() == default_text:
                widget.delete(0, tk.END)
                widget.config(fg="#000000")

        def on_focus_out(event):
            if not widget.get():
                widget.insert(0, default_text)
                widget.config(fg="#a0a0a0")

        widget.bind("<FocusIn>", on_focus_in)
        widget.bind("<FocusOut>", on_focus_out)

    for i, text in enumerate(labels):
        tk.Label(
            win,
            text=text + " *",
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(anchor="w", pady=(5, 2))

        entry = tk.Entry(win, font=("Segoe UI", 11), bd=1, relief="solid", width=50)
        entry.insert(0, placeholders[i])
        entry.config(fg="#a0a0a0")

        setup_placeholder_logic(entry, placeholders[i])

        entry.pack(fill="x", ipady=4)
        entries[text] = entry  # Store by key

    # --- Action Buttons ---
    btn_frame = tk.Frame(win, bg="white")
    btn_frame.pack(fill="x", pady=(20, 0))
    btn_frame.columnconfigure(0, weight=1)  # Spacer column

    # Wrapper to collect data and call the external save function (save_cmd)
    def call_save_command():
        # Collect data needed by the external logic handler
        data = {
            "name": entries["Full Name"].get().strip(),
            "student_id": entries["Student ID"].get().strip(),
            "email": entries["Email"].get().strip(),
            "placeholders": placeholders  # Pass placeholders for validation check
        }
        # Call the external save command, passing the collected data and the modal window
        save_cmd(data, win)

        # Cancel Button

    tk.Button(
        btn_frame,
        text="Cancel",
        command=win.destroy,
        bg="#ecf0f1",
        fg="#2c3e50",
        activebackground="#bdc3c7",
        bd=0,
        font=("Segoe UI", 11, "bold"),
        padx=18,
        pady=10,
        relief="flat"
    ).pack(side="right", padx=10)

    # Add User Button (Modern Styled - Dark)
    tk.Button(
        btn_frame,
        text="Add User",
        command=call_save_command,  # Calls the wrapper to retrieve data and execute external save
        bg="#2c3e50",
        fg="white",
        font=("Segoe UI", 11, "bold"),
        bd=0,
        padx=18,
        pady=10,
        activebackground="#1c2b36",
        relief="flat"
    ).pack(side="right")


# ----------------- MAIN USER MANAGEMENT UI FUNCTION -----------------
def create_user_management_ui(parent_frame, get_students_func, get_borrowed_func, add_user_cmd):
    """Builds the complete User Management UI."""
    global user_management_table

    frame = tk.Frame(parent_frame, bg="#f5f7fa")
    frame.place(relwidth=1, relheight=1)

    # ---------------- PAGE HEADER & BUTTON ----------------
    top_bar = tk.Frame(frame, bg="#f5f7fa")
    top_bar.pack(fill="x", padx=20, pady=(10, 20))

    # Left side: Title and Description
    header_left = tk.Frame(top_bar, bg="#f5f7fa")
    header_left.pack(side="left", fill="x", expand=True)

    tk.Label(header_left, text="User Management", font=("Segoe UI", 26, "bold"), bg="#f5f7fa", fg="#2c3e50").pack(
        anchor="w")
    tk.Label(header_left, text="Manage library users and their accounts", font=("Segoe UI", 12), bg="#f5f7fa",
             fg="#7f8c8d").pack(anchor="w")

    app_root = parent_frame.winfo_toplevel()
    tk.Button(
        top_bar,
        text="➕ Add New User",
        # FIXED CALL: Button now calls the zero-argument command passed from adminDashboardUI
        command=add_user_cmd,
        bg="#5d5fef",
        fg="white",
        font=("Segoe UI", 11, "bold"),
        bd=0,
        padx=15,
        pady=7
    ).pack(side="right")

    # ---------------- SEARCH BAR ----------------
    search_frame = tk.Frame(frame, bg="white", bd=1, relief="solid")
    search_frame.pack(fill="x", padx=20, pady=(0, 20))

    tk.Label(search_frame, text="🔍", bg="white", font=("Segoe UI", 12)).pack(side="left", padx=10)

    search_entry = tk.Entry(
        search_frame,
        font=("Segoe UI", 11),
        bg="white",
        bd=0
    )
    search_entry.pack(side="left", fill="x", expand=True, padx=5, pady=10)
    search_entry.insert(0, "Search by name, student ID, or email...")

    # ---------------- MAIN TABLE CARD ----------------
    card = tk.Frame(frame, bg="white", bd=1, relief="solid")
    card.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    # Title with total count (mock)
    tk.Label(
        card,
        text=f"All Users ({len(get_students_func())})",
        font=("Segoe UI", 16, "bold"),
        bg="white",
        fg="#2c3e50"
    ).pack(anchor="w", padx=15, pady=10)

    # Define table columns
    columns = ("Name", "Student ID", "Email", "Role", "Status", "Books Out", "Join Date", "Actions")
    user_table = ttk.Treeview(card, columns=columns, show="headings", height=15)

    # Set global reference
    user_management_table = user_table

    # Configure headings
    user_table.heading("Name", text="Name")
    user_table.heading("Student ID", text="Student ID")
    user_table.heading("Email", text="Email")
    user_table.heading("Role", text="Role")
    user_table.heading("Status", text="Status")
    user_table.heading("Books Out", text="Books Out", anchor="center")
    user_table.heading("Join Date", text="Join Date")
    user_table.heading("Actions", text="Actions", anchor="center")

    # Configure column widths
    user_table.column("Name", width=150)
    user_table.column("Student ID", width=100)
    user_table.column("Email", width=200)
    user_table.column("Role", width=80)
    user_table.column("Status", width=90, stretch=False, anchor="center")
    user_table.column("Books Out", width=90, stretch=False, anchor="center")
    user_table.column("Join Date", width=100)
    user_table.column("Actions", width=100, stretch=False, anchor="center")

    user_table.pack(fill="both", expand=True, padx=15, pady=10)

    # --- Data Insertion and Dynamic Widgets ---

    # Function to populate/refresh the table
    def refresh_user_table():
        user_table.delete(*user_table.get_children())

        for student in get_students_func():
            # Mock data setup: Assume all students are 'student' role, status based on ID parity
            status = "active" if student['id'] % 2 == 1 else "suspended"

            # 5. FIXED CALL: Use the passed function for borrowed books count
            borrowed_count = len(get_borrowed_func(student['name']))
            join_date = "2024-01-01"  # Mock join date

            # Insert main row data
            user_table.insert(
                "",
                "end",
                values=(
                    f"👤 {student['name']}",
                    f"STU{student['id'] - 200:03d}",  # Generate mock STU ID
                    student['email'],
                    "student",
                    status,
                    borrowed_count,
                    join_date,
                    "Details"
                ),
                tags=('status_' + status,)
            )

    refresh_user_table()

    user_table.bind('<Double-1>', lambda e: messagebox.showinfo("Action", "View Details clicked!"))

    return frame