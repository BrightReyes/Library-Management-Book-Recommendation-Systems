# adminDashboardUI.py
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from datetime import timedelta
from book_management_ui import create_book_management_ui
from user_management_ui import create_user_management_ui, get_current_user_table, open_add_user_modal
from transactions_ui import create_transactions_ui, get_transaction_list_frame, display_recent_transactions

# Use API client as the single source of truth
from api_client import (
    get_books as api_get_books,
    create_book as api_create_book,
    update_book as api_update_book,
    delete_book as api_delete_book,
    get_users as api_get_users,
    create_user as api_create_user,
    update_user as api_update_user,
    delete_user as api_delete_user,
    get_loans as api_get_loans,
    create_loan as api_create_loan,
    return_loan as api_return_loan,
)


def get_books():
    return api_get_books()


def get_overdue_books():
    loans = api_get_loans()
    today = datetime.datetime.now().date()
    overdue = [l for l in loans if l.get('status') == 'borrowed' and l.get('due_date') and datetime.datetime.fromisoformat(l['due_date']).date() < today]
    return overdue


def borrow_book(book_id_or_isbn, student_identifier=None):
    # student_identifier: can be user id (int) or username/email
    # book_id_or_isbn: can be book id (int) or ISBN string
    
    # Find book by ID or ISBN
    books = api_get_books()
    book = None
    try:
        # Try as book ID first
        bid = int(book_id_or_isbn)
        book = next((b for b in books if b['id'] == bid), None)
    except ValueError:
        # Try as ISBN
        book = next((b for b in books if b.get('isbn') == book_id_or_isbn), None)
    
    if not book:
        raise Exception(f"Book not found: {book_id_or_isbn}")
    
    if book.get('available', 0) <= 0:
        raise Exception(f"Book '{book.get('title')}' is not available")
    
    payload = {'book': book['id']}
    if student_identifier:
        # try to determine user id
        try:
            payload['user'] = int(student_identifier)
        except ValueError:
            # try to resolve by username/email
            users = api_get_users()
            found = None
            for u in users:
                if u.get('username') == student_identifier or u.get('email') == student_identifier:
                    found = u
                    break
            if found:
                payload['user'] = found['id']
            else:
                raise Exception(f"User not found: {student_identifier}")
    api_create_loan(payload)
    return True


def return_book(book_id_or_isbn):
    # find active loan for the book by ID or ISBN
    books = api_get_books()
    book = None
    try:
        # Try as book ID first
        bid = int(book_id_or_isbn)
        book = next((b for b in books if b['id'] == bid), None)
    except ValueError:
        # Try as ISBN
        book = next((b for b in books if b.get('isbn') == book_id_or_isbn), None)
    
    if not book:
        raise Exception(f"Book not found: {book_id_or_isbn}")
    
    loans = api_get_loans()
    active = next((l for l in loans if l.get('book') == book['id'] and l.get('status') == 'borrowed'), None)
    if not active:
        raise Exception(f"No active loan found for book '{book.get('title')}'")
    api_return_loan(active['id'])
    return True


def get_students():
    users = api_get_users()
    # Return the raw user data from API - it already has all needed fields
    return users


def add_student(name, email):
    username = email.split('@')[0]
    payload = {'username': username, 'email': email, 'password': 'changeme'}
    return api_create_user(payload)


def edit_student(user_id, name, email):
    payload = {'username': name, 'email': email}
    return api_update_user(user_id, payload)


def delete_student(user_id):
    return api_delete_user(user_id)


def get_student_borrowed_books(name_or_id):
    users = api_get_users()
    user = None
    try:
        uid = int(name_or_id)
        user = next((u for u in users if u['id'] == uid), None)
    except Exception:
        user = next((u for u in users if u.get('username') == name_or_id or u.get('email') == name_or_id), None)
    if not user:
        return []
    loans = api_get_loans()
    return [l for l in loans if l.get('user') == user['id'] and l.get('status') == 'borrowed']


