# my_loans_ui.py
import tkinter as tk
from tkinter import ttk
import datetime
from datetime import timedelta

# --- MOCK DATA (Simulated retrieval for My Loans) ---

MOCK_STUDENT_BORROWS = [
    {
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "isbn": "978-0-06-112008-4",
        "due_date": (datetime.datetime.now() - timedelta(days=332)),  # Overdue
        "days_overdue": 332,
        "fine": 176.00,
        "status_icon": "📘"
    },
    {
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "isbn": "978-0-14-143951-8",
        "due_date": (datetime.datetime.now() - timedelta(days=357)),  # Overdue
        "days_overdue": 357,
        "fine": 178.00,
        "status_icon": "📘"
    },
    {
        "title": "The Hitchhiker's Guide",
        "author": "Douglas Adams",
        "isbn": "978-0-345-39180-3",
        "due_date": (datetime.datetime.now() + timedelta(days=5)),  # Active
        "days_overdue": 0,
        "fine": 0.00,
        "status_icon": "📘"
    }
]


def calculate_loan_stats(borrows):
    overdue_count = sum(1 for b in borrows if b['days_overdue'] > 0)
    active_count = len(borrows) - overdue_count

    return {
        "active": active_count,
        "overdue": overdue_count,
        "renewals_left": 3,  # Mock value
        "total_fines": sum(b['fine'] for b in borrows)
    }


MOCK_STATS = calculate_loan_stats(MOCK_STUDENT_BORROWS)


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

def create_my_loans_ui(parent_frame):
    """Loads the My Loans content into the provided frame."""

    # Clear previous content before loading new UI
    for widget in parent_frame.winfo_children():
        widget.destroy()

    main_wrapper = tk.Frame(parent_frame, bg="#f5f7fa", padx=30, pady=20)
    main_wrapper.pack(fill="both", expand=True)

    # ---------------- HEADER ----------------
    tk.Label(main_wrapper, text="My Loans", font=("Segoe UI", 28, "bold"), bg="#f5f7fa", fg="#2c3e50").pack(anchor="w")
    tk.Label(main_wrapper, text="Manage your currently borrowed books", font=("Segoe UI", 12), bg="#f5f7fa",
             fg="#7f8c8d").pack(anchor="w", pady=(0, 20))

    # ---------------- LOAN STATS ROW ----------------
    stats_row = tk.Frame(main_wrapper, bg="#f5f7fa")
    stats_row.pack(fill="x", pady=10)

    _create_loan_stat_card(stats_row, "Active Loans", MOCK_STATS["active"], "Books currently borrowed", "📘", "#5d5fef")
    _create_loan_stat_card(stats_row, "Overdue", MOCK_STATS["overdue"], "Need attention", "⭕", "#e74c3c")
    _create_loan_stat_card(stats_row, "Renewals Available", MOCK_STATS["renewals_left"], "Total renewals left", "↻",
                           "#9b59b6")

    # ---------------- OVERDUE ALERT ----------------
    if MOCK_STATS["overdue"] > 0:
        alert_frame = tk.Frame(main_wrapper, bg="#fcf2f2", bd=1, relief="solid", highlightbackground="#e74c3c",
                               highlightthickness=1)
        alert_frame.pack(fill="x", pady=(20, 10), padx=5)
        tk.Label(
            alert_frame,
            text=f" ❌ You have {MOCK_STATS['overdue']} overdue books. Please return them soon as possible to avoid fines.",
            bg="#fcf2f2",
            fg="#e74c3c",
            font=("Segoe UI", 10, "bold"),
            padx=10, pady=10,
            anchor="w"
        ).pack(fill="x")

    # ---------------- OVERDUE BOOKS LIST ----------------

    overdue_card = tk.Frame(main_wrapper, bg="white", pady=10)
    overdue_card.pack(fill="both", expand=True, pady=(20, 10))

    tk.Label(overdue_card, text=f"Overdue Books ({MOCK_STATS['overdue']})", font=("Segoe UI", 14, "bold"), bg="white",
             fg="#e74c3c", padx=15).pack(anchor="w")
    tk.Label(overdue_card, text="Please return these books immediately", font=("Segoe UI", 10), bg="white",
             fg="#7f8c8d", padx=15).pack(anchor="w", pady=(0, 10))

    # Overdue List Items
    for i, book in enumerate(MOCK_STUDENT_BORROWS):
        if book['days_overdue'] > 0:
            fine_amount = f"Fine: ${book['fine']:.2f}"

            item_frame = tk.Frame(overdue_card, bg="white", padx=15, pady=10)
            item_frame.pack(fill="x", pady=5)

            # Book Cover/Image (Placeholder - for display purposes)
            # You would integrate actual images here if available
            cover_frame = tk.Frame(item_frame, bg="#f5f7fa", width=80, height=120)
            cover_frame.pack(side="left", padx=(0, 15))
            cover_frame.pack_propagate(False)
            tk.Label(cover_frame, text="[Book Cover]", bg="#f5f7fa", fg="#7f8c8d", font=("Segoe UI", 8)).pack(
                expand=True)

            # Text Content
            text_frame = tk.Frame(item_frame, bg="white")
            text_frame.pack(side="left", anchor="w", fill="x", expand=True)

            tk.Label(text_frame, text=book["title"], bg="white", fg="#2c3e50", font=("Segoe UI", 12, "bold")).pack(
                anchor="w")
            tk.Label(text_frame, text=book["author"], bg="white", fg="#7f8c8d", font=("Segoe UI", 10)).pack(anchor="w",
                                                                                                            pady=(2, 5))

            # Overdue Status
            tk.Label(text_frame, text=f"🔴 {book['days_overdue']} days overdue", bg="white", fg="#e74c3c",
                     font=("Segoe UI", 10, "bold")).pack(anchor="w")
            tk.Label(text_frame, text=f"Due date: {book['due_date'].strftime('%m/%d/%Y')}", bg="white", fg="#7f8c8d",
                     font=("Segoe UI", 10)).pack(anchor="w")
            tk.Label(text_frame, text=fine_amount, bg="white", fg="#e74c3c", font=("Segoe UI", 10, "bold")).pack(
                anchor="w", pady=(5, 0))

            ttk.Separator(overdue_card, orient='horizontal').pack(fill='x', padx=15, pady=5)

    return main_wrapper