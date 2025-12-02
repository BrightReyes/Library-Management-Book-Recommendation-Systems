# adminDashboardUI.py
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from datetime import timedelta
from book_management_ui import create_book_management_ui
from user_management_ui import create_user_management_ui, get_current_user_table, open_add_user_modal
from transactions_ui import create_transactions_ui, get_transaction_list_frame, display_recent_transactions

# ------------------ MOCK DATA AND FUNCTIONS ------------------
# ... (MOCK DATA and CRUD functions remain unchanged) ...
books = [
    {"id": 101, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "genre": "Classic",
     "status": "Available"},
    {"id": 102, "title": "1984", "author": "George Orwell", "genre": "Dystopian", "status": "Borrowed"},
    {"id": 103, "title": "To Kill a Mockingbird", "author": "Harper Lee", "genre": "Classic", "status": "Borrowed"},
    {"id": 104, "title": "Sapiens", "author": "Yuval Noah Harari", "genre": "History", "status": "Available"},
    {"id": 105, "title": "Educated", "author": "Tara Westover", "genre": "Memoir", "status": "Available"},
]

borrow_records = [
    {"book_id": 102, "student_name": "Alice Smith",
     "borrow_date": (datetime.datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d"),
     "due_date": (datetime.datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")},  # Overdue
    {"book_id": 103, "student_name": "Bob Johnson",
     "borrow_date": (datetime.datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
     "due_date": (datetime.datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")},  # Active
    {"book_id": 104, "student_name": "Charlie Brown",
     "borrow_date": (datetime.datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
     "due_date": (datetime.datetime.now() + timedelta(days=13)).strftime("%Y-%m-%d")},  # Active
]

students = [
    {"id": 201, "name": "Alice Smith", "email": "alice@uni.edu"},
    {"id": 202, "name": "Bob Johnson", "email": "bob@uni.edu"},
    {"id": 203, "name": "Charlie Brown", "email": "charlie@uni.edu"},
]


# Simple CRUD mocks (essential for the provided code to run)
def add_book(title, author, genre):
    new_id = max(b['id'] for b in books) + 1 if books else 101
    books.append({"id": new_id, "title": title, "author": author, "genre": genre, "status": "Available"})


def edit_book(id, title, author, genre):
    book = next(b for b in books if b["id"] == id)
    book.update({"title": title, "author": author, "genre": genre})


def delete_book(id):
    global books
    books = [b for b in books if b["id"] != id]


def get_books():
    return books


def get_overdue_books():
    today = datetime.datetime.now().date()
    overdue_records = [r for r in borrow_records if
                       datetime.datetime.strptime(r["due_date"], "%Y-%m-%d").date() < today]
    return overdue_records


def borrow_book(book_id, student_name):
    book_id = int(book_id)
    book = next((b for b in books if b['id'] == book_id and b['status'] == "Available"), None)
    if book:
        book['status'] = "Borrowed"
        borrow_records.append({
            "book_id": book_id,
            "student_name": student_name,
            "borrow_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "due_date": (datetime.datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        })
        return True
    return False


def return_book(book_id):
    book_id = int(book_id)
    book = next((b for b in books if b['id'] == book_id and b['status'] == "Borrowed"), None)
    if book:
        book['status'] = "Available"
        global borrow_records
        borrow_records = [r for r in borrow_records if r['book_id'] != book_id]
        return True
    return False


def get_students(): return students


def add_student(name, email):
    new_id = max(s['id'] for s in students) + 1 if students else 201
    students.append({"id": new_id, "name": name, "email": email})


def edit_student(id, name, email):
    student = next(s for s in students if s["id"] == id)
    student.update({"name": name, "email": email})


def delete_student(id):
    global students
    students = [s for s in students if s["id"] != id]


def get_student_borrowed_books(name):
    return [r for r in borrow_records if r['student_name'] == name]


def get_student_overdue_books(name):
    today = datetime.datetime.now().date()
    return [r for r in borrow_records if
            r['student_name'] == name and datetime.datetime.strptime(r["due_date"], "%Y-%m-%d").date() < today]


# Note: The original 'modern_button' helper is required for the rest of the code to run.
def modern_button(parent, text, color, cmd):
    return tk.Button(
        parent, text=text, command=cmd,
        bg=color, fg="white",
        font=("Segoe UI", 11, "bold"),
        bd=0, padx=18, pady=10,
        activebackground=color,
        activeforeground="white"
    )


# ------------------ Admin Dashboard ------------------
def open_main_ui(username, role="admin"):
    app = tk.Tk()
    app.title(f"Library System - Admin ({username})")
    app.geometry("1400x800")
    app.config(bg="#f5f7fa")
    app.resizable(True, True)

    # ---------------- Sidebar (Enhanced Look) ----------------
    sidebar_width = 240
    sidebar = tk.Frame(app, width=sidebar_width, bg="#FFFFFF", relief="flat", bd=0)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)  # Keep width fixed

    # LMS Admin Header
    header_frame = tk.Frame(sidebar, bg="#FFFFFF")
    header_frame.pack(fill="x", pady=(20, 10))
    tk.Label(header_frame, text="📚 LMS Admin", fg="#5d5fef", bg="white", font=("Segoe UI", 16, "bold")).pack(pady=5)
    tk.Label(header_frame, text="Library Management", fg="#7f8c8d", bg="white", font=("Segoe UI", 10)).pack(
        pady=(0, 10))

    # Navigation Frame
    nav_frame = tk.Frame(sidebar, bg="#FFFFFF")
    nav_frame.pack(fill="both", expand=True, pady=10)

    # Bottom User/Logout Frame
    bottom_frame = tk.Frame(sidebar, bg="#FFFFFF")
    bottom_frame.pack(side="bottom", fill="x", pady=10)

    tk.Label(
        bottom_frame,
        text=f"👤 Admin User\n{role.capitalize()}",
        fg="#2c3e50",
        bg="white",
        font=("Segoe UI", 10),
        pady=10
    ).pack(fill="x")

    tk.Button(
        bottom_frame,
        text="  Logout",
        command=app.quit,  # Placeholder for logout
        bg="#ecf0f1",
        fg="#2c3e50",
        activebackground="#bdc3c7",
        anchor="w",
        bd=0,
        font=("Segoe UI", 12, "bold"),
        pady=10
    ).pack(fill="x")

    # ---------------- Content Area ----------------
    content = tk.Frame(app, bg="#f5f7fa")
    content.pack(side="right", fill="both", expand=True, padx=20, pady=20)

    # Frames for different views
    dashboard_frame = tk.Frame(content, bg="#f5f7fa")
    books_frame = tk.Frame(content, bg="#f5f7fa")  # This will host the new UI
    students_frame = tk.Frame(content, bg="#f5f7fa")  # This will host the new UI
    transactions_frame = tk.Frame(content, bg="#f5f7fa")
    # reports_frame = tk.Frame(content, bg="#f5f7fa") # Reports frame removed

    for frame in (dashboard_frame, books_frame, students_frame, transactions_frame):
        frame.place(relwidth=1, relheight=1)

    # Function to switch frames and highlight button
    active_button = None

    def switch_frame(frame, btn):
        nonlocal active_button
        if active_button:
            active_button.config(bg="white", fg="#2c3e50", font=("Segoe UI", 12))

        btn.config(bg="#ecf0f1", fg="#2c3e50", font=("Segoe UI", 12, "bold"))
        active_button = btn

        # Refresh data when switching to a relevant tab
        if frame == students_frame:
            refresh_all_data()
        elif frame == transactions_frame:
            refresh_all_data()

        frame.tkraise()

    # ---------------- Sidebar Buttons (Enhanced) ----------------
    def add_nav_btn(text, frame, icon):
        btn = tk.Button(
            nav_frame,
            text=f"  {icon} {text}",
            command=lambda: switch_frame(frame, btn),
            bg="white",
            fg="#2c3e50",
            activebackground="#ecf0f1",
            activeforeground="#2c3e50",
            bd=0,
            font=("Segoe UI", 12),
            anchor="w",
            padx=15,
            pady=10,
            width=sidebar_width // 6
        )
        btn.pack(fill="x", pady=2)
        return btn

    dashboard_btn = add_nav_btn("Dashboard", dashboard_frame, "📊")
    book_btn = add_nav_btn("Book Management", books_frame, "📚")
    user_btn = add_nav_btn("User Management", students_frame, "👥")
    trans_btn = add_nav_btn("Lending & Returns", transactions_frame, "🔄")
    # report_btn removed

    # Set Dashboard as active initially
    switch_frame(dashboard_frame, dashboard_btn)

    # Helper function for card creation (Refactored to match image style)
    def create_card(parent, title, value, bg, icon, stat_change, stat_color):
        card = tk.Frame(parent, bg="#FFFFFF", padx=15, pady=10, relief="flat", bd=0)
        card.pack(side="left", padx=10, fill="x", expand=True)

        # Main Data Row (Value and Icon)
        data_frame = tk.Frame(card, bg="white")
        data_frame.pack(fill="x")

        # Icon on the right
        icon_frame = tk.Frame(data_frame, bg=bg, width=40, height=40)
        icon_frame.pack(side="right", padx=(10, 0))
        icon_frame.pack_propagate(False)
        tk.Label(icon_frame, text=icon, bg=bg, fg="white", font=("Segoe UI", 16)).pack(expand=True)

        # Title
        tk.Label(card, text=title, bg="white", fg="#7f8c8d", font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 2))

        # Value Label (Dynamically updated)
        value_label = tk.Label(data_frame, text=value, bg="white", fg="#2c3e50", font=("Segoe UI", 24, "bold"))
        value_label.pack(side="left", anchor="w")

        # Stat Change Label
        tk.Label(card, text=stat_change, bg="white", fg=stat_color, font=("Segoe UI", 10)).pack(anchor="w", pady=(5, 0))

        return value_label  # Return the label for external updating

    # ---------------- Dashboard Content ----------------

    # Top Row: Welcome and Add New Book Button
    top_bar = tk.Frame(dashboard_frame, bg="#f5f7fa")
    top_bar.pack(fill="x", pady=(0, 20), padx=10)

    tk.Label(
        top_bar,
        text="Dashboard",
        font=("Segoe UI", 28, "bold"),
        bg="#f5f7fa",
        fg="#2c3e50"
    ).pack(side="left")

    tk.Label(
        top_bar,
        text="Welcome back! Here's what's happening today.",
        font=("Segoe UI", 12),
        bg="#f5f7fa",
        fg="#7f8c8d"
    ).pack(side="left", padx=10, pady=5)

    # Add New Book Button (Top Right)
    tk.Button(
        top_bar,
        text="➕ Add New Book",
        command=lambda: switch_frame(books_frame, book_btn),  # Just switch to the new Book Management frame
        bg="#5d5fef",
        fg="white",
        activebackground="#4a4cce",
        bd=0,
        font=("Segoe UI", 12, "bold"),
        padx=15,
        pady=5
    ).pack(side="right")

    # Stats Row (Four Cards)
    stats_frame = tk.Frame(dashboard_frame, bg="#f5f7fa")
    stats_frame.pack(fill="x", pady=(0, 20), padx=10)

    # Variables to hold the dashboard labels for dynamic updates
    total_books_label = create_card(stats_frame, "Total Books", len(books), "#5d5fef", "📚", "+12% from last month",
                                    "#27ae60")
    total_users_label = create_card(stats_frame, "Total Users", len(students), "#00b894", "👥", "+5% from last month",
                                    "#27ae60")
    overdue_label = create_card(stats_frame, "Overdue Books", len(get_overdue_books()), "#d63031", "⏰",
                                "-8% from last week", "#d63031")
    checked_out_label = create_card(stats_frame, "Books Checked Out Today", len(borrow_records), "#f39c12", "📤",
                                    "+25% from yesterday", "#27ae60")

    # Main Content Area (Graph and Quick Actions)
    main_content_frame = tk.Frame(dashboard_frame, bg="#f5f7fa")
    main_content_frame.pack(fill="both", expand=True, padx=10)

    # Left Column (Graph/Activity - 70% width)
    left_col = tk.Frame(main_content_frame, bg="#f5f7fa")
    left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

    # --- REPLACED: Monthly Borrowing Trends with Recent Activity Card ---
    # Recent Activity (Placeholder)
    activity_card = tk.Frame(left_col, bg="white", padx=15, pady=15)
    activity_card.pack(fill="both", expand=True)
    tk.Label(activity_card, text="Recent Activity", bg="white", font=("Segoe UI", 14, "bold")).pack(anchor="w",
                                                                                                    pady=(0, 5))
    tk.Label(activity_card, text="Latest system changes, borrowings, and returns.", bg="white", fg="#7f8c8d",
             font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 10))
    tk.Label(activity_card, text="[MOCK ACTIVITY LIST CONTENT FILLING SPACE]", bg="white", fg="#7f8c8d",
             font=("Segoe UI", 12), height=20).pack(
        fill="both", expand=True)  # Expanded content

    # Right Column (Quick Actions - 30% width)
    right_col = tk.Frame(main_content_frame, bg="#f5f7fa", width=300)
    right_col.pack(side="right", fill="y")
    right_col.pack_propagate(False)  # Keep fixed width

    # Quick Actions Card
    actions_card = tk.Frame(right_col, bg="white", padx=15, pady=15)
    actions_card.pack(fill="x", pady=(0, 20))
    tk.Label(actions_card, text="Quick Actions", bg="white", font=("Segoe UI", 14, "bold")).pack(anchor="w",
                                                                                                 pady=(0, 5))
    tk.Label(actions_card, text="Common tasks and shortcuts", bg="white", fg="#7f8c8d", font=("Segoe UI", 10)).pack(
        anchor="w", pady=(0, 15))

    # Quick Action Buttons
    def quick_action_button(parent, text, cmd):
        btn = tk.Button(
            parent, text=text, command=cmd,
            bg="#f5f7fa", fg="#2c3e50",
            activebackground="#ecf0f1",
            anchor="w",
            bd=0,
            font=("Segoe UI", 12),
            padx=10,
            pady=10
        )
        btn.pack(fill="x", pady=5)

    quick_action_button(actions_card, "➕ Add New Book",
                        lambda: switch_frame(books_frame, book_btn))
    # FIX: Quick action button should call the modal creator
    quick_action_button(actions_card, "👥 Register New User",
                        lambda: switch_frame(students_frame, user_btn) or open_add_user_modal(app,
                                                                                              handle_add_user_logic))
    quick_action_button(actions_card, "⏰ View Overdue List",
                        lambda: switch_frame(transactions_frame, trans_btn))

    # Removed Reports button here

    # ---------------- Common Refresh Function (Updated to use new labels) ----------------
    def refresh_all_data():
        # 1. Update Dashboard Stats
        total_books_label.config(text=len(books))
        total_users_label.config(text=len(students))
        overdue_label.config(text=len(get_overdue_books()))
        checked_out_label.config(text=len(borrow_records))

        # 2. Refresh Tables (if visible)
        if students_frame.winfo_viewable():
            refresh_students()
        if transactions_frame.winfo_viewable():
            refresh_transactions()

    # ---------------- Book Management (INTEGRATED) ----------------
    create_book_management_ui(books_frame)

    # ---------------- User Management (INTEGRATED) ----------------

    # 1. Define refresh_students
    def refresh_students():
        table = get_current_user_table()
        if table:
            table.delete(*table.get_children())
            for student in get_students():
                status = "active" if student['id'] % 2 == 1 else "suspended"
                borrowed_count = len(get_student_borrowed_books(student['name']))
                join_date = "2024-01-01"
                table.insert("", "end", values=(
                    f"👤 {student['name']}",
                    f"STU{student['id'] - 200:03d}",
                    student['email'],
                    "student",
                    status,
                    borrowed_count,
                    join_date,
                    "Details"
                ))

    # 2. Define the SAVE LOGIC handler
    def handle_add_user_logic(data_dict, modal_window):
        name = data_dict['name']
        student_id = data_dict['student_id']
        email = data_dict['email']
        placeholders = data_dict['placeholders']

        ph_name = placeholders[0]
        ph_id = placeholders[1]
        ph_email = placeholders[2]

        # Validation
        if name == ph_name or not name:
            messagebox.showerror("Validation Error", "Full Name is required.")
            return
        if student_id == ph_id or not student_id:
            messagebox.showerror("Validation Error", "Student ID is required.")
            return
        if email == ph_email or not email:
            messagebox.showerror("Validation Error", "Email is required.")
            return

        add_student(name, email)
        refresh_students()
        refresh_all_data()
        messagebox.showinfo("Success", f"User '{name}' added successfully (ID: {student_id}).")
        modal_window.destroy()

    # --- INTEGRATION STEP: Call the new function, passing the necessary callbacks ---
    create_user_management_ui(
        students_frame,
        get_students_func=get_students,
        get_borrowed_func=get_student_borrowed_books,
        add_user_cmd=lambda: open_add_user_modal(app, handle_add_user_logic)
    )

    # ---------------- Lending/Returns (Transactions) (INTEGRATED) ----------------

    # Business Logic Handlers for Borrow/Return
    def handle_borrow_logic(book_id, student_id):
        if borrow_book(book_id, student_id):
            messagebox.showinfo("Success", f"Book {book_id} successfully checked out to {student_id}.")
            refresh_all_data()
        else:
            messagebox.showerror("Error", f"Checkout failed. Book {book_id} may not be available.")

    def handle_return_logic(book_id):
        if return_book(book_id):
            messagebox.showinfo("Success", f"Book {book_id} successfully returned.")
            refresh_all_data()
        else:
            messagebox.showerror("Error", f"Return failed. Book {book_id} may not be currently borrowed.")

    # 1. Refresh transactions function
    def refresh_transactions():
        """
        Refreshes the recent transactions list in the external UI component.
        """
        trans_frame = get_transaction_list_frame()
        if trans_frame:
            display_recent_transactions(borrow_records, get_books, trans_frame)

    # 2. Integration call for the Transaction UI
    create_transactions_ui(
        transactions_frame,
        get_books_func=get_books,
        get_borrow_records_func=lambda: borrow_records,
        borrow_cmd=handle_borrow_logic,
        return_cmd=handle_return_logic
    )

    # Load dashboard first
    refresh_all_data()
    app.mainloop()


if __name__ == "__main__":
    open_main_ui("admin_user")