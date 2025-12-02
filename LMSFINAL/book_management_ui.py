# book_management_ui.py
import tkinter as tk
from tkinter import ttk, messagebox

# --- Global Variables and CRUD Functions ---

# SAMPLE DATA ONLY — This is now a global variable that the app modifies
sample_books = [
    {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "isbn": "978-0-7432-7356-5",
        "category": "Fiction",
        "quantity": 5,
        "available": 3
    },
    {
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "isbn": "978-0-06-112008-4",
        "category": "Fiction",
        "quantity": 4,
        "available": 2
    },
    {
        "title": "1984",
        "author": "George Orwell",
        "isbn": "978-0-452-28423-4",
        "category": "Science Fiction",
        "quantity": 6,
        "available": 6
    },
]

# Variable to hold the reference to the ttk.Treeview widget
book_management_table = None


# 1. UPDATED MOCK ADD FUNCTION
def mock_add_book_to_db(data):
    """Adds the new book data to the global list and refreshes the UI."""
    global sample_books
    global book_management_table

    new_book = {
        "title": data["Title"],
        "author": data["Author"],
        "isbn": data["ISBN"],
        "category": data["Category"],
        "quantity": data["Quantity"],  # Now an int
        "available": data["Quantity"]
    }

    sample_books.append(new_book)

    if book_management_table:
        refresh_book_table()

    messagebox.showinfo("Success", f"Book '{data['Title']}' successfully added and displayed.")


# Mock Delete Function (for action buttons)
def mock_delete_book(title):
    global sample_books
    sample_books = [b for b in sample_books if b["title"] != title]
    refresh_book_table()
    messagebox.showinfo("Deleted", f"Book '{title}' deleted from mock list.")

# Mock Edit Function (opens a new window, simplified logic)
def mock_edit_book_modal(parent, book_data):
    messagebox.showinfo("Edit", f"Opening edit modal for: {book_data['title']}. (Actual edit logic would go here)")
    # For a full implementation, this would open a Toplevel window pre-filled with book_data.

# 2. NEW REFRESH FUNCTION
def refresh_book_table():
    """Clears and re-populates the book table with the current global data."""
    global book_management_table
    global sample_books

    if book_management_table:
        # Clear existing entries
        book_management_table.delete(*book_management_table.get_children())

        # Insert all current books
        for i, book in enumerate(sample_books):
            # We use the title as a unique ID for mock purposes
            tree_id = book["title"]

            book_management_table.insert(
                "",
                "end",
                iid=tree_id, # Set the item ID to the book title for easy lookup
                values=(
                    book["title"],
                    book["author"],
                    book["isbn"],
                    book["category"],
                    book["quantity"],
                    book["available"],
                    "✏️  🗑️" # Placeholder text for visual buttons
                )
            )


# --- Helper Function for Consistent Button Styling ---
def modern_button(parent, text, color, cmd):
    """A helper function for consistent button styling."""
    return tk.Button(
        parent, text=text, command=cmd,
        bg=color, fg="white",
        font=("Segoe UI", 11, "bold"),
        bd=0, padx=18, pady=10,
        activebackground=color,
        activeforeground="white",
        relief="flat"
    )


