# borrowing_history_ui.py
import tkinter as tk
from tkinter import ttk, messagebox
import datetime

# --- MOCK DATA (Simulated retrieval for Borrowing History) ---

MOCK_HISTORY_RECORDS = [
    {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "borrowed": datetime.datetime(2024, 10, 15),
        "returned": datetime.datetime(2024, 10, 28),
        "status": "On Time",
        "cover_placeholder": "[Image]"
    },
    {
        "title": "1984",
        "author": "George Orwell",
        "borrowed": datetime.datetime(2024, 10, 14),
        "returned": datetime.datetime(2024, 10, 24),
        "status": "On Time",
        "cover_placeholder": "[Image]"
    },
    {
        "title": "Brave New World",
        "author": "Aldous Huxley",
        "borrowed": datetime.datetime(2024, 9, 1),
        "returned": datetime.datetime(2024, 11, 1),
        "status": "Late",
        "cover_placeholder": "[Image]"
    }
]


# Helper to calculate status (for mock purposes)
def calculate_history_stats(records):
    total_reads = len(records)
    late_returns = sum(1 for r in records if r['status'] == 'Late')

    return {
        "total_reads": total_reads,
        "this_year_completed": 0,  # Mock value for 2024 completion count
        "late_returns": late_returns
    }


MOCK_STATS = calculate_history_stats(MOCK_HISTORY_RECORDS)


# Helper function for stat card creation
def _create_history_stat_card(parent, title, value, detail, icon, bg_color):
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


# Helper function for status label
def _create_status_label(parent, status):
    if status == "On Time":
        bg_color = "#2ecc71"  # Green
        fg_color = "white"
    else:
        bg_color = "#f39c12"  # Orange/Late
        fg_color = "white"

    label_frame = tk.Frame(parent, bg=bg_color, padx=6, pady=2, relief="flat", bd=0)
    label_frame.pack(anchor="w", pady=(5, 0))

    tk.Label(
        label_frame,
        text=status.upper(),
        bg=bg_color,
        fg=fg_color,
        font=("Segoe UI", 8, "bold")
    ).pack()


# ----------------- MAIN UI BUILDER FUNCTION -----------------

def create_borrowing_history_ui(parent_frame):
    """Loads the Borrowing History content into the provided frame."""

    # Clear previous content before loading new UI
    for widget in parent_frame.winfo_children():
        widget.destroy()

    main_wrapper = tk.Frame(parent_frame, bg="#f5f7fa", padx=30, pady=20)
    main_wrapper.pack(fill="both", expand=True)

    # ---------------- HEADER ----------------
    tk.Label(main_wrapper, text="Borrowing History", font=("Segoe UI", 28, "bold"), bg="#f5f7fa", fg="#2c3e50").pack(
        anchor="w")
    tk.Label(main_wrapper, text="View your complete reading history", font=("Segoe UI", 12), bg="#f5f7fa",
             fg="#7f8c8d").pack(anchor="w", pady=(0, 20))

    # ---------------- HISTORY STATS ROW ----------------
    stats_row = tk.Frame(main_wrapper, bg="#f5f7fa")
    stats_row.pack(fill="x", pady=10)

    _create_history_stat_card(stats_row, "Total Books Read", MOCK_STATS["total_reads"], "All time", "📘", "#5d5fef")
    _create_history_stat_card(stats_row, "This Year", MOCK_STATS["this_year_completed"], "Books completed in 2024",
                              "🗓️", "#2ecc71")
    _create_history_stat_card(stats_row, "Late Returns", f"{MOCK_STATS['late_returns']}",
                              f"Out of {MOCK_STATS['total_reads']} total", "⏰", "#f39c12")

    # ---------------- SEARCH & FILTER BAR ----------------
    filter_frame = tk.Frame(main_wrapper, bg="white", bd=1, relief="solid")
    filter_frame.pack(fill="x", pady=(20, 15))
    filter_frame.columnconfigure(0, weight=1)  # Allow search entry to expand

    tk.Entry(
        filter_frame,
        font=("Segoe UI", 11),
        bg="white",
        bd=0,
        width=40
    ).grid(row=0, column=0, sticky="ew", padx=(15, 10), pady=10)

    # Combo Box for Status
    ttk.Combobox(
        filter_frame,
        values=["All Status", "On Time", "Late", "Lost"],
        state="readonly",
        width=15
    ).grid(row=0, column=1, padx=10, pady=10)

    # Combo Box for Year
    current_year = datetime.datetime.now().year
    years = [str(y) for y in range(current_year, current_year - 5, -1)]
    ttk.Combobox(
        filter_frame,
        values=["All Years"] + years,
        state="readonly",
        width=10
    ).grid(row=0, column=2, padx=10, pady=10)

    # ---------------- HISTORY LIST ----------------

    history_list_card = tk.Frame(main_wrapper, bg="white", pady=10, bd=1, relief="solid")
    history_list_card.pack(fill="both", expand=True, pady=(10, 0))

    tk.Label(history_list_card, text=f"History ({MOCK_STATS['total_reads']})", font=("Segoe UI", 14, "bold"),
             bg="white", fg="#2c3e50", padx=15).pack(anchor="w")
    tk.Label(history_list_card, text="Your borrowing and return records", font=("Segoe UI", 10), bg="white",
             fg="#7f8c8d", padx=15).pack(anchor="w", pady=(0, 10))

    # Detailed History Items
    for book in MOCK_HISTORY_RECORDS:
        item_frame = tk.Frame(history_list_card, bg="white", padx=15, pady=10)
        item_frame.pack(fill="x", pady=5)

        # Cover/Image (Placeholder)
        cover_frame = tk.Frame(item_frame, bg="#f5f7fa", width=80, height=100)
        cover_frame.pack(side="left", padx=(0, 15))
        cover_frame.pack_propagate(False)
        tk.Label(cover_frame, text=book["cover_placeholder"], bg="#f5f7fa", fg="#7f8c8d", font=("Segoe UI", 8)).pack(
            expand=True)

        # Text Content
        text_frame = tk.Frame(item_frame, bg="white")
        text_frame.pack(side="left", anchor="w", fill="x", expand=True)

        tk.Label(text_frame, text=book["title"], bg="white", fg="#2c3e50", font=("Segoe UI", 12, "bold")).pack(
            anchor="w")
        tk.Label(text_frame, text=book["author"], bg="white", fg="#7f8c8d", font=("Segoe UI", 10)).pack(anchor="w",
                                                                                                        pady=(2, 5))

        # Borrow/Return Dates
        borrow_date = book["borrowed"].strftime('%m/%d/%Y')
        return_date = book["returned"].strftime('%m/%d/%Y')
        days_loaned = (book["returned"] - book["borrowed"]).days

        date_frame = tk.Frame(text_frame, bg="white")
        date_frame.pack(anchor="w", fill="x", pady=(0, 5))

        tk.Label(date_frame, text=f"Borrowed: {borrow_date}", bg="white", fg="#7f8c8d", font=("Segoe UI", 10)).pack(
            side="left")
        tk.Label(date_frame, text=f"Returned: {return_date}", bg="white", fg="#7f8c8d", font=("Segoe UI", 10)).pack(
            side="left", padx=15)
        tk.Label(date_frame, text=f"({days_loaned} days)", bg="white", fg="#7f8c8d", font=("Segoe UI", 9)).pack(
            side="left")

        _create_status_label(text_frame, book["status"])

        ttk.Separator(history_list_card, orient='horizontal').pack(fill='x', padx=15, pady=5)

    return main_wrapper