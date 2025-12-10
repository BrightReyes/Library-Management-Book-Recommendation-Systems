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
    
    # Placeholder logic for search
    def on_search_focus_in(event):
        if search_entry.get() == "Search by name, student ID, or email...":
            search_entry.delete(0, tk.END)
            search_entry.config(fg="#000000")
    
    def on_search_focus_out(event):
        if not search_entry.get():
            search_entry.insert(0, "Search by name, student ID, or email...")
            search_entry.config(fg="#a0a0a0")
    
    search_entry.config(fg="#a0a0a0")
    search_entry.bind("<FocusIn>", on_search_focus_in)
    search_entry.bind("<FocusOut>", on_search_focus_out)
    
    # Bind real-time search
    def on_search_change(event):
        search_text = search_entry.get()
        refresh_user_table(search_text)
    
    search_entry.bind("<KeyRelease>", on_search_change)

    # ---------------- MAIN TABLE CARD ----------------
    card = tk.Frame(frame, bg="white", bd=1, relief="solid")
    card.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    # Title with total count
    title_frame = tk.Frame(card, bg="white")
    title_frame.pack(fill="x", padx=15, pady=10)
    
    user_count_label = tk.Label(
        title_frame,
        text=f"All Users ({len(get_students_func())})",
        font=("Segoe UI", 16, "bold"),
        bg="white",
        fg="#2c3e50"
    )
    user_count_label.pack(side="left")

    # Create scrollable container for user list
    list_canvas = tk.Canvas(card, bg="white", highlightthickness=0)
    list_scrollbar = tk.Scrollbar(card, orient="vertical", command=list_canvas.yview)
    scrollable_list = tk.Frame(list_canvas, bg="white")

    scrollable_list.bind(
        "<Configure>",
        lambda e: list_canvas.configure(scrollregion=list_canvas.bbox("all"))
    )

    list_canvas.create_window((0, 0), window=scrollable_list, anchor="nw")
    list_canvas.configure(yscrollcommand=list_scrollbar.set)

    list_canvas.pack(side="left", fill="both", expand=True, padx=15, pady=10)
    list_scrollbar.pack(side="right", fill="y", pady=10)

    # Enable mouse wheel scrolling
    def on_list_mousewheel(event):
        list_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    list_canvas.bind_all("<MouseWheel>", on_list_mousewheel)

    # Header row
    header_row = tk.Frame(scrollable_list, bg="#f5f7fa", height=40)
    header_row.pack(fill="x", pady=(0, 5))
    
    tk.Label(header_row, text="Name", bg="#f5f7fa", fg="#2c3e50", font=("Segoe UI", 10, "bold"), width=18, anchor="w").pack(side="left", padx=(5, 10))
    tk.Label(header_row, text="Student ID", bg="#f5f7fa", fg="#2c3e50", font=("Segoe UI", 10, "bold"), width=11, anchor="w").pack(side="left", padx=(0, 10))
    tk.Label(header_row, text="Email", bg="#f5f7fa", fg="#2c3e50", font=("Segoe UI", 10, "bold"), width=23, anchor="w").pack(side="left", padx=(0, 10))
    tk.Label(header_row, text="Role", bg="#f5f7fa", fg="#2c3e50", font=("Segoe UI", 10, "bold"), width=8, anchor="w").pack(side="left", padx=(35, 10))
    tk.Label(header_row, text="Books Out", bg="#f5f7fa", fg="#2c3e50", font=("Segoe UI", 10, "bold"), width=9, anchor="center").pack(side="left", padx=(35, 10))
    tk.Label(header_row, text="Actions", bg="#f5f7fa", fg="#2c3e50", font=("Segoe UI", 10, "bold"), width=10, anchor="center").pack(side="left", padx=(70, 5))

    # Set global reference to scrollable list
    user_management_table = scrollable_list

    # --- Data Insertion and Dynamic Widgets ---

    # Function to populate/refresh the table
    def refresh_user_table(search_term=""):
        # Clear existing user rows (keep header)
        for widget in scrollable_list.winfo_children()[1:]:  # Skip header row
            widget.destroy()

        students = get_students_func()
        
        # Update count
        user_count_label.config(text=f"All Users ({len(students)})")
        
        # Apply search filter
        if search_term and search_term != "Search by name, student ID, or email...":
            search_lower = search_term.lower()
            students = [s for s in students if 
                       search_lower in s.get('username', '').lower() or
                       search_lower in s.get('email', '').lower() or
                       search_lower in f"STU{s['id']:03d}".lower()]

        for student in students:
            # Get borrowed books count
            borrowed_count = len(get_borrowed_func(student['id']))

            # Create row frame
            row_frame = tk.Frame(scrollable_list, bg="white", height=50)
            row_frame.pack(fill="x", pady=2)
            
            username = student.get('username', student.get('email', 'Unknown'))
            student_id_str = f"STU{student['id']:03d}"
            email = student.get('email', '')
            role = "admin" if student.get('is_staff', False) else "student"
            
            # Columns
            tk.Label(row_frame, text=f"👤 {username}", bg="white", fg="#2c3e50", font=("Segoe UI", 10), width=18, anchor="w").pack(side="left", padx=(5, 10))
            tk.Label(row_frame, text=student_id_str, bg="white", fg="#7f8c8d", font=("Segoe UI", 10), width=11, anchor="w").pack(side="left", padx=(0, 10))
            tk.Label(row_frame, text=email, bg="white", fg="#7f8c8d", font=("Segoe UI", 10), width=23, anchor="w").pack(side="left", padx=(0, 10))
            tk.Label(row_frame, text=role, bg="white", fg="#7f8c8d", font=("Segoe UI", 10), width=8, anchor="w").pack(side="left", padx=(50, 10))
            tk.Label(row_frame, text=str(borrowed_count), bg="white", fg="#7f8c8d", font=("Segoe UI", 10), width=9, anchor="center").pack(side="left", padx=(50, 10))
            
            # Delete button
            def make_delete_handler(uid, uname):
                def handler():
                    if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user '{uname}'?\n\nThis action cannot be undone."):
                        try:
                            from api_client import delete_user
                            delete_user(uid)
                            refresh_user_table(search_term)
                            messagebox.showinfo("Success", f"User '{uname}' has been deleted successfully.")
                        except Exception as e:
                            messagebox.showerror("Error", f"Failed to delete user: {e}")
                return handler
            
            delete_btn = tk.Button(
                row_frame,
                text="🗑️ Delete",
                command=make_delete_handler(student['id'], username),
                bg="#e74c3c",
                fg="white",
                font=("Segoe UI", 9, "bold"),
                bd=0,
                padx=10,
                pady=5,
                activebackground="#c0392b",
                cursor="hand2"
            )
            delete_btn.pack(side="left", padx=(85, 5))
            
            # Separator
            ttk.Separator(scrollable_list, orient='horizontal').pack(fill='x', padx=10)

    refresh_user_table()

    return frame