# ----------------- ADD NEW BOOK MODAL -----------------
# ... (open_add_book_modal remains unchanged) ...
def open_add_book_modal(parent):
    # ... (code omitted for brevity, assumes functional modal) ...
    win = tk.Toplevel(parent)
    win.title("Add New Book")
    win.config(bg="white", padx=20, pady=20)
    win.geometry("550x580")
    win.transient(parent)
    win.grab_set()

    # --- Header ---
    tk.Label(
        win,
        text="Add New Book",
        font=("Segoe UI", 18, "bold"),
        bg="white",
        fg="#2c3e50"
    ).pack(anchor="w", pady=(0, 5))

    tk.Label(
        win,
        text="Fill in the details to add a new book to the library",
        font=("Segoe UI", 10),
        bg="white",
        fg="#7f8c8d"
    ).pack(anchor="w", pady=(0, 20))

    # --- Input Fields Frame ---
    input_frame = tk.Frame(win, bg="white")
    input_frame.pack(fill="x")

    entries = {}
    labels = {
        "Title": "Enter book title",
        "Author": "Enter author name",
        "ISBN": "978-0-XXX-XXXXX-X",
        "Quantity": "Number of copies",
        "Description": "Enter book description",
        "Cover Image URL": "https://example.com/cover.jpg",
    }

    category_values = ["Fiction", "Non-Fiction", "Science", "History", "Memoir", "Dystopian"]

    def create_label_entry(parent, text, placeholder, row, col, is_required=True, is_wide=False, is_dropdown=False):
        # --- Placeholder Logic for Entry/Text Widgets ---
        def setup_placeholder_logic(widget, default_text, is_text_widget=False):
            def on_focus_in(event):
                current_text = widget.get("1.0", "end-1c").strip() if is_text_widget else widget.get()
                if current_text == default_text:
                    if is_text_widget:
                        widget.delete("1.0", tk.END)
                    else:
                        widget.delete(0, tk.END)
                    widget.config(fg="#000000")

            def on_focus_out(event):
                current_text = widget.get("1.0", "end-1c").strip() if is_text_widget else widget.get()
                if not current_text:
                    if is_text_widget:
                        widget.insert("1.0", default_text)
                    else:
                        widget.insert(0, default_text)
                    widget.config(fg="#a0a0a0")

            widget.bind("<FocusIn>", on_focus_in)
            widget.bind("<FocusOut>", on_focus_out)

        # --------------------------------------------------

        label_text = text + (" *" if is_required else "")
        tk.Label(parent, text=label_text, font=("Segoe UI", 10, "bold"), bg="white", fg="#2c3e50").grid(row=row * 2,
                                                                                                        column=col,
                                                                                                        sticky="w",
                                                                                                        pady=(10, 2))

        if is_dropdown:
            widget = ttk.Combobox(
                parent,
                values=category_values,
                state="readonly",
                width=25 if not is_wide else 58
            )
            widget.set("Select category")
        elif text == "Description":
            widget = tk.Text(parent, font=("Segoe UI", 10), height=4, bd=1, relief="solid")
            widget.insert("1.0", placeholder)
            widget.config(fg="#a0a0a0")
            setup_placeholder_logic(widget, placeholder, is_text_widget=True)
        else:
            widget = tk.Entry(parent, font=("Segoe UI", 10), bd=1, relief="solid", width=25 if not is_wide else 58)
            widget.insert(0, placeholder)
            widget.config(fg="#a0a0a0")
            setup_placeholder_logic(widget, placeholder, is_text_widget=False)

        widget.grid(row=row * 2 + 1, column=col, sticky="ew", padx=5, pady=(0, 10), columnspan=2 if is_wide else 1)
        entries[text] = widget

        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)

    # Row 0: Title and Author
    create_label_entry(input_frame, "Title", labels["Title"], 0, 0)
    create_label_entry(input_frame, "Author", labels["Author"], 0, 1)

    # Row 1: ISBN and Category
    create_label_entry(input_frame, "ISBN", labels["ISBN"], 1, 0)
    create_label_entry(input_frame, "Category", "Select category", 1, 1, is_dropdown=True)

    # Row 2: Quantity
    create_label_entry(input_frame, "Quantity", labels["Quantity"], 2, 0)

    # Row 3: Description (Wide)
    create_label_entry(input_frame, "Description", labels["Description"], 3, 0, is_required=False, is_wide=True)

    # Row 4: Cover Image URL (Wide)
    create_label_entry(input_frame, "Cover Image URL", labels["Cover Image URL"], 4, 0, is_required=False, is_wide=True)

    # --- Action Buttons ---
    btn_frame = tk.Frame(win, bg="white")
    btn_frame.pack(fill="x", pady=(20, 0))
    btn_frame.columnconfigure(0, weight=1)  # Spacer column

    def save_book():
        # Define placeholders for cleanup
        placeholders = {
            "Title": "Enter book title",
            "Author": "Enter author name",
            "ISBN": "978-0-XXX-XXXXX-X",
            "Quantity": "Number of copies",
            "Category": "Select category",
            "Description": "Enter book description",
            "Cover Image URL": "https://example.com/cover.jpg",
        }

        # 1. Retrieve Data using CAPITALIZED keys (matching entries dictionary)
        description_text = entries["Description"].get("1.0", tk.END).strip()
        cover_url_text = entries["Cover Image URL"].get()

        data = {
            "Title": entries["Title"].get(),
            "Author": entries["Author"].get(),
            "ISBN": entries["ISBN"].get(),
            "Category": entries["Category"].get(),
            "Quantity": entries["Quantity"].get(),
            "Description": description_text,
            "Cover Image URL": cover_url_text,
        }

        # 2. Validation and Data Cleanup
        required_fields = ["Title", "Author", "ISBN", "Quantity"]

        for key in required_fields:
            if data[key].strip() == placeholders[key] or not data[key].strip():
                messagebox.showerror("Validation Error", f"The '{key}' field is required.")
                return

        if data["Category"] == placeholders["Category"] or not data["Category"].strip():
            messagebox.showerror("Validation Error", "The 'Category' field is required.")
            return

        # Check Quantity is a valid positive integer
        try:
            quantity_val = int(data["Quantity"])
            if quantity_val <= 0:
                messagebox.showerror("Validation Error", "Quantity must be a positive whole number.")
                return
            data["Quantity"] = quantity_val  # Store as int
        except ValueError:
            messagebox.showerror("Validation Error", "Quantity must be a valid number.")
            return

        # Clean Optional Fields
        if data["Description"] == placeholders["Description"]:
            data["Description"] = ""

        if data["Cover Image URL"] == placeholders["Cover Image URL"]:
            data["Cover Image URL"] = ""

        # 3. Call DB Handler (This now updates the global list and table)
        mock_add_book_to_db(data)

        # 4. Close the window
        win.destroy()

    # Cancel Button
    cancel_btn = tk.Button(
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
    )
    cancel_btn.grid(row=0, column=1, padx=10, sticky="e")

    # Add Book Button
    add_btn = modern_button(btn_frame, "Add Book", "#2c3e50", save_book)
    add_btn.grid(row=0, column=2, sticky="e")

    tk.Label(btn_frame, text="", bg="white").grid(row=0, column=0, sticky="ew")


