# transactions_ui.py
import tkinter as tk
from tkinter import ttk, messagebox

# Global reference to the Transaction List Container
transactions_list_frame = None


def get_transaction_list_frame():
    global transactions_list_frame
    return transactions_list_frame


def modern_button(parent, text, color, cmd):
    """A helper function for consistent button styling (copied from adminDashboardUI)."""
    return tk.Button(
        parent, text=text, command=cmd,
        bg=color, fg="white",
        font=("Segoe UI", 11, "bold"),
        bd=0, padx=18, pady=10,
        activebackground=color,
        activeforeground="white",
        relief="flat"
    )


def display_recent_transactions(borrow_records, get_books_func, target_frame):
    """Refreshes the recent transaction list based on current mock data."""
    # Clear previous items
    for widget in target_frame.winfo_children():
        widget.destroy()

    # New implementation: load recent loans from API if provided; fall back to borrow_records param
    from api_client import get_loans

    try:
        loans = get_loans()
    except Exception:
        loans = borrow_records or []

    if not loans:
        tk.Label(target_frame, text="No recent transactions found.", bg="white", fg="#7f8c8d",
                 font=("Segoe UI", 10)).pack(padx=20, pady=20)
        return

    # Display the last few loans
    for record in loans[-5:]:
        is_return = record.get('status') == 'returned'
        book_title = record.get('book_title') or 'Unknown'

        if is_return:
            action = "Return"
            icon = "↩️"
            color = "#2ecc71"
            details = f"User {record.get('user')}"
            date_str = record.get('return_date') or ''
        else:
            action = "Checkout"
            icon = "📤"
            color = "#3498db"
            details = f"User {record.get('user')} • Due: {record.get('due_date')}"
            date_str = record.get('borrow_date')

        item_frame = tk.Frame(target_frame, bg="white", padx=15, pady=10)
        item_frame.pack(fill="x", pady=1, side="top")

        # Icon
        tk.Label(item_frame, text=icon, fg=color, bg="white", font=("Segoe UI", 16)).pack(side="left", padx=5)

        # Text details
        text_frame = tk.Frame(item_frame, bg="white")
        text_frame.pack(side="left", fill="x", expand=True)

        tk.Label(text_frame, text=f"{action} - \"{book_title}\"", bg="white", fg="#2c3e50",
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")
        tk.Label(text_frame, text=details, bg="white", fg="#7f8c8d", font=("Segoe UI", 9)).pack(anchor="w")

        # Date
        tk.Label(item_frame, text=date_str, bg="white", fg="#7f8c8d", font=("Segoe UI", 9)).pack(side="right")


def create_transactions_ui(parent_frame, get_books_func, get_borrow_records_func, borrow_cmd, return_cmd):
    """
    Builds the complete Lending & Returns UI.

    :param borrow_cmd: The callback function (handle_borrow_logic) for Check Out.
    :param return_cmd: The callback function (handle_return_logic) for Return.
    """
    global transactions_list_frame

    frame = tk.Frame(parent_frame, bg="#f5f7fa")
    frame.place(relwidth=1, relheight=1)

    # Create canvas with scrollbar for transactions scrolling
    trans_canvas = tk.Canvas(frame, bg="#f5f7fa", highlightthickness=0)
    trans_scrollbar = tk.Scrollbar(frame, orient="vertical", command=trans_canvas.yview)
    trans_scrollable = tk.Frame(trans_canvas, bg="#f5f7fa")

    trans_scrollable.bind(
        "<Configure>",
        lambda e: trans_canvas.configure(scrollregion=trans_canvas.bbox("all"))
    )

    trans_canvas.create_window((0, 0), window=trans_scrollable, anchor="nw")
    trans_canvas.configure(yscrollcommand=trans_scrollbar.set)

    trans_canvas.pack(side="left", fill="both", expand=True)
    trans_scrollbar.pack(side="right", fill="y")

    # Enable mouse wheel scrolling
    def on_trans_mousewheel(event):
        trans_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    trans_canvas.bind_all("<MouseWheel>", on_trans_mousewheel)

    # ---------------- PAGE HEADER ----------------
    header = tk.Frame(trans_scrollable, bg="#f5f7fa")
    header.pack(fill="x", padx=20, pady=(10, 5))

    tk.Label(
        header,
        text="Lending & Returns",
        font=("Segoe UI", 26, "bold"),
        bg="#f5f7fa",
        fg="#2c3e50"
    ).pack(anchor="w")

    tk.Label(
        header,
        text="Process book checkouts and returns",
        font=("Segoe UI", 12),
        bg="#f5f7fa",
        fg="#7f8c8d"
    ).pack(anchor="w")

    # ---------------- QUICK TRANSACTION CARD ----------------
    quick_trans_card = tk.Frame(trans_scrollable, bg="white", padx=20, pady=20, bd=1, relief="solid")
    quick_trans_card.pack(fill="x", padx=20, pady=(20, 0))

    tk.Label(
        quick_trans_card,
        text="Quick Transaction",
        font=("Segoe UI", 16, "bold"),
        bg="white",
        fg="#2c3e50"
    ).pack(anchor="w", pady=(0, 5))

    tk.Label(
        quick_trans_card,
        text="Process book checkouts and returns quickly",
        font=("Segoe UI", 10),
        bg="white",
        fg="#7f8c8d"
    ).pack(anchor="w", pady=(0, 15))

    # --- Tabbed Interface for Check Out / Return ---
    notebook = ttk.Notebook(quick_trans_card, height=120)
    notebook.pack(fill="x", expand=False, pady=(5, 15))

    check_out_frame = tk.Frame(notebook, bg="white", padx=10, pady=10)
    return_frame = tk.Frame(notebook, bg="white", padx=10, pady=10)

    notebook.add(check_out_frame, text="Check Out")
    notebook.add(return_frame, text="Return")

    # Placeholder logic helper
    def setup_placeholder(entry, default_text):
        entry.config(fg="#a0a0a0")
        entry.bind("<FocusIn>", lambda e: [entry.delete(0, tk.END),
                                           entry.config(fg="#000000")] if entry.get() == default_text else None)
        entry.bind("<FocusOut>",
                   lambda e: [entry.insert(0, default_text), entry.config(fg="#a0a0a0")] if not entry.get() else None)

    # === CHECK OUT TAB ===

    # Input Grid
    check_out_grid = tk.Frame(check_out_frame, bg="white")
    check_out_grid.pack(fill="x")
    check_out_grid.columnconfigure(0, weight=1)
    check_out_grid.columnconfigure(1, weight=1)

    tk.Label(check_out_grid, text="Book ISBN / Book ID", bg="white", fg="#7f8c8d", font=("Segoe UI", 10)).grid(row=0,
                                                                                                               column=0,
                                                                                                               sticky="w",
                                                                                                               padx=10)
    tk.Label(check_out_grid, text="Student ID / User ID", bg="white", fg="#7f8c8d", font=("Segoe UI", 10)).grid(row=0,
                                                                                                                column=1,
                                                                                                                sticky="w",
                                                                                                                padx=10)

    # Input Fields
    book_id_entry = tk.Entry(check_out_grid, font=("Segoe UI", 11), bd=1, relief="solid", width=30)
    book_id_entry.grid(row=1, column=0, sticky="ew", padx=10, ipady=4)
    book_id_entry.insert(0, "Enter ISBN or Book ID")

    student_id_entry = tk.Entry(check_out_grid, font=("Segoe UI", 11), bd=1, relief="solid", width=30)
    student_id_entry.grid(row=1, column=1, sticky="ew", padx=10, ipady=4)
    student_id_entry.insert(0, "Enter Student/User ID")

    setup_placeholder(book_id_entry, "Enter ISBN or Book ID")
    setup_placeholder(student_id_entry, "Enter Student/User ID")

    # Check Out Command Wrapper
    def process_check_out():
        b_id = book_id_entry.get().strip()
        s_id = student_id_entry.get().strip()

        if b_id in ["Enter ISBN or Book ID", ""] or s_id in ["Enter Student/User ID", ""]:
            messagebox.showerror("Error", "Please enter both Book ID and Student ID.")
            return

        # Call external command for business logic (expects book id integer or isbn)
        try:
            # If the borrow_cmd expects a book id int, ensure conversion
            borrow_cmd(b_id, s_id)
        except Exception as e:
            messagebox.showerror('Error', f'Checkout failed: {e}')

        # Clear fields
        book_id_entry.delete(0, tk.END)
        book_id_entry.insert(0, "Enter ISBN or Book ID")
        student_id_entry.delete(0, tk.END)
        student_id_entry.insert(0, "Enter Student/User ID")
        setup_placeholder(book_id_entry, "Enter ISBN or Book ID")
        setup_placeholder(student_id_entry, "Enter Student/User ID")

    # Check Out Button
    modern_button(
        check_out_frame,
        "Check Out Book",
        "#2c3e50",
        process_check_out
    ).pack(side="right", pady=10, padx=10)

    # Input Grid
    return_grid = tk.Frame(return_frame, bg="white")
    return_grid.pack(fill="x")
    return_grid.columnconfigure(0, weight=1)
    return_grid.columnconfigure(1, weight=1)  # Added second column

    # Input Labels (Matching Check Out tab)
    tk.Label(return_grid, text="Book ISBN / Book ID", bg="white", fg="#7f8c8d", font=("Segoe UI", 10)).grid(row=0,
                                                                                                            column=0,
                                                                                                            sticky="w",
                                                                                                            padx=10)
    tk.Label(return_grid, text="Student ID / User ID", bg="white", fg="#7f8c8d", font=("Segoe UI", 10)).grid(row=0,
                                                                                                             column=1,
                                                                                                             sticky="w",
                                                                                                             padx=10)

    # Input Fields
    return_book_id_entry = tk.Entry(return_grid, font=("Segoe UI", 11), bd=1, relief="solid", width=30)
    return_book_id_entry.grid(row=1, column=0, sticky="ew", padx=10, ipady=4)
    setup_placeholder(return_book_id_entry, "Enter Book ID or ISBN")

    # NOTE: This field is not strictly needed for the return logic but is added for visual parity
    return_student_id_entry = tk.Entry(return_grid, font=("Segoe UI", 11), bd=1, relief="solid", width=30)
    return_student_id_entry.grid(row=1, column=1, sticky="ew", padx=10, ipady=4)
    setup_placeholder(return_student_id_entry, "Enter Student/User ID")

    # Return Command Wrapper
    def process_return():
        # Data validation and pass-through to external logic
        b_id = return_book_id_entry.get().strip()

        # NOTE: We still only validate the Book ID for the return logic
        if b_id in ["Enter Book ID or ISBN", ""]:
            messagebox.showerror("Error", "Please enter Book ID to return.")
            return

        # Call external command for business logic (only passing Book ID)
        try:
            return_cmd(b_id)
        except Exception as e:
            messagebox.showerror('Error', f'Return failed: {e}')

        # Clear fields
        return_book_id_entry.delete(0, tk.END)
        return_book_id_entry.insert(0, "Enter Book ID or ISBN")
        setup_placeholder(return_book_id_entry, "Enter Book ID or ISBN")

        # Clear the second field as well
        return_student_id_entry.delete(0, tk.END)
        return_student_id_entry.insert(0, "Enter Student/User ID")
        setup_placeholder(return_student_id_entry, "Enter Student/User ID")

    # Return Button
    modern_button(
        return_frame,
        "Return Book",
        "#2ecc71",
        process_return
    ).pack(side="right", pady=10, padx=10)
    # ---------------- RECENT TRANSACTIONS ----------------

    recent_trans_container = tk.Frame(trans_scrollable, bg="#f5f7fa")
    recent_trans_container.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(
        recent_trans_container,
        text="Recent Transactions",
        font=("Segoe UI", 16, "bold"),
        bg="#f5f7fa",
        fg="#2c3e50"
    ).pack(anchor="w", pady=(10, 5))

    tk.Label(
        recent_trans_container,
        text="Latest book checkouts and returns",
        font=("Segoe UI", 10),
        bg="#f5f7fa",
        fg="#7f8c8d"
    ).pack(anchor="w", pady=(0, 10))

    # Transaction List Container (Mock Display)
    global transactions_list_frame
    transactions_list_frame = tk.Frame(recent_trans_container, bg="white", bd=1, relief="solid")
    transactions_list_frame.pack(fill="both", expand=True)

    # Initial display
    # This must be called from outside by the adminDashboardUI.refresh_transactions()
    # display_recent_transactions(get_borrow_records_func(), get_books_func, transactions_list_frame)

    return frame