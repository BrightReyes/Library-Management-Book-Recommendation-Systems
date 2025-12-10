# book_management_ui.py
import tkinter as tk
from tkinter import ttk, messagebox

# This UI now uses the Django REST backend as the single source of truth.
from api_client import get_books, create_book, update_book, delete_book

# Variable to hold the reference to the ttk.Treeview widget
book_management_table = None



# Add Book Function (uses API)
def add_book_to_db(data):
    payload = {
        'title': data['Title'],
        'author': data['Author'],
        'isbn': data['ISBN'],
        'category': data['Category'],
        'quantity': int(data['Quantity']),
        'available': int(data['Quantity']),
        'description': data.get('Description', ''),
        'cover_url': data.get('Cover Image URL', ''),
    }
    try:
        create_book(payload)
        if book_management_table:
            refresh_book_table()
        messagebox.showinfo("Success", f"Book '{data['Title']}' successfully added.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add book: {e}")


# Delete Book Function (uses API)
def delete_book_from_db(book_id, title):
    try:
        delete_book(book_id)
        refresh_book_table()
        messagebox.showinfo("Deleted", f"Book '{title}' deleted.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to delete book: {e}")

# Edit Book Modal (uses API)
def edit_book_modal(parent, book_data):
    # Open a simple modal to edit book fields and save via API
    win = tk.Toplevel(parent)
    win.title("Edit Book")
    win.config(bg="white", padx=20, pady=20)
    win.geometry("520x420")
    win.transient(parent)
    win.grab_set()

    entries = {}

    def create_label_entry(parent, text, default):
        tk.Label(parent, text=text, bg='white').pack(anchor='w')
        e = tk.Entry(parent)
        e.insert(0, default)
        e.pack(fill='x', pady=5)
        entries[text] = e

    create_label_entry(win, 'Title', book_data.get('title', ''))
    create_label_entry(win, 'Author', book_data.get('author', ''))
    create_label_entry(win, 'ISBN', book_data.get('isbn', ''))
    create_label_entry(win, 'Category', book_data.get('category', ''))
    create_label_entry(win, 'Quantity', str(book_data.get('quantity', 1)))

    def save():
        payload = {
            'title': entries['Title'].get(),
            'author': entries['Author'].get(),
            'isbn': entries['ISBN'].get(),
            'category': entries['Category'].get(),
            'quantity': int(entries['Quantity'].get()),
            'available': int(entries['Quantity'].get()),
        }
        try:
            update_book(book_data['id'], payload)
            refresh_book_table()
            win.destroy()
            messagebox.showinfo('Saved', 'Book updated successfully')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to update book: {e}')

    tk.Button(win, text='Save', command=save, bg='#2c3e50', fg='white').pack(pady=10)
    # For a full implementation, this would open a Toplevel window pre-filled with book_data.

# 2. NEW REFRESH FUNCTION with search and sort support
_current_sort_column = None
_current_sort_reverse = False
_search_term = ""
_category_filter = "All Categories"

