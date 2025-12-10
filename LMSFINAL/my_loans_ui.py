# my_loans_ui.py
import tkinter as tk
from tkinter import ttk
import datetime
from datetime import timedelta

from api_client import get_loans


def calculate_loan_stats_from_loans(loans):
    overdue_count = 0
    active_count = 0
    total_fines = 0.0
    for l in loans:
        if l.get('status') == 'borrowed':
            active_count += 1
            if l.get('due_date'):
                try:
                    due = datetime.datetime.fromisoformat(l['due_date'])
                    if due.date() < datetime.datetime.now().date():
                        overdue_count += 1
                except Exception:
                    pass
        total_fines += float(l.get('fine', 0) or 0)

    return {
        'active': active_count,
        'overdue': overdue_count,
        'renewals_left': 3,
        'total_fines': total_fines
    }


# Helper function for card creation (Local to this module)
def _create_loan_stat_card(parent, title, value, detail, icon, bg_color):
    card = tk.Frame(parent, bg="#FFFFFF", padx=15, pady=10, relief="solid", bd=1)
    card.pack(side="left", padx=10, fill="x", expand=True)

    # Icon/Value Row
    top_row = tk.Frame(card, bg="white")
    top_row.pack(fill="x")

    # Value
    tk.Label(top_row, text=value, bg="white", fg="#2c3e50", font=("Segoe UI", 24, "bold")).pack(side="left", anchor="w")

    # Icon
    icon_frame = tk.Frame(top_row, bg=bg_color, width=40, height=40)
    icon_frame.pack(side="right")
    icon_frame.pack_propagate(False)
    tk.Label(icon_frame, text=icon, bg=bg_color, fg="white", font=("Segoe UI", 16)).pack(expand=True)

    # Title & Detail
    tk.Label(card, text=title, bg="white", fg="#7f8c8d", font=("Segoe UI", 11)).pack(anchor="w", pady=(5, 2))
    tk.Label(card, text=detail, bg="white", fg="#7f8c8d", font=("Segoe UI", 10)).pack(anchor="w", pady=(5, 0))

    return card


# ----------------- MAIN UI BUILDER FUNCTION -----------------

