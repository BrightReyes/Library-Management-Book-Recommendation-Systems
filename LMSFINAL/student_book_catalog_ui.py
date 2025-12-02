# student_book_catalog_ui.py
import tkinter as tk
from tkinter import ttk, messagebox

# --- MOCK DATA and Helper Functions (Must be provided by the main app/admin module) ---

# We'll use a mock list of books and a mock borrow function.
# In a real setup, these would be passed from the StudentPortalApp initialization.

MOCK_CATALOG_BOOKS = [
    {"id": 106, "title": "The Hitchhiker's Guide to the Galaxy", "author": "Douglas Adams", "genre": "Sci-Fi",
     "available": 2},
    {"id": 107, "title": "A Brief History of Time", "author": "Stephen Hawking", "genre": "Science", "available": 1},
    {"id": 108, "title": "Becoming", "author": "Michelle Obama", "genre": "Biography", "available": 0},
    # Unavailable book
    {"id": 109, "title": "Where the Crawdads Sing", "author": "Delia Owens", "genre": "Fiction", "available": 4},
]


def modern_button_small(parent, text, color, cmd):
    """A helper for small action buttons."""
    return tk.Button(
        parent, text=text, command=cmd,
        bg=color, fg="white",
        font=("Segoe UI", 10, "bold"),
        bd=0, padx=10, pady=5,
        activebackground=color,
        activeforeground="white",
        relief="flat"
    )


def create_book_catalog_ui(parent_frame, current_student_name, borrow_logic_cmd):
    """
    Builds the book catalog interface for students.

    :param parent_frame: The frame to contain the UI.
    :param current_student_name: The name of the logged-in student.
    :param borrow_logic_cmd: The callback function to handle the actual borrowing process.
    """

    # Clear previous widgets
    for widget in parent_frame.winfo_children():
        widget.destroy()

    frame = tk.Frame(parent_frame, bg="#f5f7fa")
    frame.pack(fill="both", expand=True)

    # ---------------- HEADER ----------------
    header_frame = tk.Frame(frame, bg="#f5f7fa")
    header_frame.pack(fill="x", padx=30, pady=(20, 5))

    tk.Label(
        header_frame,
        text="Book Catalog",
        font=("Segoe UI", 28, "bold"),
        bg="#f5f7fa",
        fg="#2c3e50"
    ).pack(anchor="w")

    tk.Label(
        header_frame,
        text="Browse and borrow books available in the library.",
        font=("Segoe UI", 12),
        bg="#f5f7fa",
        fg="#7f8c8d"
    ).pack(anchor="w", pady=(0, 20))

    # ---------------- SEARCH BAR ----------------
    search_frame = tk.Frame(frame, bg="white", bd=1, relief="solid")
    search_frame.pack(fill="x", padx=30, pady=(0, 20))

    tk.Label(search_frame, text="🔍", bg="white", font=("Segoe UI", 12)).pack(side="left", padx=10)

    search_entry = tk.Entry(
        search_frame,
        font=("Segoe UI", 11),
        bg="white",
        bd=0
    )
    search_entry.pack(side="left", fill="x", expand=True, padx=5, pady=10)
    search_entry.insert(0, "Search by title or author...")

    # ---------------- MAIN TABLE/LIST VIEW ----------------

    table_card = tk.Frame(frame, bg="white", bd=1, relief="solid")
    table_card.pack(fill="both", expand=True, padx=30, pady=(0, 30))

    # Define table columns
    columns = ("Title", "Author", "Genre", "Availability", "Action")
    catalog_table = ttk.Treeview(table_card, columns=columns, show="headings", height=15)

    # Configure headings
    catalog_table.heading("Title", text="Title")
    catalog_table.heading("Author", text="Author")
    catalog_table.heading("Genre", text="Genre")
    catalog_table.heading("Availability", text="Availability", anchor="center")
    catalog_table.heading("Action", text="Action", anchor="center")

    # Configure column widths
    catalog_table.column("Title", width=300, anchor="w")
    catalog_table.column("Author", width=200, anchor="w")
    catalog_table.column("Genre", width=100, anchor="center")
    catalog_table.column("Availability", width=100, stretch=False, anchor="center")
    catalog_table.column("Action", width=120, stretch=False, anchor="center")

    catalog_table.pack(fill="both", expand=True, padx=15, pady=15)

    # --- Data Population and Action Binding ---

    def handle_borrow_click(book_id, book_title, current_available):
        if current_available <= 0:
            messagebox.showerror("Unavailable", f"'{book_title}' is currently checked out.")
            return

        if messagebox.askyesno("Confirm Borrow", f"Do you want to borrow '{book_title}'?"):
            # Call the external logic handler provided by the main app
            borrow_logic_cmd(book_id, current_student_name)

    def refresh_catalog():
        catalog_table.delete(*catalog_table.get_children())

        for book in MOCK_CATALOG_BOOKS:
            book_id = book['id']
            available = book['available']
            status_text = f"{available} available" if available > 0 else "Unavailable"

            # The action button requires complex handling, as we can't embed widgets.
            # We insert the data and rely on tags/events for clicks.
            catalog_table.insert(
                "",
                "end",
                iid=book_id,
                values=(
                    book["title"],
                    book["author"],
                    book["genre"],
                    status_text,
                    "Borrow" if available > 0 else "---"
                ),
                tags=('available' if available > 0 else 'unavailable', book_id)
            )

        # Apply visual tags
        catalog_table.tag_configure('unavailable', foreground='#e74c3c')
        catalog_table.tag_configure('available', foreground='#2ecc71')

    # Handler for clicking the 'Borrow' text/button area
    def catalog_click_handler(event):
        """Handles click events in the Action column."""
        item_id = catalog_table.identify_row(event.y)
        column_id = catalog_table.identify_column(event.x)

        if item_id and column_id == '#5':  # Check if click is in the Action column (#5)
            item_values = catalog_table.item(item_id, 'values')
            book_id = item_id  # We used the ID as iid during insertion
            book_title = item_values[0]
            current_available = int(item_values[3].split()[0]) if 'available' in item_values[3] else 0

            if current_available > 0:
                handle_borrow_click(book_id, book_title, current_available)

    catalog_table.bind('<ButtonRelease-1>', catalog_click_handler)

    refresh_catalog()

    return frame