# ----------------- MAIN BOOK MANAGEMENT UI FUNCTION -----------------

def create_book_management_ui(parent_frame):
    global book_management_table  # Declare global access

    frame = tk.Frame(parent_frame, bg="#f5f7fa")
    frame.place(relwidth=1, relheight=1)
    app_root = parent_frame.winfo_toplevel() # Get reference to the root window for modals

    # ... (Header and Search Bar code omitted for brevity) ...
    header = tk.Frame(frame, bg="#f5f7fa")
    header.pack(fill="x", padx=20, pady=(10, 5))
    tk.Label(header, text="Book Management", font=("Segoe UI", 26, "bold"), bg="#f5f7fa", fg="#2c3e50").pack(anchor="w")
    tk.Label(header, text="Manage your library’s book collection", font=("Segoe UI", 12), bg="#f5f7fa",
             fg="#7f8c8d").pack(anchor="w")

    search_frame = tk.Frame(frame, bg="white", bd=1, relief="solid")
    search_frame.pack(fill="x", padx=20, pady=15)
    tk.Label(search_frame, text="🔍", bg="white", font=("Segoe UI", 12)).pack(side="left", padx=10)
    search_entry = tk.Entry(search_frame, font=("Segoe UI", 11), bg="white", bd=0)
    search_entry.pack(side="left", fill="x", expand=True, padx=5, pady=10)
    search_entry.insert(0, "Search by title, author, or ISBN...")

    category = ttk.Combobox(search_frame, values=["All Categories", "Fiction", "Science Fiction", "Romance"],
                            state="readonly", width=20)
    category.set("All Categories")
    category.pack(side="right", padx=10)

    # ---------------- ADD NEW BOOK BUTTON ----------------
    top_btn_frame = tk.Frame(frame, bg="#f5f7fa")
    top_btn_frame.pack(anchor="ne", padx=20, pady=5)

    tk.Button(
        top_btn_frame,
        text="➕ Add New Book",
        command=lambda: open_add_book_modal(app_root), # Use app_root reference
        bg="#5d5fef",
        fg="white",
        font=("Segoe UI", 11, "bold"),
        bd=0,
        padx=15,
        pady=7
    ).pack()

    # ---------------- MAIN TABLE CARD ----------------
    card = tk.Frame(frame, bg="white", bd=1, relief="solid")
    card.pack(fill="both", expand=True, padx=20, pady=(10, 20))

    tk.Label(
        card,
        text="All Books",
        font=("Segoe UI", 16, "bold"),
        bg="white",
        fg="#2c3e50"
    ).pack(anchor="w", padx=15, pady=10)

    # Table columns
    columns = ("Title", "Author", "ISBN", "Category", "Qty", "Available", "Actions")
    table = ttk.Treeview(card, columns=columns, show="headings", height=15)

    # **Crucial step: Store the table reference globally**
    book_management_table = table

    table.heading("Title", text="Title")
    table.heading("Author", text="Author")
    table.heading("ISBN", text="ISBN")
    table.heading("Category", text="Category")
    table.heading("Qty", text="Quantity")
    table.heading("Available", text="Available")
    table.heading("Actions", text="Actions")

    table.column("Title", width=200)
    table.column("Author", width=160)
    table.column("ISBN", width=150)
    table.column("Category", width=110)
    table.column("Qty", width=80, anchor="center")
    table.column("Available", width=80, anchor="center")
    table.column("Actions", width=100, anchor="center")

    table.pack(fill="both", expand=True, padx=15, pady=10)

    # ---------------- ACTION HANDLER BINDING ----------------
    def item_click_handler(event):
        """Handles click events in the actions column for Edit/Delete."""
        item_id = table.identify_row(event.y)
        column_id = table.identify_column(event.x)

        if item_id and column_id == '#7': # Check if click is in the Actions column (#7)
            item_values = table.item(item_id, 'values')
            book_title = item_values[0]

            # Find the mock book data
            book_data = next((b for b in sample_books if b['title'] == book_title), None)
            if not book_data: return

            # Determine which icon was clicked based on column position (Rough estimate)
            # You would normally calculate the precise pixel offset here.

            x_offset = table.winfo_x() + table.column('#7', 'width') - (table.column('#7', 'width') / 2)

            # We assume a click on the left half of the column is EDIT, right half is DELETE
            if event.x < x_offset:
                # Edit action
                mock_edit_book_modal(app_root, book_data)
            else:
                # Delete action
                if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{book_title}'?"):
                    mock_delete_book(book_title)


    table.bind('<ButtonRelease-1>', item_click_handler)


    # ---------------- LOAD INITIAL DATA ----------------
    refresh_book_table()

    return frame