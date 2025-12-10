# borrowing_history_ui.py
import tkinter as tk
from tkinter import ttk, messagebox
import datetime

from api_client import get_loans


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

def create_borrowing_history_ui(parent_frame, current_student_id=None):
    """Loads the Borrowing History content into the provided frame."""

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
    tk.Label(main_wrapper, text="Borrowing History", font=("Segoe UI", 28, "bold"), bg="#f5f7fa", fg="#2c3e50").pack(
        anchor="w")
    tk.Label(main_wrapper, text="View your complete reading history", font=("Segoe UI", 12), bg="#f5f7fa",
             fg="#7f8c8d").pack(anchor="w", pady=(0, 20))

    # ---------------- HISTORY STATS ROW ----------------
    stats_row = tk.Frame(main_wrapper, bg="#f5f7fa")
    stats_row.pack(fill="x", pady=10)

    # Load history from API loans if available
    from api_client import get_loans
    try:
        loans = get_loans()
    except Exception:
        loans = []

    if current_student_id:
        loans = [l for l in loans if l.get('user') == current_student_id]

    total_reads = len([l for l in loans if l.get('status') == 'returned'])
    
    # Calculate this year's reads
    current_year = datetime.datetime.now().year
    this_year_reads = 0
    for l in loans:
        if l.get('status') == 'returned' and l.get('return_date'):
            try:
                return_dt = datetime.datetime.fromisoformat(l['return_date'])
                if return_dt.year == current_year:
                    this_year_reads += 1
            except:
                pass
    
    late_returns = 0
    for l in loans:
        if l.get('status') == 'returned' and l.get('return_date') and l.get('due_date'):
            try:
                return_dt = datetime.datetime.fromisoformat(l['return_date'])
                due_dt = datetime.datetime.fromisoformat(l['due_date'])
                if return_dt > due_dt:
                    late_returns += 1
            except:
                pass

    _create_history_stat_card(stats_row, "Total Books Read", total_reads, "All time", "📘", "#5d5fef")
    _create_history_stat_card(stats_row, "This Year", this_year_reads, "Books completed this year",
                              "🗓️", "#2ecc71")
    _create_history_stat_card(stats_row, "Late Returns", f"{late_returns}",
                              f"Out of {total_reads} total", "⏰", "#f39c12")

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

    tk.Label(history_list_card, text=f"History ({total_reads})", font=("Segoe UI", 14, "bold"),
             bg="white", fg="#2c3e50", padx=15).pack(anchor="w")
    tk.Label(history_list_card, text="Your borrowing and return records", font=("Segoe UI", 10), bg="white",
             fg="#7f8c8d", padx=15).pack(anchor="w", pady=(0, 10))

    # Detailed History Items from loans - sort by most recent first
    all_loans_sorted = sorted(loans, key=lambda x: x.get('borrow_date', ''), reverse=True)

    for loan in all_loans_sorted:
        item_frame = tk.Frame(history_list_card, bg="white", padx=15, pady=10)
        item_frame.pack(fill="x", pady=5)

        # Cover/Image (Placeholder)
        cover_frame = tk.Frame(item_frame, bg="#f5f7fa", width=80, height=100)
        cover_frame.pack(side="left", padx=(0, 15))
        cover_frame.pack_propagate(False)
        tk.Label(cover_frame, text="📘", bg="#f5f7fa", fg="#5d5fef", font=("Segoe UI", 20)).pack(expand=True)

        # Text Content
        text_frame = tk.Frame(item_frame, bg="white")
        text_frame.pack(side="left", anchor="w", fill="x", expand=True)

        tk.Label(text_frame, text=loan.get('book_title', 'Unknown'), bg="white", fg="#2c3e50", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        tk.Label(text_frame, text=loan.get('book_author', ''), bg="white", fg="#7f8c8d", font=("Segoe UI", 10)).pack(anchor="w", pady=(2, 5))

        borrow_date = loan.get('borrow_date', '')
        return_date = loan.get('return_date', '')
        status = loan.get('status', '')
        
        days_loaned = ''
        status_text = "Borrowed"
        status_color = "#5d5fef"
        
        if status == 'returned' and return_date:
            status_text = "Returned"
            status_color = "#2ecc71"
            try:
                if borrow_date and return_date:
                    bd = datetime.datetime.fromisoformat(borrow_date)
                    rd = datetime.datetime.fromisoformat(return_date)
                    days_loaned = (rd - bd).days
            except:
                pass
        elif status == 'borrowed':
            status_text = "Currently Borrowed"
            status_color = "#f39c12"
            try:
                if borrow_date:
                    bd = datetime.datetime.fromisoformat(borrow_date)
                    days_loaned = (datetime.datetime.now() - bd).days
            except:
                pass

        # Format dates
        formatted_borrow = ""
        formatted_return = ""
        try:
            if borrow_date:
                formatted_borrow = datetime.datetime.fromisoformat(borrow_date).strftime('%m/%d/%Y')
        except:
            formatted_borrow = borrow_date
        
        try:
            if return_date:
                formatted_return = datetime.datetime.fromisoformat(return_date).strftime('%m/%d/%Y')
        except:
            formatted_return = return_date

        date_frame = tk.Frame(text_frame, bg="white")
        date_frame.pack(anchor="w", fill="x", pady=(0, 5))

        tk.Label(date_frame, text=f"Borrowed: {formatted_borrow}", bg="white", fg="#7f8c8d", font=("Segoe UI", 10)).pack(side="left")
        if formatted_return:
            tk.Label(date_frame, text=f"Returned: {formatted_return}", bg="white", fg="#7f8c8d", font=("Segoe UI", 10)).pack(side="left", padx=15)
        if days_loaned:
            tk.Label(date_frame, text=f"({days_loaned} days)", bg="white", fg="#7f8c8d", font=("Segoe UI", 9)).pack(side="left")

        # Status badge
        status_frame = tk.Frame(text_frame, bg=status_color, padx=6, pady=2, relief="flat", bd=0)
        status_frame.pack(anchor="w", pady=(5, 0))
        tk.Label(
            status_frame,
            text=status_text.upper(),
            bg=status_color,
            fg="white",
            font=("Segoe UI", 8, "bold")
        ).pack()

        ttk.Separator(history_list_card, orient='horizontal').pack(fill='x', padx=15, pady=5)

    return main_wrapper