# data.py

users = {
    "admin_user": {"password": "admin", "role": "admin"},
    "john.doe": {"password": "student", "role": "student"},
}

# --- FIX: Add the mock function that register.py is trying to import ---
def add_user(username, password, email):
    """Mocks adding a new user to the global dictionary for registration."""
    if username not in users:
        # In a real app, you would hash the password and validate the email
        users[username] = {"password": password, "role": "student", "email": email}
        return True
    return False

# Book data structure matching the columns in the image
books = [
    {"id": 101, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "isbn": "978-0-7432-7356-5", "category": "Fiction", "quantity": 5, "available": 3, "description": "A classic story.", "cover_url": "cover_tg.jpg"},
    {"id": 102, "title": "To Kill a Mockingbird", "author": "Harper Lee", "isbn": "978-0-06-112008-4", "category": "Fiction", "quantity": 4, "available": 2, "description": "A powerful novel.", "cover_url": "cover_tk.jpg"},
    {"id": 103, "title": "1984", "author": "George Orwell", "isbn": "978-0-452-28423-4", "category": "Science Fiction", "quantity": 6, "available": 3, "description": "Dystopian classic.", "cover_url": "cover_19.jpg"},
    {"id": 104, "title": "Pride and Prejudice", "author": "Jane Austen", "isbn": "978-0-14-143951-8", "category": "Romance", "quantity": 3, "available": 1, "description": "Classic romance.", "cover_url": "cover_pp.jpg"},
    {"id": 105, "title": "The Catcher in the Rye", "author": "J.D. Salinger", "isbn": "978-0-316-76948-0", "category": "Fiction", "quantity": 4, "available": 3, "description": "Adolescent angst.", "cover_url": "cover_cr.jpg"},
]

students = [
    {"id": 201, "name": "Alice Smith", "email": "alice@uni.edu"},
    {"id": 202, "name": "Bob Johnson", "email": "bob@uni.edu"},
]

borrow_records = [
    {"book_id": 101, "student_name": "Alice Smith", "borrow_date": "2025-11-20", "due_date": "2025-12-05"},
    {"book_id": 103, "student_name": "Bob Johnson", "borrow_date": "2025-11-25", "due_date": "2025-12-10"},
]