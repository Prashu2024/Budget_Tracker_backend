"""
Script to seed the database with sample data for demo user
Run this after migrations: python manage.py shell < seed_data.py
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "budget_tracker.settings")
django.setup()

from django.contrib.auth.models import User
from budget.models import Category, Transaction, Budget
from decimal import Decimal
from datetime import datetime, timedelta
import random


# Create or get demo user
try:
    demo_user = User.objects.get(username='test')
    print("Test user already exists")
except User.DoesNotExist:
    demo_user = User.objects.create_user(
        username='test',
        password='test123',
        email='test@gmail.com',
        first_name='Test',
        last_name='User'
    )
    print("Test user created successfully")

# Clear existing data for demo user
Category.objects.filter(user=demo_user).delete()
Transaction.objects.filter(user=demo_user).delete()
Budget.objects.filter(user=demo_user).delete()

# Create Income Categories
income_categories = [
    Category.objects.create(user=demo_user, name='Salary', type='income'),
    Category.objects.create(user=demo_user, name='Freelance', type='income'),
    Category.objects.create(user=demo_user, name='Investment Returns', type='income'),
    Category.objects.create(user=demo_user, name='Bonus', type='income'),
]

# Create Expense Categories
expense_categories = [
    Category.objects.create(user=demo_user, name='Groceries', type='expense'),
    Category.objects.create(user=demo_user, name='Transportation', type='expense'),
    Category.objects.create(user=demo_user, name='Entertainment', type='expense'),
    Category.objects.create(user=demo_user, name='Utilities', type='expense'),
    Category.objects.create(user=demo_user, name='Healthcare', type='expense'),
    Category.objects.create(user=demo_user, name='Shopping', type='expense'),
    Category.objects.create(user=demo_user, name='Dining Out', type='expense'),
    Category.objects.create(user=demo_user, name='Education', type='expense'),
]

print(f"Created {len(income_categories)} income categories")
print(f"Created {len(expense_categories)} expense categories")

# Generate transactions for the last 6 months
today = datetime.now().date()
transactions_created = 0

# Monthly Income Transactions
for i in range(6):
    month_date = today - timedelta(days=30 * i)
    
    # Salary (monthly)
    Transaction.objects.create(
        user=demo_user,
        category=income_categories[0],
        type='income',
        amount=Decimal('50000.00'),
        date=month_date.replace(day=1),
        description='Monthly salary credit'
    )
    transactions_created += 1
    
    # Occasional freelance income
    if random.choice([True, False]):
        Transaction.objects.create(
            user=demo_user,
            category=income_categories[1],
            type='income',
            amount=Decimal(str(random.randint(5000, 20000))),
            date=month_date - timedelta(days=random.randint(1, 28)),
            description='Freelance project payment'
        )
        transactions_created += 1

# Weekly Expense Transactions for last 3 months
for i in range(12):  # 12 weeks
    week_date = today - timedelta(weeks=i)
    
    # Groceries (weekly)
    Transaction.objects.create(
        user=demo_user,
        category=expense_categories[0],
        type='expense',
        amount=Decimal(str(random.randint(2000, 6000))),
        date=week_date,
        description='Weekly grocery shopping'
    )
    transactions_created += 1
    
    # Transportation
    if random.choice([True, True, False]):  # 66% chance
        Transaction.objects.create(
            user=demo_user,
            category=expense_categories[1],
            type='expense',
            amount=Decimal(str(random.randint(500, 2000))),
            date=week_date - timedelta(days=random.randint(0, 6)),
            description='Fuel and transportation'
        )
        transactions_created += 1

# Random expense transactions
expense_descriptions = {
    'Entertainment': ['Movie tickets', 'Concert', 'Streaming subscription', 'Gaming'],
    'Utilities': ['Electricity bill', 'Water bill', 'Internet bill', 'Phone bill'],
    'Healthcare': ['Medical checkup', 'Medicines', 'Health insurance', 'Gym membership'],
    'Shopping': ['Clothing', 'Electronics', 'Home items', 'Accessories'],
    'Dining Out': ['Restaurant', 'Cafe', 'Fast food', 'Food delivery'],
    'Education': ['Online course', 'Books', 'Training', 'Certification'],
}

for i in range(30):  # 30 random transactions
    random_date = today - timedelta(days=random.randint(0, 180))
    category = random.choice(expense_categories[2:])  # Skip groceries and transport
    
    descriptions = expense_descriptions.get(category.name, ['Miscellaneous expense'])
    
    Transaction.objects.create(
        user=demo_user,
        category=category,
        type='expense',
        amount=Decimal(str(random.randint(500, 5000))),
        date=random_date,
        description=random.choice(descriptions)
    )
    transactions_created += 1

print(f"Created {transactions_created} transactions")

# Create budgets for last 3 months and next 2 months
budgets_created = 0
for i in range(-2, 3):  # -2 to +2 months
    target_date = today + timedelta(days=30 * i)
    month = target_date.month
    year = target_date.year
    
    try:
        Budget.objects.create(
            user=demo_user,
            month=month,
            year=year,
            amount=Decimal('30000.00')
        )
        budgets_created += 1
    except:
        pass  # Budget might already exist

print(f"Created {budgets_created} budgets")

print("\n" + "="*50)
print("Sample data seeded successfully!")
print("="*50)
print("\nDemo Account Credentials:")
print("Username: test")
print("Password: test123")
print("\nData Summary:")
print(f"- Income Categories: {len(income_categories)}")
print(f"- Expense Categories: {len(expense_categories)}")
print(f"- Transactions: {transactions_created}")
print(f"- Budgets: {budgets_created}")
print("="*50)