# student_portal_app.py
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from datetime import timedelta
from student_book_catalog_ui import create_book_catalog_ui
from my_loans_ui import create_my_loans_ui
from borrowing_history_ui import create_borrowing_history_ui
from api_client import get_loans, get_books


def get_stats_for_student(student_id, loans):
    student_loans = [l for l in loans if l.get('user') == student_id]
    borrowed_count = len([l for l in student_loans if l.get('status') == 'borrowed'])
    returned_count = len([l for l in student_loans if l.get('status') == 'returned'])
    
    overdue = 0
    total_fines = 0.0
    for l in student_loans:
        total_fines += float(l.get('fine', 0) or 0)
        if l.get('status') == 'borrowed' and l.get('due_date'):
            try:
                due = datetime.datetime.fromisoformat(l['due_date'])
                if due.date() < datetime.datetime.now().date():
                    overdue += 1
            except Exception:
                pass
    
    return {
        'borrowed': borrowed_count,
        'fines': f"${total_fines:.2f}",
        'reads': returned_count,
        'overdue': overdue
    }


def modern_button_plain(parent, text, cmd):
    """A helper function for the primary student button style."""
    return tk.Button(
        parent, text=text, command=cmd,
        bg="#5d5fef", fg="white",
        font=("Segoe UI", 12, "bold"),
        bd=0, padx=15, pady=8,
        activebackground="#4a4cce",
        relief="flat"
    )


