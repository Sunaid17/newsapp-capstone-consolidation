# NewsHub - News Application

A Django-based news application that allows publishers to create and manage news articles while readers can browse, search, and bookmark articles.

## Table of Contents
- [Project Overview](#project-overview)
- [Project Structure](#project-structure)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation Guide](#installation-guide)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [User Roles](#user-roles)
- [Technologies Used](#technologies-used)
- [Troubleshooting](#troubleshooting)

## Project Overview

**NewsHub** is a full-featured news platform built with Django framework. It supports:
- User authentication with role-based access control
- Article creation and management for publishers
- Article browsing, searching, and filtering for all users
- Bookmark functionality for authenticated users
- RESTful API for third-party integration

## Project Structure

```
NewsApp/
├── NewsApp/                    # Main Django project settings
│   ├── __init__.py
│   ├── settings.py             # Django settings
│   ├── urls.py                 # Main URL configuration
│   ├── wsgi.py
│   └── asgi.py
├── articles/                   # Articles app (models, views, admin)
│   ├── models.py               # CustomUser, Publisher, Category, Article models
│   ├── views.py                # Views for articles CRUD and browsing
│   ├── urls.py                 # URL routing for articles
│   ├── admin.py                # Admin configuration
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py    # Database seeding command
│   └── migrations/
├── accounts/                   # Authentication app
│   ├── views.py                # Login, register, logout views
│   ├── urls.py                 # URL routing for authentication
│   └── apps.py
├── templates/                   # HTML templates
│   ├── base.html               # Base template with navigation
│   ├── home.html               # Home page with article grid
│   ├── login.html              # Login page
│   ├── register.html           # Registration page
│   ├── create_article.html     # Article creation form
│   ├── my_articles.html        # Publisher's articles list
│   └── article_detail.html    # Single article view
├── static/                     # Static files (CSS, JS)
│   ├── style.css               # Main stylesheet
│   └── app.js                  # JavaScript for interactivity
├── media/                      # User-uploaded files
├── db.sqlite3                  # SQLite database (created after migrations)
├── manage.py                   # Django management script
└── requirements.txt            # Python dependencies
```

## Features

### Authentication & Authorization
- User registration with role selection (Reader/Publisher)
- Login/Logout functionality
- Role-based access control (RBAC)
- Password hashing with PBKDF2

### Article Management (Publishers)
- Create new articles
- Edit existing articles
- Delete articles
- View personal articles dashboard

### Article Browsing (All Users)
- View all published articles
- Filter by category
- Search by title/content
- View article details in modal

### Bookmarks (Authenticated Users)
- Bookmark/unbookmark articles
- View bookmarked articles list

### RESTful API
- Public endpoints for article retrieval
- Filter by category and search
- Third-party client support

## Prerequisites

Before installing, ensure you have:
- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for cloning)

## Installation Guide

### Step 1: Clone or Extract the Project

If you have the project as a ZIP file:
```bash
cd /path/to/your/projects
unzip NewsApplication.zip
cd NewsApp
```

### Step 2: Create a Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate on Linux/Mac
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

If you don't have requirements.txt, install manually:
```bash
pip install Django==4.2.11
```

### Step 4: Configure Database

The project is pre-configured to use SQLite. The database will be created automatically when you run migrations.

**For MariaDB/MySQL (optional):**
1. Create a database in MariaDB:
   ```sql
   CREATE DATABASE newsapp_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. Update `NewsApp/settings.py` with your database credentials:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'newsapp_db',
           'USER': 'your_username',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '3306',
       }
   }
   ```

### Step 5: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### Step 7: Seed Sample Data

```bash
python manage.py seed_data
```

This creates:
- 7 categories (Politics, Technology, Sports, Entertainment, Business, Health, Science)
- 1 publisher user: `publisher1` / `password123`
- 8 sample articles

## Running the Application

### Step 1: Start the Development Server

```bash
python manage.py runserver
```

### Step 2: Access the Application

Open your browser and navigate to:
```
http://127.0.0.1:8000/
```

### Step 3: Access Admin Panel (Optional)

Navigate to:
```
http://127.0.0.1:8000/admin/
```

Login with your superuser credentials.

## Configuration

### Email Settings

The application includes email configuration for password reset functionality. Update `NewsApp/settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # For development
# Or use SMTP for production:
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

### Allowed Hosts

For production, update `ALLOWED_HOSTS` in settings.py:
```python
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']
```

## API Documentation

### Base URL
```
http://127.0.0.1:8000/api/
```

### Authentication
Use JWT tokens. Obtain a token by posting to `/token/` with username and password:
```python
import requests

BASE_URL = "http://127.0.0.1:8000/api"

# Get token
response = requests.post(f"{BASE_URL}/token/", {
    "username": "journalist1",
    "password": "password123"
})
token = response.json()["access"]

# Use token
headers = {"Authorization": f"Bearer {token}"}
```

### Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | /token/ | Obtain JWT token | Public |
| POST | /token/refresh/ | Refresh JWT token | Public |
| GET | /user/ | Get current user | Authenticated |
| GET | /articles/ | List articles | Authenticated |
| POST | /articles/ | Create article | Journalist |
| GET | /articles/subscribed/ | Get subscribed content | Reader |
| GET | /articles/{id}/ | Get single article | Authenticated |
| POST | /articles/{id}/approve/ | Approve/reject article | Editor |
| GET | /newsletters/ | List newsletters | Authenticated |
| POST | /newsletters/ | Create newsletter | Journalist |
| POST | /subscribe/ | Subscribe to publisher/journalist | Reader |
| GET | /publishers/ | List all publishers | Authenticated |
| GET | /journalists/ | List verified journalists | Authenticated |

### Example API Calls
```python
import requests

BASE_URL = "http://127.0.0.1:8000/api"

# Get token and use it
response = requests.post(f"{BASE_URL}/token/", {
    "username": "journalist1",
    "password": "password123"
})
token = response.json()["access"]
headers = {"Authorization": f"Bearer {token}"}

# Get all articles
response = requests.get(f"{BASE_URL}/articles/", headers=headers)
print(response.json())

# Subscribe to publisher
response = requests.post(f"{BASE_URL}/subscribe/", 
    {"type": "publisher", "publisher_id": 1},
    headers=headers
)
```

## User Roles

### Reader
- Browse all published articles
- Search and filter articles
- Bookmark articles
- View bookmarks

### Publisher
- All reader capabilities
- Create new articles
- Edit own articles
- Delete own articles
- View own articles dashboard

### Admin
- All publisher capabilities
- Manage all articles
- Manage users
- Access Django admin panel

## Test Accounts

After running `python manage.py seed_data`:

| Role | Username | Password |
|------|----------|----------|
| Publisher | publisher1 | password123 |

You can also register new users through the registration page.

## Technologies Used

- **Backend:** Django 4.2.11
- **Database:** SQLite (default), MariaDB/MySQL (optional)
- **Frontend:** HTML5, CSS3, JavaScript
- **Fonts:** Inter (Google Fonts)
- **Python:** 3.8+

## Troubleshooting

### "ModuleNotFoundError: No module named 'django'"

Solution: Activate your virtual environment and install Django:
```bash
source venv/bin/activate
pip install Django==4.2.11
```

### "Database already exists" error during migration

Solution: Delete the existing database and recreate:
```bash
rm db.sqlite3
python manage.py migrate
```

### "Port already in use" error

Solution: Use a different port:
```bash
python manage.py runserver 8001
```

### Login/Register not working

Solution: Check that:
1. `{% load static %}` is at the top of base.html
2. STATIC_URL is correctly configured in settings.py
3. Run `python manage.py collectstatic` if needed

### CSRF token errors

Solution: Ensure your templates include `{% csrf_token %}` in forms and JavaScript sends the CSRF token in headers.

## License

This project is for educational purposes.