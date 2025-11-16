# Budget Tracker - Backend

Django REST Framework API for personal budget tracking application with user authentication and financial data management.

##  Live Demo

**Backend API Deplyment Link:** https://budgettrackerbackend-production-53a7.up.railway.app/api  
**DRF Browsable API:** https://budgettrackerbackend-production-53a7.up.railway.app/api/  
**Admin Panel:** https://budgettrackerbackend-production-53a7.up.railway.app/admin/
 
**Backend Repository:** https://github.com/Prashu2024/Budget_Tracker_backend

##  Test Credentials

### Regular User (API Access)
```
Username: test
Password: test123
```

### Admin User (Admin Panel)
```
Username: postgres
Password: [Contact developer]
```

##  Features

### Core Functionality
- **User Authentication:** Token-based authentication using DRF
- **Category Management:** CRUD operations for income/expense categories
- **Transaction Management:** 
  - Add, edit, delete income/expense transactions
  - Advanced filtering (type, category, date range, amount range)
  - Pagination support
  - Search in descriptions
- **Budget Management:** 
  - Set monthly budgets
  - Get current month budget
  - Budget vs expense comparison
- **Dashboard API:** 
  - Aggregated financial summary
  - Income/expense by category
  - 6-month trend data

### Security
- Token-based authentication
- User-specific data isolation
- CORS configuration for frontend
- Input validation and sanitization

##  Tech Stack

- **Django 4.2.7** - Web framework
- **Django REST Framework 3.14.0** - API development
- **SQLite** - Database (development)
- **PostgreSQL** - Database (production via Railway)
- **Token Authentication** - Security
- **Django CORS Headers** - Cross-origin requests
- **Gunicorn** - WSGI server
- **WhiteNoise** - Static file serving

##  Installation

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

### Setup

```bash
# Clone repository
git clone https://github.com/Prashu2024/Budget_Tracker_backend.git
cd Budget_Tracker_backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (for admin access)
python manage.py createsuperuser

# Create demo user (optional)
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.create_user('demo', 'demo@example.com', 'demo123')
>>> exit()

# Run development server
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

##  Project Structure

```
budget_tracker/
├── budget_tracker/
│   ├── settings.py       # Django settings
│   ├── urls.py          # Main URL routing
│   └── wsgi.py          # WSGI configuration
├── budget/
│   ├── models.py        # Database models
│   ├── serializers.py   # DRF serializers
│   ├── views.py         # API views
│   ├── admin.py         # Admin configuration
│   └── tests.py         # Unit tests
├── manage.py
├── requirements.txt
└── Procfile            # Deployment configuration
```

##  Database Models

### User
Django's built-in User model for authentication.

### Category
```python
- user (ForeignKey)
- name (CharField)
- type (CharField: 'income' or 'expense')
- created_at, updated_at
```

### Transaction
```python
- user (ForeignKey)
- category (ForeignKey)
- type (CharField: 'income' or 'expense')
- amount (DecimalField)
- description (TextField)
- date (DateField)
- created_at, updated_at
```

### Budget
```python
- user (ForeignKey)
- month (IntegerField: 1-12)
- year (IntegerField)
- amount (DecimalField)
- created_at, updated_at
```

##  API Endpoints

### Authentication
```
POST   /api/auth/login/          # User login
POST   /api/auth/logout/         # User logout
GET    /api/auth/user/           # Current user info
```

### Dashboard
```
GET    /api/dashboard/           # Financial summary
```

### Categories
```
GET    /api/categories/          # List categories
POST   /api/categories/          # Create category
GET    /api/categories/{id}/     # Get category
PUT    /api/categories/{id}/     # Update category
DELETE /api/categories/{id}/     # Delete category
```

### Transactions
```
GET    /api/transactions/        # List transactions (with filters)
POST   /api/transactions/        # Create transaction
GET    /api/transactions/{id}/   # Get transaction
PUT    /api/transactions/{id}/   # Update transaction
DELETE /api/transactions/{id}/   # Delete transaction
```

**Query Parameters for Filtering:**
- `type` - Filter by 'income' or 'expense'
- `category` - Filter by category ID
- `start_date` - Filter from date (YYYY-MM-DD)
- `end_date` - Filter to date (YYYY-MM-DD)
- `min_amount` - Minimum amount
- `max_amount` - Maximum amount
- `search` - Search in description
- `page` - Page number for pagination

### Budgets
```
GET    /api/budgets/             # List budgets
POST   /api/budgets/             # Create budget
GET    /api/budgets/current-month/  # Current month budget
GET    /api/budgets/{id}/        # Get budget
PUT    /api/budgets/{id}/        # Update budget
DELETE /api/budgets/{id}/        # Delete budget
```

##  Environment Variables

```env
DEBUG=False
SECRET_KEY=<your-secret-key>
ALLOWED_HOSTS=<your-domain>
DATABASE_URL=<postgresql-url>  # For production
CORS_ORIGINS=<frontend-url>
```

##  API Response Examples

### Dashboard Response
```json
{
  "total_income": "65000.00",
  "total_expenses": "35000.00",
  "balance": "30000.00",
  "monthly_budget": "40000.00",
  "budget_remaining": "5000.00",
  "budget_percentage": 87.5,
  "income_by_category": [
    {"category__name": "Salary", "total": "50000.00"}
  ],
  "expenses_by_category": [
    {"category__name": "Groceries", "total": "5000.00"}
  ],
  "monthly_trend": [
    {"month": "Jun 2024", "income": 50000, "expenses": 30000}
  ]
}
```

### Transaction List Response
```json
{
  "count": 45,
  "next": "http://api/transactions/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "type": "expense",
      "category": 3,
      "category_name": "Groceries",
      "amount": "5000.00",
      "description": "Weekly shopping",
      "date": "2024-11-15",
      "created_at": "2024-11-15T10:30:00Z"
    }
  ]
}
```

##  Running Tests

```bash
python manage.py test
```

##  Deployment

### Railway (Current Setup)

1. Connect GitHub repository to Railway
2. Set environment variables
3. Railway auto-deploys on push to main branch

### Alternative Platforms
- Heroku
- Render
- PythonAnywhere
- DigitalOcean

##  Acknowledgments

This project was developed with assistance from:
- **Claude (Anthropic)** - AI assistant for Django architecture, DRF implementation, API design, database modeling, and optimization
- **ChatGPT (OpenAI)** - AI assistant for debugging, query optimization, and best practices

All code has been reviewed, tested, and fully understood by the developer.

### External Libraries
- Django, Django REST Framework, django-cors-headers, gunicorn, whitenoise (all BSD/MIT licensed)

##  Developer

**Prashu2024**  
GitHub: [@Prashu2024](https://github.com/Prashu2024)

---