class StudentPortalApp(tk.Tk):
    def __init__(self, user_info=None):
        super().__init__()
        self.title("Library Portal - Student Access")
        self.geometry("1200x800")
        self.config(bg="#f5f7fa")
        self.resizable(True, True)

        # Use authenticated user info
        if user_info:
            self.current_student_id = user_info.get('id')
            self.current_student_name = user_info.get('username', 'Student')
        else:
            self.current_student_id = None
            self.current_student_name = 'Student'

        # Store button references for reliable navigation
        self.nav_buttons = {}

        # --- Frames for different views ---
        self.dashboard_frame = tk.Frame(self, bg="#f5f7fa")
        self.book_catalog_frame = tk.Frame(self, bg="#f5f7fa")
        self.my_loans_frame = tk.Frame(self, bg="#f5f7fa")
        self.history_frame = tk.Frame(self, bg="#f5f7fa") # Target Frame

        self.active_frame = None

        self._create_sidebar()
        self._create_content_area()

        # Start on the Dashboard
        self.show_frame(self.dashboard_frame, self.nav_buttons.get(self.dashboard_frame))

    def _create_sidebar(self):
        sidebar_width = 240
        sidebar = tk.Frame(self, width=sidebar_width, bg="#FFFFFF", relief="flat", bd=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Header
        header_frame = tk.Frame(sidebar, bg="#FFFFFF")
        header_frame.pack(fill="x", pady=(20, 30))
        tk.Label(header_frame, text="Library Portal", fg="#5d5fef", bg="white", font=("Segoe UI", 16, "bold")).pack(
            pady=5)
        tk.Label(header_frame, text="Student Access", fg="#7f8c8d", bg="white", font=("Segoe UI", 10)).pack(pady=(0, 5))

        # Navigation Frame
        nav_frame = tk.Frame(sidebar, bg="#FFFFFF")
        nav_frame.pack(fill="x", pady=10)

        # Navigation Buttons
        self.dashboard_btn = self._add_nav_btn("Dashboard", self.dashboard_frame, "📊", nav_frame)
        self.nav_buttons[self.dashboard_frame] = self.dashboard_btn

        self.book_catalog_btn = self._add_nav_btn("Book Catalog", self.book_catalog_frame, "🔍", nav_frame)
        self.nav_buttons[self.book_catalog_frame] = self.book_catalog_btn

        self.my_loans_btn = self._add_nav_btn("My Loans", self.my_loans_frame, "🧾", nav_frame)
        self.nav_buttons[self.my_loans_frame] = self.my_loans_btn

        self.history_btn = self._add_nav_btn("Borrowing History", self.history_frame, "🕒", nav_frame)
        self.nav_buttons[self.history_frame] = self.history_btn

        # Bottom User/Logout Frame
        bottom_frame = tk.Frame(sidebar, bg="#FFFFFF", bd=0, highlightthickness=1, highlightbackground="#e0e0e0")
        bottom_frame.pack(side="bottom", fill="x", pady=(10, 0))

        user_id_display = f"ID: {self.current_student_id}" if self.current_student_id else "Student"
        tk.Label(
            bottom_frame,
            text=f"👤 {self.current_student_name}\n{user_id_display}",
            fg="#2c3e50",
            bg="white",
            font=("Segoe UI", 10, "bold"),
            pady=10
        ).pack(fill="x")

        tk.Button(
            bottom_frame,
            text="➜ Logout",
            command=self.logout,
            bg="#ecf0f1",
            fg="#2c3e50",
            activebackground="#bdc3c7",
            anchor="w",
            bd=0,
            font=("Segoe UI", 12, "bold"),
            pady=10
        ).pack(fill="x")

    def _add_nav_btn(self, text, frame, icon, parent_frame):
        btn = tk.Button(
            parent_frame,
            text=f"  {icon} {text}",
            command=lambda: self.show_frame(frame, btn),
            bg="white",
            fg="#2c3e50",
            activebackground="#ecf0f1",
            activeforeground="#2c3e50",
            bd=0,
            font=("Segoe UI", 12),
            anchor="w",
            padx=15,
            pady=10
        )
        btn.pack(fill="x", pady=2)
        return btn

    def logout(self):
        """Logout and return to login screen."""
        from api_client import set_token
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            set_token(None)  # Clear the authentication token
            self.destroy()
            import login
            login.open_login_window()

    def student_borrow_book(self, book_id, student_name):
        """Handles the business logic for borrowing a book and refreshes the UI."""
        from api_client import create_loan

        try:
            payload = {'book': int(book_id)}
            create_loan(payload)
            messagebox.showinfo("Success", f"Book borrowed successfully!")
            # Refresh all views to show updated data
            self._load_dashboard_content(self.dashboard_frame)
            self.load_catalog_content(self.book_catalog_frame)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to borrow book: {e}")

    def show_frame(self, frame, btn=None):

        # 1. Deselect old button and hide old frame
        if self.active_frame and self.active_frame_btn:
            self.active_frame_btn.config(bg="white", font=("Segoe UI", 12))
            self.active_frame.place_forget()

        # 2. Update active state
        self.active_frame = frame
        self.active_frame_btn = btn

        if btn:
            btn.config(bg="#ecf0f1", font=("Segoe UI", 12, "bold"))

        # 3. Position and raise new frame
        frame.place(relwidth=1, relheight=1, x=240, width=-240)
        frame.tkraise()

        # 4. Load content on demand
        if frame == self.dashboard_frame:
            self._load_dashboard_content(frame)
        elif frame == self.book_catalog_frame:
            self.load_catalog_content(frame)
        elif frame == self.my_loans_frame:
            create_my_loans_ui(frame, self.current_student_id)
        elif frame == self.history_frame:
            # *** FIX: Load the external Borrowing History component ***
            create_borrowing_history_ui(frame, self.current_student_id)

    def _create_content_area(self):
        # The content frames are created and positioned in show_frame.
        pass

    def _load_dashboard_content(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

        # Create canvas with scrollbar for scrolling functionality
        canvas = tk.Canvas(frame, bg="#f5f7fa", highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
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

        # ---------------- MAIN HEADER ----------------
        tk.Label(scrollable_frame, text=f"Welcome back, {self.current_student_name}!", font=("Segoe UI", 28, "bold"), bg="#f5f7fa",
             fg="#2c3e50").pack(anchor="w", padx=30, pady=(20, 5))
        tk.Label(scrollable_frame, text="Here's your library overview", font=("Segoe UI", 12), bg="#f5f7fa", fg="#7f8c8d").pack(
            anchor="w", padx=30, pady=(0, 20))

        # ---------------- STATS ROW ----------------
        stats_row = tk.Frame(scrollable_frame, bg="#f5f7fa", padx=20)
        stats_row.pack(fill="x", pady=10)

        # ... (create_stat_card definitions remain here) ...
        def create_stat_card(parent, title, value, detail, icon, bg_color):
            card = tk.Frame(parent, bg="#FFFFFF", padx=15, pady=10, relief="solid", bd=1)
            card.pack(side="left", padx=10, fill="x", expand=True)

            # Icon Frame
            icon_frame = tk.Frame(card, bg=bg_color, width=40, height=40)
            icon_frame.pack(side="right", padx=(10, 0))
            icon_frame.pack_propagate(False)
            tk.Label(icon_frame, text=icon, bg=bg_color, fg="white", font=("Segoe UI", 16)).pack(expand=True)

            # Text Content
            tk.Label(card, text=title, bg="white", fg="#7f8c8d", font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 2))
            tk.Label(card, text=value, bg="white", fg="#2c3e50", font=("Segoe UI", 24, "bold")).pack(anchor="w")
            tk.Label(card, text=detail, bg="white", fg="#7f8c8d", font=("Segoe UI", 10)).pack(anchor="w", pady=(5, 0))

            return card

        # Load loans for current student and compute stats
        try:
            loans = get_loans()
        except Exception:
            loans = []

        stats = get_stats_for_student(self.current_student_id, loans) if self.current_student_id else {'borrowed': 0, 'fines': "$0.00", 'reads': 0, 'overdue': 0}

        create_stat_card(stats_row, "Books Borrowed", stats["borrowed"], "Currently checked out", "📘", "#5d5fef")
        create_stat_card(stats_row, "Pending Fines", stats["fines"], "All clear!", "⏰", "#2ecc71")
        create_stat_card(stats_row, "Books Read", stats["reads"], "This year", "📚", "#9b59b6")

        # ---------------- MAIN CONTENT WRAPPER ----------------
        main_wrapper = tk.Frame(scrollable_frame, bg="#f5f7fa", padx=30, pady=10)
        main_wrapper.pack(fill="both", expand=True)

        # --- Currently Borrowed Section ---
        borrowed_card = tk.Frame(main_wrapper, bg="white", bd=1, relief="solid")
        borrowed_card.pack(fill="x", pady=(0, 30))

        # ... (Borrowed header and list remains the same) ...
        borrowed_header = tk.Frame(borrowed_card, bg="white", padx=15, pady=10)
        borrowed_header.pack(fill="x")
        tk.Label(borrowed_header, text="Currently Borrowed", font=("Segoe UI", 14, "bold"), bg="white",
                 fg="#2c3e50").pack(side="left")
        tk.Button(borrowed_header, text="View All", bg="#ecf0f1", bd=0, font=("Segoe UI", 10)).pack(side="right",
                                                                                                    padx=5)

        tk.Label(borrowed_card, text="Books you have checked out", font=("Segoe UI", 10), bg="white", fg="#7f8c8d",
                 padx=15).pack(anchor="w", pady=(0, 5))

        borrowed_list = tk.Frame(borrowed_card, bg="white", padx=15, pady=10)
        borrowed_list.pack(fill="x")

        # Display actual borrowed loans for the student
        try:
            loans = get_loans()
        except Exception:
            loans = []

        student_loans = [l for l in loans if l.get('user') == self.current_student_id]

        for l in student_loans:
            item_frame = tk.Frame(borrowed_list, bg="white", padx=10, pady=10)
            item_frame.pack(fill="x", pady=5)

            tk.Label(item_frame, text="📘", fg="#5d5fef", bg="white", font=("Segoe UI", 16)).pack(side="left", padx=5)

            text_frame = tk.Frame(item_frame, bg="white")
            text_frame.pack(side="left", fill="x", expand=True)

            title = l.get('book_title') or l.get('book', '')
            author = l.get('book_author', '')

            tk.Label(text_frame, text=title, bg="white", fg="#2c3e50", font=("Segoe UI", 11, "bold")).pack(anchor="w")
            tk.Label(text_frame, text=author, bg="white", fg="#7f8c8d", font=("Segoe UI", 9)).pack(anchor="w")

            due_frame = tk.Frame(item_frame, bg="white")
            due_frame.pack(side="right", padx=10)

            due_date = l.get('due_date') or ''
            days_remaining = ''
            try:
                if due_date:
                    due_dt = datetime.datetime.fromisoformat(due_date)
                    delta = (due_dt.date() - datetime.datetime.now().date()).days
                    days_remaining = f"{delta} days remaining" if delta >= 0 else f"{abs(delta)} days overdue"
            except Exception:
                pass

            tk.Label(due_frame, text=f"Due {due_date}" if due_date else "", bg="white", fg="#7f8c8d", font=("Segoe UI", 10)).pack(anchor="e")
            tk.Label(due_frame, text=days_remaining, bg="white", fg="#e74c3c", font=("Segoe UI", 9, "bold")).pack(anchor="e")

        ttk.Separator(borrowed_card, orient='horizontal').pack(fill='x', padx=15, pady=5)

        # --- Browse Catalog Section (Replaces Recommended for You) ---
        browse_card = tk.Frame(main_wrapper, bg="white", bd=1, relief="solid")
        browse_card.pack(fill="x", pady=(10, 0))

        browse_header = tk.Frame(browse_card, bg="white", padx=15, pady=10)
        browse_header.pack(fill="x")
        tk.Label(browse_header, text="Browse Library", font=("Segoe UI", 14, "bold"), bg="white", fg="#2c3e50").pack(
            side="left")

        tk.Button(browse_header, text="View All", bg="#ecf0f1", bd=0, font=("Segoe UI", 10)).pack(side="right", padx=5)

        tk.Label(browse_card, text="Search for new books to check out", font=("Segoe UI", 10), bg="white", fg="#7f8c8d",
                 padx=15).pack(anchor="w", pady=(0, 15))

        # Browse Button Row
        browse_btn_frame = tk.Frame(browse_card, bg="white", pady=10)
        browse_btn_frame.pack(fill="x")

        def switch_to_catalog():
            # Find the correct nav button for Book Catalog and trigger switch
            catalog_btn = self.nav_buttons.get(self.book_catalog_frame)
            if catalog_btn:
                self.show_frame(self.book_catalog_frame, catalog_btn)

        # Central button
        modern_button_plain(
            browse_btn_frame,
            "📚 Browse Catalog",
            switch_to_catalog
        ).pack(pady=10)

    def load_catalog_content(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

        # Call the external catalog UI creator
        create_book_catalog_ui(
            frame,
            self.current_student_name,
            self.student_borrow_book  # Use the internal wrapper method
        )

    def _load_simple_content(self, frame, title, subtitle):
        # Clears frame and displays basic header (Placeholder for other tabs)
        for widget in frame.winfo_children():
            widget.destroy()

        tk.Label(frame, text=title, font=("Segoe UI", 28, "bold"), bg="#f5f7fa", fg="#2c3e50").pack(anchor="w", padx=30,
                                                                                                    pady=(20, 5))
        tk.Label(frame, text=subtitle, font=("Segoe UI", 12), bg="#f5f7fa", fg="#7f8c8d").pack(anchor="w", padx=30,
                                                                                               pady=(0, 20))


if __name__ == "__main__":
    app = StudentPortalApp()
    app.mainloop()