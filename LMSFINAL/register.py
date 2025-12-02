# register.py

import tkinter as tk
from tkinter import messagebox
# Import the actual login module to use its function
import login

# The 'from data import add_user' line should remain if your 'data.py' exists.
from data import add_user


# NOTE: We REMOVE the dummy def open_login_window() here.
# We REMOVE the dummy def add_user() here.

def open_register_window():
    reg = tk.Tk()
    reg.title("Library System | Register")
    # Increased sizes for visibility
    reg.geometry("480x580")
    reg.configure(bg="#eef1f6")
    reg.resizable(False, False)

    # Center window
    reg.update_idletasks()
    width, height = 480, 580
    x = (reg.winfo_screenwidth() // 2) - (width // 2)
    y = (reg.winfo_screenheight() // 2) - (height // 2)
    reg.geometry(f"{width}x{height}+{x}+{y}")

    # --- Card Frame ---
    card = tk.Frame(reg, bg="white", bd=0, highlightthickness=0)
    card.place(relx=0.5, rely=0.5, anchor="center", width=380, height=530)

    # Title and Description... (unchanged)
    tk.Label(
        card,
        text="Create Account",
        font=("Segoe UI", 20, "bold"),
        bg="white"
    ).pack(pady=(20, 3))

    tk.Label(
        card,
        text="Fill in your details to register a new account",
        font=("Segoe UI", 10),
        fg="#7f8c8d",
        bg="white"
    ).pack(pady=(0, 10))

    # Input Fields Helper (unchanged)
    def create_input(label, show=None):
        tk.Label(card, text=label, font=("Segoe UI", 10), bg="white").pack(anchor="w", padx=30)
        entry = tk.Entry(
            card, font=("Segoe UI", 11),
            width=32, bd=1, relief="solid", show=show
        )
        entry.pack(pady=(3, 8))
        return entry

    # New Required Fields (unchanged)
    first_name_entry = create_input("First Name")
    middle_name_entry = create_input("Middle Name")
    last_name_entry = create_input("Last Name")
    email_entry = create_input("Email Address")
    username_entry = create_input("Username")
    password_entry = create_input("Password", show="*")

    # Register Logic
    def register_user():
        first = first_name_entry.get().strip()
        middle = middle_name_entry.get().strip()
        last = last_name_entry.get().strip()
        email = email_entry.get().strip()
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        if not all([first, last, email, username, password]):
            messagebox.showerror("Error", "All required fields must be filled!")
            return

        fullname = f"{first} {middle} {last}".strip()

        # Call the actual add_user from data.py
        success = add_user(username, password, fullname)

        if success:
            messagebox.showinfo("Success", "Account created successfully!")
            reg.destroy()
            # *** CRITICAL: Call the actual function from the imported module ***
            login.open_login_window()
        else:
            messagebox.showerror("Error", "Username already exists!")

    # Submit Button (unchanged)
    register_btn = tk.Button(
        card,
        text="Register",
        font=("Segoe UI", 11, "bold"),
        bg="#5d5fef",
        fg="white",
        bd=0,
        relief="flat",
        width=28,
        height=1,
        command=register_user,
    )
    register_btn.pack(pady=(15, 15))

    # Back / Already have an account? (unchanged)
    footer = tk.Frame(card, bg="white")
    footer.pack()

    tk.Label(
        footer,
        text="Already have an account?",
        font=("Segoe UI", 10),
        bg="white"
    ).pack(side="left")

    back_btn = tk.Button(
        footer,
        text="Sign In",
        font=("Segoe UI", 10, "underline"),
        bg="white",
        fg="#5d5fef",
        bd=0,
        cursor="hand2",
        # *** CRITICAL: Call the actual function from the imported module ***
        command=lambda: [reg.destroy(), login.open_login_window()],
    )
    back_btn.pack(side="left", padx=3)

    reg.mainloop()


if __name__ == "__main__":
    open_register_window()