def refresh_book_table(search_term="", category_filter="All Categories"):
    global book_management_table, _search_term, _category_filter
    _search_term = search_term
    _category_filter = category_filter
    
    if not book_management_table:
        return
    try:
        books = get_books()
    except Exception as e:
        messagebox.showerror('Error', f'Failed to load books: {e}')
        return

    # Apply search filter
    if search_term and search_term != "Search by title, author, or ISBN...":
        search_lower = search_term.lower()
        books = [b for b in books if 
                 search_lower in b.get('title', '').lower() or
                 search_lower in b.get('author', '').lower() or
                 search_lower in b.get('isbn', '').lower()]
    
    # Apply category filter
    if category_filter and category_filter != "All Categories":
        books = [b for b in books if b.get('category', '') == category_filter]
    
    # Apply current sort if any
    if _current_sort_column:
        books = sorted(books, key=lambda x: x.get(_current_sort_column, ''), reverse=_current_sort_reverse)

    book_management_table.delete(*book_management_table.get_children())
    for book in books:
        tree_id = str(book['id'])
        book_management_table.insert(
            '', 'end', iid=tree_id,
            values=(
                book.get('title', ''),
                book.get('author', ''),
                book.get('isbn', ''),
                book.get('category', ''),
                book.get('quantity', 0),
                book.get('available', 0),
                '✏️  🗑️'
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
        add_book_to_db(data)

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

    # Placeholder logic for search
    def on_search_focus_in(event):
        if search_entry.get() == "Search by title, author, or ISBN...":
            search_entry.delete(0, tk.END)
            search_entry.config(fg="#000000")
    
    def on_search_focus_out(event):
        if not search_entry.get():
            search_entry.insert(0, "Search by title, author, or ISBN...")
            search_entry.config(fg="#a0a0a0")
    
    search_entry.config(fg="#a0a0a0")
    search_entry.bind("<FocusIn>", on_search_focus_in)
    search_entry.bind("<FocusOut>", on_search_focus_out)
    
    # Bind real-time search
    def on_search_change(event):
        search_text = search_entry.get()
        cat_value = category.get()
        refresh_book_table(search_text, cat_value)
    
    search_entry.bind("<KeyRelease>", on_search_change)

    category = ttk.Combobox(search_frame, values=["All Categories", "Fiction", "Science Fiction", "Romance"],
                            state="readonly", width=20)
    category.set("All Categories")
    category.pack(side="right", padx=10)
    
    # Bind category change
    def on_category_change(event):
        search_text = search_entry.get()
        cat_value = category.get()
        refresh_book_table(search_text, cat_value)
    
    category.bind("<<ComboboxSelected>>", on_category_change)

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

    # Sort function
    def sort_by_column(col):
        global _current_sort_column, _current_sort_reverse
        if _current_sort_column == col:
            _current_sort_reverse = not _current_sort_reverse
        else:
            _current_sort_column = col
            _current_sort_reverse = False
        refresh_book_table(_search_term, _category_filter)

    # Column mapping for sorting
    col_map = {
        "Title": "title",
        "Author": "author",
        "ISBN": "isbn",
        "Category": "category",
        "Qty": "quantity",
        "Available": "available"
    }

    table.heading("Title", text="Title ↕", command=lambda: sort_by_column("title"))
    table.heading("Author", text="Author ↕", command=lambda: sort_by_column("author"))
    table.heading("ISBN", text="ISBN ↕", command=lambda: sort_by_column("isbn"))
    table.heading("Category", text="Category ↕", command=lambda: sort_by_column("category"))
    table.heading("Qty", text="Quantity ↕", command=lambda: sort_by_column("quantity"))
    table.heading("Available", text="Available ↕", command=lambda: sort_by_column("available"))
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

        if item_id and column_id == '#7':  # Check if click is in the Actions column (#7)
            item_values = table.item(item_id, 'values')
            book_title = item_values[0]
            # We stored the book id as the iid when inserting
            try:
                book_id = int(item_id)
            except Exception:
                return
            # Build a simple book_data dict from the row values
            book_data = {
                'id': book_id,
                'title': item_values[0],
                'author': item_values[1],
                'isbn': item_values[2],
                'category': item_values[3],
                'quantity': int(item_values[4]) if item_values[4] else 0,
                'available': int(item_values[5]) if item_values[5] else 0,
            }

            # Determine which icon was clicked based on column position (Rough estimate)
            # You would normally calculate the precise pixel offset here.

            x_offset = table.winfo_x() + table.column('#7', 'width') - (table.column('#7', 'width') / 2)

            # We assume a click on the left half of the column is EDIT, right half is DELETE
            if event.x < x_offset:
                # Edit action
                edit_book_modal(app_root, book_data)
            else:
                # Delete action
                if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{book_title}'?"):
                    delete_book_from_db(book_id, book_title)


    table.bind('<ButtonRelease-1>', item_click_handler)


    # ---------------- LOAD INITIAL DATA ----------------
    refresh_book_table()

    return frame