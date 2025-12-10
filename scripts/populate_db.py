"""
Script to populate the database with sample data for testing
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lms_backend'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_backend.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from core.models import Book, Loan
from datetime import datetime, timedelta

User = get_user_model()

def populate_books():
    """Add sample books to the database"""
    books_data = [
        {
            'title': 'To Kill a Mockingbird',
            'author': 'Harper Lee',
            'isbn': '978-0-06-112008-4',
            'category': 'Fiction',
            'quantity': 5,
            'available': 5,
            'description': 'A classic novel about racial injustice in the American South'
        },
        {
            'title': '1984',
            'author': 'George Orwell',
            'isbn': '978-0-452-28423-4',
            'category': 'Dystopian',
            'quantity': 3,
            'available': 3,
            'description': 'A dystopian social science fiction novel'
        },
        {
            'title': 'The Great Gatsby',
            'author': 'F. Scott Fitzgerald',
            'isbn': '978-0-7432-7356-5',
            'category': 'Fiction',
            'quantity': 4,
            'available': 4,
            'description': 'A 1925 novel written by American author F. Scott Fitzgerald'
        },
        {
            'title': 'Pride and Prejudice',
            'author': 'Jane Austen',
            'isbn': '978-0-14-143951-8',
            'category': 'Romance',
            'quantity': 6,
            'available': 6,
            'description': 'A romantic novel of manners'
        },
        {
            'title': 'The Catcher in the Rye',
            'author': 'J.D. Salinger',
            'isbn': '978-0-316-76948-0',
            'category': 'Fiction',
            'quantity': 3,
            'available': 3,
            'description': 'A story about teenage rebellion and angst'
        },
        {
            'title': 'Harry Potter and the Sorcerer\'s Stone',
            'author': 'J.K. Rowling',
            'isbn': '978-0-439-70818-8',
            'category': 'Fantasy',
            'quantity': 7,
            'available': 7,
            'description': 'The first novel in the Harry Potter series'
        },
        {
            'title': 'The Hobbit',
            'author': 'J.R.R. Tolkien',
            'isbn': '978-0-547-92822-7',
            'category': 'Fantasy',
            'quantity': 4,
            'available': 4,
            'description': 'A fantasy novel and children\'s book'
        },
        {
            'title': 'Fahrenheit 451',
            'author': 'Ray Bradbury',
            'isbn': '978-1-451-67331-9',
            'category': 'Science Fiction',
            'quantity': 3,
            'available': 3,
            'description': 'A dystopian novel about a future society'
        },
        {
            'title': 'The Lord of the Rings',
            'author': 'J.R.R. Tolkien',
            'isbn': '978-0-544-00341-5',
            'category': 'Fantasy',
            'quantity': 5,
            'available': 5,
            'description': 'An epic high-fantasy novel'
        },
        {
            'title': 'Animal Farm',
            'author': 'George Orwell',
            'isbn': '978-0-452-28424-1',
            'category': 'Political Fiction',
            'quantity': 4,
            'available': 4,
            'description': 'An allegorical novella'
        }
    ]
    
    for book_data in books_data:
        book, created = Book.objects.get_or_create(
            isbn=book_data['isbn'],
            defaults=book_data
        )
        if created:
            print(f"Created book: {book.title}")
        else:
            print(f"Book already exists: {book.title}")

def populate_users():
    """Add sample users to the database"""
    users_data = [
        {'username': 'john_doe', 'email': 'john.doe@university.edu', 'password': 'password123'},
        {'username': 'jane_smith', 'email': 'jane.smith@university.edu', 'password': 'password123'},
        {'username': 'bob_wilson', 'email': 'bob.wilson@university.edu', 'password': 'password123'},
        {'username': 'alice_johnson', 'email': 'alice.johnson@university.edu', 'password': 'password123'},
        {'username': 'charlie_brown', 'email': 'charlie.brown@university.edu', 'password': 'password123'},
    ]
    
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={'email': user_data['email']}
        )
        if created:
            user.set_password(user_data['password'])
            user.save()
            print(f"Created user: {user.username}")
        else:
            print(f"User already exists: {user.username}")

def main():
    print("Populating database with sample data...")
    print("\n--- Adding Books ---")
    populate_books()
    print("\n--- Adding Users ---")
    populate_users()
    print("\n✅ Database population complete!")

if __name__ == '__main__':
    main()
