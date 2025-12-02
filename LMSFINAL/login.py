import tkinter as tk
from tkinter import messagebox
from data import users
# --- IMPORT FINAL MODULES ---
import adminDashboardUI
import register
import student_portal_app  # Import the actual Student App class


def open_login_window():
    login = tk.Tk()
    login.title("Library System | Login")
    login.geometry("460x480")  # Increased height slightly for better spacing
    login.configure(bg="#eef1f6")  # Light gray background
    login.resizable(False, False)

    # Center window
    login.update_idletasks()
    width, height = 460, 480
    x = (login.winfo_screenwidth() // 2) - (width // 2)
    y = (login.winfo_screenheight() // 2) - (height // 2)
    login.geometry(f"{width}x{height}+{x}+{y}")

    # --- CARD FRAME (modern clean look) ---
    card = tk.Frame(
        login,
        bg="white",
        bd=0,
        highlightthickness=0
    )
    card.place(relx=0.5, rely=0.5, anchor="center", width=360, height=420)

    # Title
    tk.Label(
        card,
        text="Login",
        font=("Segoe UI", 24, "bold"),  # Enhanced font size
        bg="white"
    ).pack(pady=(30, 5))

    tk.Label(
        card,
        text="Enter your credentials to access your account",
        font=("Segoe UI", 10),
        fg="#7f8c8d",
        bg="white"
    ).pack(pady=(0, 30))

    # Username Label + Entry (Styled for clean modern look)
    tk.Label(card, text="Username", font=("Segoe UI", 10), bg="white").pack(anchor="w", padx=40)
    username_entry = tk.Entry(
        card, font=("Segoe UI", 11),
        width=30,
        bd=0,
        relief="flat",
        highlightthickness=1,
        highlightbackground="#bdc3c7",
        highlightcolor="#5d5fef"
    )
    username_entry.pack(pady=(3, 15))

    # Password Label + Entry (Styled for clean modern look)
    tk.Label(card, text="Password", font=("Segoe UI", 10), bg="white").pack(anchor="w", padx=40)
    password_entry = tk.Entry(
        card, font=("Segoe UI", 11),
        width=30, show="*",
        bd=0,
        relief="flat",
        highlightthickness=1,
        highlightbackground="#bdc3c7",
        highlightcolor="#5d5fef"
    )
    password_entry.pack(pady=(3, 5))

    # Remember Me + Forgot Password Row
    row = tk.Frame(card, bg="white")
    row.pack(fill="x", padx=40, pady=(5, 15))

    remember_var = tk.BooleanVar()
    tk.Checkbutton(
        row, text="Remember me",
        variable=remember_var,
        bg="white",
        font=("Segoe UI", 10),
        bd=0,
        highlightthickness=0,
        selectcolor="white"
    ).pack(side="left")

    # Login logic (MODIFIED FOR STUDENT PORTAL LAUNCH)
    def login_user():
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        if username in users and users[username]["password"] == password:
            role = users[username]["role"]

            # --- LAUNCH THE CORRECT PORTAL ---
            login.destroy()

            if role == "admin":
                adminDashboardUI.open_main_ui(username)
            elif role == "student":
                # *** CORRECT INTEGRATION ***
                app = student_portal_app.StudentPortalApp()
                app.mainloop()
            else:
                messagebox.showerror("Error", "Undefined role.")
        else:
            messagebox.showerror("Error", "Invalid email or password.")

    # Sign In Button
    tk.Button(
        card,
        text="Login",
        font=("Segoe UI", 12, "bold"),
        bg="#5d5fef",
        activebackground="#4a4cce",
        fg="white",
        bd=0,
        relief="flat",
        width=25,
        height=2,
        command=login_user
    ).pack(pady=(10, 25))

    # Create account link
    footer = tk.Frame(card, bg="white")
    footer.pack()

    tk.Label(
        footer,
        text="Don’t have an account?",
        font=("Segoe UI", 10),
        bg="white"
    ).pack(side="left")

    def open_register():
        login.destroy()
        try:
            register.open_register_window()
        except ImportError as e:
            messagebox.showerror("Module Error", f"Failed to open registration: {e}")

    register_btn = tk.Button(
        footer,
        text="Create one",
        font=("Segoe UI", 10),
        bg="white",
        fg="#5d5fef",
        bd=0,
        cursor="hand2",
        command=open_register
    )
    register_btn.bind("<Enter>", lambda e: register_btn.config(font=("Segoe UI", 10, "underline")))
    register_btn.bind("<Leave>", lambda e: register_btn.config(font=("Segoe UI", 10)))
    register_btn.pack(side="left", padx=3)

    login.mainloop()


if __name__ == "__main__":
    open_login_window()