# Library Management System

A comprehensive library management system with Django REST Framework backend and Tkinter GUI frontend.

## Features

### Admin Portal
- Dashboard with statistics and recent activity
- Book Management (Add, Edit, Delete, Search, Sort, Filter)
- User Management (Add, Delete, Search)
- Lending & Returns (Borrow/Return books)
- Real-time availability tracking

### Student Portal
- Personal dashboard with borrowing statistics
- Book catalog with search and borrow functionality
- My Loans (view active loans, return books, track overdue items)
- Borrowing history with detailed records

### Backend API
- JWT token-based authentication
- RESTful API endpoints for books, users, and loans
- Atomic transactions for data consistency
- Query parameter filtering support
- Automatic fine tracking and overdue calculations

## Installation

### Windows PowerShell

1. **Clone the repository**
```powershell
git clone <repository-url>
cd Library-Management-Book-Recommendation-System
```

2. **Create and activate virtual environment**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. **Install dependencies**
```powershell
pip install -r requirements.txt
```

4. **Setup database**
```powershell
cd lms_backend
python manage.py migrate
python manage.py createsuperuser
```

5. **Populate sample data (optional)**
```powershell
python ..\scripts\populate_db.py
```

6. **Start the backend server**
```powershell
python manage.py runserver
```

7. **Start the frontend (in a new terminal)**
```powershell
cd ..
python LMSFINAL\login.py
```

## API Endpoints

### Authentication
- `POST /api/auth/login/` — Obtain JWT token
- `POST /api/auth/refresh/` — Refresh JWT token

### Books
- `GET /api/books/` — List all books
- `POST /api/books/` — Create new book
- `GET /api/books/{id}/` — Get book details
- `PUT /api/books/{id}/` — Update book
- `DELETE /api/books/{id}/` — Delete book

### Users
- `GET /api/users/` — List all users
- `POST /api/users/` — Create new user (registration)
- `GET /api/users/me/` — Get current user info
- `GET /api/users/{id}/` — Get user details
- `PUT /api/users/{id}/` — Update user
- `DELETE /api/users/{id}/` — Delete user

### Loans
- `GET /api/loans/` — List all loans (supports ?user=<id>&status=<borrowed|returned>)
- `POST /api/loans/` — Create new loan (borrow book)
- `POST /api/loans/{id}/return/` — Return a book

## Default Credentials

After running `createsuperuser`, you can create admin and student accounts through the registration interface or Django admin panel.

## Project Structure

```
Library-Management-Book-Recommendation-System/
├── lms_backend/           # Django backend
│   ├── core/              # Main app with models, views, serializers
│   └── lms_backend/       # Django project settings
├── LMSFINAL/              # Tkinter frontend
│   ├── login.py           # Login interface
│   ├── register.py        # Registration interface
│   ├── adminDashboardUI.py      # Admin portal
│   ├── student_portal_app.py    # Student portal
│   ├── book_management_ui.py    # Book management
│   ├── user_management_ui.py    # User management
│   ├── transactions_ui.py       # Lending/Returns
│   ├── my_loans_ui.py          # Student loans view
│   ├── borrowing_history_ui.py # Borrowing history
│   ├── student_book_catalog_ui.py # Book catalog
│   └── api_client.py      # API communication layer
└── scripts/               # Utility scripts
    └── populate_db.py     # Sample data population
```

## Technologies Used

- **Backend**: Django 4.x, Django REST Framework, SQLite
- **Frontend**: Python Tkinter
- **Authentication**: JWT (djangorestframework-simplejwt)
- **API Communication**: requests library

## License

MIT License