def create_my_loans_ui(parent_frame, current_student_id=None):
    """Loads the My Loans content into the provided frame for the current student."""
    from tkinter import messagebox
    from api_client import return_loan

    # Clear previous content before loading new UI
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # Create canvas with scrollbar for scrolling functionality
    canvas = tk.Canvas(parent_frame, bg="#f5f7fa", highlightthickness=0)
    scrollbar = tk.Scrollbar(parent_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#f5f7fa")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Enable mouse wheel scrolling
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    canvas.bind_all("<MouseWheel>", on_mousewheel)

    main_wrapper = tk.Frame(scrollable_frame, bg="#f5f7fa", padx=30, pady=20)
    main_wrapper.pack(fill="both", expand=True)

    # ---------------- HEADER ----------------
    tk.Label(main_wrapper, text="My Loans", font=("Segoe UI", 28, "bold"), bg="#f5f7fa", fg="#2c3e50").pack(anchor="w")
    tk.Label(main_wrapper, text="Manage your currently borrowed books", font=("Segoe UI", 12), bg="#f5f7fa",
             fg="#7f8c8d").pack(anchor="w", pady=(0, 20))

    # ---------------- LOAN STATS ROW ----------------
    stats_row = tk.Frame(main_wrapper, bg="#f5f7fa")
    stats_row.pack(fill="x", pady=10)

    # Load actual stats from API for the current student
    loans = []
    try:
        loans = get_loans()
    except Exception:
        loans = []

    if current_student_id:
        loans = [l for l in loans if l.get('user') == current_student_id]

    stats = calculate_loan_stats_from_loans(loans)

    _create_loan_stat_card(stats_row, "Active Loans", stats.get('active', 0), "Books currently borrowed", "📘", "#5d5fef")
    _create_loan_stat_card(stats_row, "Overdue", stats.get('overdue', 0), "Need attention", "⏰", "#e74c3c")
    _create_loan_stat_card(stats_row, "Total Fines", f"${stats.get('total_fines', 0):.2f}", "Accumulated fines", "💰",
                           "#f39c12")

    # ---------------- OVERDUE ALERT ----------------
    if stats.get('overdue', 0) > 0:
        alert_frame = tk.Frame(main_wrapper, bg="#fcf2f2", bd=1, relief="solid", highlightbackground="#e74c3c",
                               highlightthickness=1)
        alert_frame.pack(fill="x", pady=(20, 10), padx=5)
        tk.Label(
            alert_frame,
            text=f" ❌ You have {stats.get('overdue', 0)} overdue books. Please return them soon as possible to avoid fines.",
            bg="#fcf2f2",
            fg="#e74c3c",
            font=("Segoe UI", 10, "bold"),
            padx=10, pady=10,
            anchor="w"
        ).pack(fill="x")

    # ---------------- OVERDUE BOOKS LIST ----------------

    overdue_card = tk.Frame(main_wrapper, bg="white", pady=10)
    overdue_card.pack(fill="both", expand=True, pady=(20, 10))

    tk.Label(overdue_card, text=f"Overdue Books ({stats.get('overdue', 0)})", font=("Segoe UI", 14, "bold"), bg="white",
             fg="#e74c3c", padx=15).pack(anchor="w")
    tk.Label(overdue_card, text="Please return these books immediately", font=("Segoe UI", 10), bg="white",
             fg="#7f8c8d", padx=15).pack(anchor="w", pady=(0, 10))

    # Overdue List Items
    # Show overdue items from API (using the already filtered loans from above)
    overdue_books = [b for b in loans if b.get('status') == 'borrowed' and b.get('due_date') and datetime.datetime.fromisoformat(b['due_date']).date() < datetime.datetime.now().date()]

    def handle_return(loan_id):
        if messagebox.askyesno("Confirm Return", "Are you sure you want to return this book?"):
            try:
                return_loan(loan_id)
                messagebox.showinfo("Success", "Book returned successfully!")
                # Refresh the UI
                create_my_loans_ui(parent_frame, current_student_id)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to return book: {e}")

    for book in overdue_books:
        fine_amount = f"Fine: ${book.get('fine', 0):.2f}"
        due_date_str = book.get('due_date', '')
        days_overdue = 0
        try:
            if due_date_str:
                due_dt = datetime.datetime.fromisoformat(due_date_str)
                days_overdue = (datetime.datetime.now().date() - due_dt.date()).days
        except Exception:
            pass
        
        item_frame = tk.Frame(overdue_card, bg="white", padx=15, pady=10)
        item_frame.pack(fill="x", pady=5)

        # Book Cover/Image (Placeholder - for display purposes)
        cover_frame = tk.Frame(item_frame, bg="#f5f7fa", width=80, height=120)
        cover_frame.pack(side="left", padx=(0, 15))
        cover_frame.pack_propagate(False)
        tk.Label(cover_frame, text="📘", bg="#f5f7fa", fg="#5d5fef", font=("Segoe UI", 24)).pack(expand=True)

        # Text Content
        text_frame = tk.Frame(item_frame, bg="white")
        text_frame.pack(side="left", anchor="w", fill="x", expand=True)

        tk.Label(text_frame, text=book.get("book_title", ""), bg="white", fg="#2c3e50", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        tk.Label(text_frame, text=book.get("book_author", ""), bg="white", fg="#7f8c8d", font=("Segoe UI", 10)).pack(anchor="w", pady=(2, 5))

        # Overdue Status
        tk.Label(text_frame, text=f"🔴 {days_overdue} days overdue", bg="white", fg="#e74c3c", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        if due_date_str:
            try:
                formatted_date = datetime.datetime.fromisoformat(due_date_str).strftime('%m/%d/%Y')
                tk.Label(text_frame, text=f"Due date: {formatted_date}", bg="white", fg="#7f8c8d", font=("Segoe UI", 10)).pack(anchor="w")
            except:
                tk.Label(text_frame, text=f"Due date: {due_date_str}", bg="white", fg="#7f8c8d", font=("Segoe UI", 10)).pack(anchor="w")
        tk.Label(text_frame, text=fine_amount, bg="white", fg="#e74c3c", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(5, 0))

        # Return Button
        btn_frame = tk.Frame(item_frame, bg="white")
        btn_frame.pack(side="right", padx=10)
        tk.Button(
            btn_frame,
            text="Return Book",
            command=lambda lid=book.get('id'): handle_return(lid),
            bg="#e74c3c",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            bd=0,
            padx=15,
            pady=8,
            activebackground="#c0392b",
            relief="flat"
        ).pack()

        ttk.Separator(overdue_card, orient='horizontal').pack(fill='x', padx=15, pady=5)

    # ---------------- ACTIVE LOANS (NON-OVERDUE) ----------------
    overdue_ids = [b.get('id') for b in overdue_books]
    active_loans = [l for l in loans if l.get('status') == 'borrowed' and l.get('id') not in overdue_ids]
    
    if active_loans:
        active_card = tk.Frame(main_wrapper, bg="white", pady=10, bd=1, relief="solid")
        active_card.pack(fill="both", expand=True, pady=(20, 10))

        tk.Label(active_card, text=f"Active Loans ({len(active_loans)})", font=("Segoe UI", 14, "bold"), bg="white",
                 fg="#2c3e50", padx=15).pack(anchor="w", pady=(10, 0))
        tk.Label(active_card, text="Books currently checked out", font=("Segoe UI", 10), bg="white",
                 fg="#7f8c8d", padx=15).pack(anchor="w", pady=(0, 10))

        for loan in active_loans:
            due_date_str = loan.get('due_date', '')
            days_remaining = 0
            try:
                if due_date_str:
                    due_dt = datetime.datetime.fromisoformat(due_date_str)
                    days_remaining = (due_dt.date() - datetime.datetime.now().date()).days
            except Exception:
                pass
            
            item_frame = tk.Frame(active_card, bg="white", padx=15, pady=10)
            item_frame.pack(fill="x", pady=5)

            # Book icon
            cover_frame = tk.Frame(item_frame, bg="#f5f7fa", width=80, height=120)
            cover_frame.pack(side="left", padx=(0, 15))
            cover_frame.pack_propagate(False)
            tk.Label(cover_frame, text="📘", bg="#f5f7fa", fg="#5d5fef", font=("Segoe UI", 24)).pack(expand=True)

            # Text Content
            text_frame = tk.Frame(item_frame, bg="white")
            text_frame.pack(side="left", anchor="w", fill="x", expand=True)

            tk.Label(text_frame, text=loan.get("book_title", ""), bg="white", fg="#2c3e50", font=("Segoe UI", 12, "bold")).pack(anchor="w")
            tk.Label(text_frame, text=loan.get("book_author", ""), bg="white", fg="#7f8c8d", font=("Segoe UI", 10)).pack(anchor="w", pady=(2, 5))

            # Due date info
            if due_date_str:
                try:
                    formatted_date = datetime.datetime.fromisoformat(due_date_str).strftime('%m/%d/%Y')
                    tk.Label(text_frame, text=f"Due: {formatted_date}", bg="white", fg="#7f8c8d", font=("Segoe UI", 10)).pack(anchor="w")
                except:
                    tk.Label(text_frame, text=f"Due: {due_date_str}", bg="white", fg="#7f8c8d", font=("Segoe UI", 10)).pack(anchor="w")
            
            days_color = "#2ecc71" if days_remaining > 7 else "#f39c12" if days_remaining > 0 else "#e74c3c"
            tk.Label(text_frame, text=f"{days_remaining} days remaining", bg="white", fg=days_color, font=("Segoe UI", 10, "bold")).pack(anchor="w")

            # Button Frame for Return
            btn_frame = tk.Frame(item_frame, bg="white")
            btn_frame.pack(side="right", padx=10)
            
            tk.Button(
                btn_frame,
                text="Return Book",
                command=lambda lid=loan.get('id'): handle_return(lid),
                bg="#2ecc71",
                fg="white",
                font=("Segoe UI", 10, "bold"),
                bd=0,
                padx=15,
                pady=8,
                activebackground="#27ae60",
                relief="flat"
            ).pack()

            ttk.Separator(active_card, orient='horizontal').pack(fill='x', padx=15, pady=5)

    return main_wrapper