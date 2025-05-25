# Library Management System API

A Django REST API for a Library Management System that supports user registration, book browsing, borrowing, and returning functionality.

## Features

- User registration and JWT authentication
- Book browsing with filtering options
- Book borrowing with inventory management
- Book returning with penalty calculation
- Admin-only book, author, and category management
- API rate limiting

## Database Schema (ER Diagram)

```
+---------------+       +---------------+       +---------------+
| User          |       | Author        |       | Category      |
+---------------+       +---------------+       +---------------+
| user          | 1   1 | id            |       | id            |
| penalty_points|<----->| name          |       | name          |
+---------------+       | bio           |       | created_at    |
                        | created_at    |       | updated_at    |
                        | updated_at    |       +------^--------+
                        +-------^-------+              |
                                |                      |
                                |                      |
                        +-------+------+---------------+------+
                        | Book          |                     |
                        +---------------+                     |
                        | id            |                     |
                        | title         |                     |
                        | description   |                     |
                        | author        |----+                |
                        | category      |----+                |
                        | total_copies  |                     |
                        | available_copies                    |
                        | created_at    |                     |
                        | updated_at    |                     |
                        +-------^-------+                     |
                                |                             |
                                |                             |
                        +-------+-------------+               |
                        | Borrow             |               |
                        +-------------------+               |
                        | id                |               |
                        | user              |               |
                        | book              |---------------+
                        | borrow_date       |
                        | due_date          |
                        | return_date       |
                        | returned          |
                        | created_at        |
                        | updated_at        |
                        +-------------------+
```

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/al-jaber-nishad/library-api
   cd library-api
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Load sample data (optional):
   ```bash
   python manage.py initialize_library
   ```

6. Create a superuser (if not using sample data):
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

8. Access the API at http://127.0.0.1:8000/api/ and get the Postman API collection at https://www.postman.com/bold-eclipse-977420/workspace/sparktech-agency/collection/29026314-06325977-6641-43c4-adcb-7d6ca772d040?action=share&creator=29026314

## API Endpoints

### Authentication
- `POST /api/register/` - Register a new user
- `POST /api/login/` - Login and get JWT tokens

### Books & Metadata
- `GET /api/books/` - List books with filters (author, category)
- `GET /api/books/{id}/` - Get a specific book
- `POST /api/books/` - Add a new book (admin only)
- `PUT /api/books/{id}/` - Update a book (admin only)