def get_student_overdue_books(name_or_id):
    borrowed = get_student_borrowed_books(name_or_id)
    today = datetime.datetime.now().date()
    overdue = [l for l in borrowed if l.get('due_date') and datetime.datetime.fromisoformat(l['due_date']).date() < today]
    return overdue


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
        text=f"👤 {username}\n{role.capitalize()}",
        fg="#2c3e50",
        bg="white",
        font=("Segoe UI", 10),
        pady=10
    ).pack(fill="x")

    def logout():
        """Logout and return to login screen."""
        from api_client import set_token
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            set_token(None)  # Clear the authentication token
            app.destroy()
            import login
            login.open_login_window()

    tk.Button(
        bottom_frame,
        text="  Logout",
        command=logout,
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
    
    # Create canvas with scrollbar for dashboard scrolling
    dashboard_canvas = tk.Canvas(dashboard_frame, bg="#f5f7fa", highlightthickness=0)
    dashboard_scrollbar = tk.Scrollbar(dashboard_frame, orient="vertical", command=dashboard_canvas.yview)
    dashboard_scrollable = tk.Frame(dashboard_canvas, bg="#f5f7fa")

    dashboard_scrollable.bind(
        "<Configure>",
        lambda e: dashboard_canvas.configure(scrollregion=dashboard_canvas.bbox("all"))
    )

    dashboard_canvas.create_window((0, 0), window=dashboard_scrollable, anchor="nw")
    dashboard_canvas.configure(yscrollcommand=dashboard_scrollbar.set)

    dashboard_canvas.pack(side="left", fill="both", expand=True)
    dashboard_scrollbar.pack(side="right", fill="y")

    # Enable mouse wheel scrolling
    def on_dashboard_mousewheel(event):
        dashboard_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    dashboard_canvas.bind_all("<MouseWheel>", on_dashboard_mousewheel)

    # Top Row: Welcome and Add New Book Button
    top_bar = tk.Frame(dashboard_scrollable, bg="#f5f7fa")
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
        command=lambda: switch_frame(books_frame, book_btn),
        bg="#5d5fef",
        fg="white",
        activebackground="#4a4cce",
        bd=0,
        font=("Segoe UI", 12, "bold"),
        padx=15,
        pady=5
    ).pack(side="right")

    # Stats Row (Four Cards)
    stats_frame = tk.Frame(dashboard_scrollable, bg="#f5f7fa")
    stats_frame.pack(fill="x", pady=(0, 20), padx=10)

    # Variables to hold the dashboard labels for dynamic updates
    try:
        total_books = len(get_books())
    except Exception:
        total_books = 0
    
    try:
        total_users = len(get_students())
    except Exception:
        total_users = 0
    
    try:
        overdue_count = len(get_overdue_books())
    except Exception:
        overdue_count = 0
    
    try:
        all_loans = api_get_loans()
        checked_out_count = len([l for l in all_loans if l.get('status') == 'borrowed'])
    except Exception:
        checked_out_count = 0
    
    total_books_label = create_card(stats_frame, "Total Books", total_books, "#5d5fef", "📚", "In library collection",
                                    "#27ae60")
    total_users_label = create_card(stats_frame, "Total Users", total_users, "#00b894", "👥", "Registered users",
                                    "#27ae60")
    overdue_label = create_card(stats_frame, "Overdue Books", overdue_count, "#d63031", "⏰",
                                "Need attention", "#d63031")
    checked_out_label = create_card(stats_frame, "Currently Checked Out", checked_out_count, "#f39c12", "📤",
                                    "Active loans", "#27ae60")

    # Main Content Area (Graph and Quick Actions)
    main_content_frame = tk.Frame(dashboard_scrollable, bg="#f5f7fa")
    main_content_frame.pack(fill="both", expand=True, padx=10)

    # Left Column (Graph/Activity - 70% width)
    left_col = tk.Frame(main_content_frame, bg="#f5f7fa")
    left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

    # Recent Activity
    activity_card = tk.Frame(left_col, bg="white", padx=15, pady=15)
    activity_card.pack(fill="both", expand=True)
    tk.Label(activity_card, text="Recent Activity", bg="white", font=("Segoe UI", 14, "bold")).pack(anchor="w",
                                                                                                    pady=(0, 5))
    tk.Label(activity_card, text="Latest system changes, borrowings, and returns.", bg="white", fg="#7f8c8d",
             font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 10))
    # Fetch recent activity from loans and display
    activity_container = tk.Frame(activity_card, bg="white")
    activity_container.pack(fill="both", expand=True)
    
    try:
        loans = api_get_loans()
        # Sort by borrow_date, most recent first
        sorted_loans = sorted(loans, key=lambda x: x.get('borrow_date', ''), reverse=True)[:10]
        
        if not sorted_loans:
            tk.Label(activity_container, text="No recent activity.", bg="white", fg="#7f8c8d",
                    font=("Segoe UI", 11)).pack(pady=10)
        else:
            for loan in sorted_loans:
                item_frame = tk.Frame(activity_container, bg="white", pady=5)
                item_frame.pack(fill="x")
                
                username = loan.get('username', f"User {loan.get('user')}")
                book_title = loan.get('book_title', 'Unknown Book')
                status = loan.get('status', 'unknown')
                date = loan.get('borrow_date', '')
                
                if status == 'borrowed':
                    icon = "📤"
                    action = "Borrowed"
                    color = "#3498db"
                elif status == 'returned':
                    icon = "↩️"
                    action = "Returned"
                    color = "#2ecc71"
                else:
                    icon = "📋"
                    action = status.title()
                    color = "#7f8c8d"
                
                tk.Label(item_frame, text=icon, bg="white", fg=color, font=("Segoe UI", 12)).pack(side="left", padx=5)
                text_frame = tk.Frame(item_frame, bg="white")
                text_frame.pack(side="left", fill="x", expand=True)
                tk.Label(text_frame, text=f"{username} {action.lower()} '{book_title}'", bg="white", fg="#2c3e50",
                        font=("Segoe UI", 10, "bold")).pack(anchor="w")
                if date:
                    try:
                        formatted_date = datetime.datetime.fromisoformat(date).strftime('%b %d, %Y')
                        tk.Label(text_frame, text=formatted_date, bg="white", fg="#7f8c8d",
                                font=("Segoe UI", 9)).pack(anchor="w")
                    except:
                        pass
    except Exception as e:
        tk.Label(activity_container, text=f"Error loading activity: {e}", bg="white", fg="#e74c3c",
                font=("Segoe UI", 10)).pack(pady=10)

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
        try:
            total_books_label.config(text=len(api_get_books()))
        except Exception:
            total_books_label.config(text="—")
        try:
            total_users_label.config(text=len(api_get_users()))
        except Exception:
            total_users_label.config(text="—")
        try:
            overdue_label.config(text=len(get_overdue_books()))
        except Exception:
            overdue_label.config(text="—")
        try:
            all_loans = api_get_loans()
            checked_out_label.config(text=len([l for l in all_loans if l.get('status') == 'borrowed']))
        except Exception:
            checked_out_label.config(text="—")

        # 2. Refresh Tables (if visible)
        if students_frame.winfo_viewable():
            refresh_students()
        if transactions_frame.winfo_viewable():
            refresh_transactions()

    # Book Management
    create_book_management_ui(books_frame)

    # User Management

    # 1. Define refresh_students (now works with custom layout instead of treeview)
    def refresh_students():
        # The user management UI handles its own refresh internally
        # This function is kept for compatibility but may not be needed
        pass

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

    create_user_management_ui(
        students_frame,
        get_students_func=get_students,
        get_borrowed_func=get_student_borrowed_books,
        add_user_cmd=lambda: open_add_user_modal(app, handle_add_user_logic)
    )

    # Lending/Returns (Transactions)

    # Business Logic Handlers for Borrow/Return
    def handle_borrow_logic(book_id, student_id):
        try:
            borrow_book(book_id, student_id)
            messagebox.showinfo("Success", f"Book successfully checked out!")
            refresh_all_data()
        except Exception as e:
            messagebox.showerror("Error", f"Checkout failed: {e}")

    def handle_return_logic(book_id):
        try:
            return_book(book_id)
            messagebox.showinfo("Success", f"Book successfully returned!")
            refresh_all_data()
        except Exception as e:
            messagebox.showerror("Error", f"Return failed: {e}")

    # 1. Refresh transactions function
    def refresh_transactions():
        """
        Refreshes the recent transactions list in the external UI component.
        """
        trans_frame = get_transaction_list_frame()
        if trans_frame:
            # transactions_ui will itself call the API if available; pass empty fallback
            display_recent_transactions([], get_books, trans_frame)

    # 2. Integration call for the Transaction UI
    create_transactions_ui(
        transactions_frame,
        get_books_func=get_books,
        get_borrow_records_func=lambda: api_get_loans(),
        borrow_cmd=handle_borrow_logic,
        return_cmd=handle_return_logic
    )

    # Load dashboard first
    refresh_all_data()
    app.mainloop()


if __name__ == "__main__":
    open_main_ui("admin_user")