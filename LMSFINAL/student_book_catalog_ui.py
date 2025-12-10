# student_book_catalog_ui.py
import tkinter as tk
from tkinter import ttk, messagebox
from api_client import get_books


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
    
    # Placeholder logic for search
    def on_search_focus_in(event):
        if search_entry.get() == "Search by title or author...":
            search_entry.delete(0, tk.END)
            search_entry.config(fg="#000000")
    
    def on_search_focus_out(event):
        if not search_entry.get():
            search_entry.insert(0, "Search by title or author...")
            search_entry.config(fg="#a0a0a0")
    
    search_entry.config(fg="#a0a0a0")
    search_entry.bind("<FocusIn>", on_search_focus_in)
    search_entry.bind("<FocusOut>", on_search_focus_out)

    # ---------------- MAIN TABLE/LIST VIEW ----------------

    table_card = tk.Frame(frame, bg="white", bd=1, relief="solid")
    table_card.pack(fill="both", expand=True, padx=30, pady=(0, 30))

    # Create a scrollable frame for the book list
    canvas = tk.Canvas(table_card, bg="white", highlightthickness=0)
    scrollbar = tk.Scrollbar(table_card, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="white")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True, padx=15, pady=15)
    scrollbar.pack(side="right", fill="y")

    # Enable mouse wheel scrolling
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    canvas.bind_all("<MouseWheel>", on_mousewheel)

    # --- Data Population and Action Binding ---

    def handle_borrow_click(book_id, book_title):
        # Call the external logic handler provided by the main app
        try:
            # ensure book_id is int when possible
            try:
                bid = int(book_id)
            except Exception:
                bid = book_id
            borrow_logic_cmd(bid, current_student_name)
        except Exception as e:
            messagebox.showerror('Error', f'Failed to borrow: {e}')

    def refresh_catalog(search_term=""):
        # Clear existing widgets
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        
        try:
            books = get_books()
        except Exception as e:
            tk.Label(scrollable_frame, text=f"Error loading books: {e}", bg="white", fg="#e74c3c",
                    font=("Segoe UI", 11)).pack(pady=20)
            return

        # Filter books based on search term
        if search_term and search_term != "Search by title or author...":
            search_lower = search_term.lower()
            books = [b for b in books if 
                     search_lower in b.get('title', '').lower() or 
                     search_lower in b.get('author', '').lower() or
                     search_lower in b.get('category', '').lower()]

        if not books:
            tk.Label(scrollable_frame, text="No books found.", bg="white", fg="#7f8c8d",
                    font=("Segoe UI", 12)).pack(pady=20)
            return

        # Header row
        header_row = tk.Frame(scrollable_frame, bg="#f5f7fa", height=40)
        header_row.pack(fill="x", pady=(0, 10))
        
        tk.Label(header_row, text="Title", bg="#f5f7fa", fg="#2c3e50", font=("Segoe UI", 11, "bold"), width=30, anchor="w").pack(side="left", padx=10)
        tk.Label(header_row, text="Author", bg="#f5f7fa", fg="#2c3e50", font=("Segoe UI", 11, "bold"), width=20, anchor="w").pack(side="left", padx=10)
        tk.Label(header_row, text="Genre", bg="#f5f7fa", fg="#2c3e50", font=("Segoe UI", 11, "bold"), width=15, anchor="center").pack(side="left", padx=10)
        tk.Label(header_row, text="Availability", bg="#f5f7fa", fg="#2c3e50", font=("Segoe UI", 11, "bold"), width=12, anchor="center").pack(side="left", padx=10)
        tk.Label(header_row, text="Action", bg="#f5f7fa", fg="#2c3e50", font=("Segoe UI", 11, "bold"), width=10, anchor="center").pack(side="left", padx=10)

        for book in books:
            book_id = book.get('id')
            available = book.get('available', book.get('quantity', 0))
            
            # Book row
            book_row = tk.Frame(scrollable_frame, bg="white", height=50)
            book_row.pack(fill="x", pady=5)
            
            # Make row clickable (double-click)
            def make_double_click_handler(bid, btitle, avail):
                def handler(event):
                    if avail > 0:
                        handle_borrow_click(bid, btitle)
                    else:
                        messagebox.showinfo("Unavailable", f"'{btitle}' is currently unavailable.")
                return handler
            
            book_row.bind('<Double-Button-1>', make_double_click_handler(book_id, book.get("title", ""), available))
            
            # Title
            title_label = tk.Label(book_row, text=book.get("title", ""), bg="white", fg="#2c3e50", 
                                  font=("Segoe UI", 10), width=30, anchor="w")
            title_label.pack(side="left", padx=10)
            title_label.bind('<Double-Button-1>', make_double_click_handler(book_id, book.get("title", ""), available))
            
            # Author
            author_label = tk.Label(book_row, text=book.get("author", ""), bg="white", fg="#7f8c8d", 
                                   font=("Segoe UI", 10), width=20, anchor="w")
            author_label.pack(side="left", padx=10)
            author_label.bind('<Double-Button-1>', make_double_click_handler(book_id, book.get("title", ""), available))
            
            # Category
            category_label = tk.Label(book_row, text=book.get("category", ""), bg="white", fg="#7f8c8d", 
                                     font=("Segoe UI", 10), width=15, anchor="center")
            category_label.pack(side="left", padx=10)
            category_label.bind('<Double-Button-1>', make_double_click_handler(book_id, book.get("title", ""), available))
            
            # Availability
            avail_color = "#2ecc71" if available > 0 else "#e74c3c"
            status_text = f"{available} available" if available > 0 else "Unavailable"
            avail_label = tk.Label(book_row, text=status_text, bg="white", fg=avail_color, 
                                  font=("Segoe UI", 10, "bold"), width=12, anchor="center")
            avail_label.pack(side="left", padx=10)
            avail_label.bind('<Double-Button-1>', make_double_click_handler(book_id, book.get("title", ""), available))
            
            # Borrow Button
            if available > 0:
                borrow_btn = tk.Button(
                    book_row,
                    text="Borrow",
                    command=lambda bid=book_id, btitle=book.get("title", ""): handle_borrow_click(bid, btitle),
                    bg="#5d5fef",
                    fg="white",
                    font=("Segoe UI", 9, "bold"),
                    bd=0,
                    padx=15,
                    pady=5,
                    activebackground="#4a4cce",
                    relief="flat",
                    cursor="hand2"
                )
                borrow_btn.pack(side="left", padx=10)
            else:
                unavail_label = tk.Label(book_row, text="---", bg="white", fg="#7f8c8d", 
                                        font=("Segoe UI", 10), width=10, anchor="center")
                unavail_label.pack(side="left", padx=10)
            
            # Separator
            ttk.Separator(scrollable_frame, orient='horizontal').pack(fill='x', padx=10, pady=2)
    
    # Bind search functionality
    def on_search_change(event):
        search_term = search_entry.get()
        refresh_catalog(search_term)
    
    search_entry.bind("<KeyRelease>", on_search_change)

    refresh_catalog()

    return frame