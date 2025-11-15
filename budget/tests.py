from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from datetime import date
from .models import Category, Transaction, Budget


class CategoryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_create_category(self):
        category = Category.objects.create(
            user=self.user,
            name='Salary',
            type='income'
        )
        self.assertEqual(category.name, 'Salary')
        self.assertEqual(category.type, 'income')
        self.assertEqual(category.user, self.user)


class TransactionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = Category.objects.create(
            user=self.user,
            name='Groceries',
            type='expense'
        )
    
    def test_create_transaction(self):
        transaction = Transaction.objects.create(
            user=self.user,
            category=self.category,
            type='expense',
            amount=Decimal('500.00'),
            date=date.today(),
            description='Weekly shopping'
        )
        self.assertEqual(transaction.amount, Decimal('500.00'))
        self.assertEqual(transaction.type, 'expense')


class BudgetModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_create_budget(self):
        budget = Budget.objects.create(
            user=self.user,
            month=1,
            year=2024,
            amount=Decimal('30000.00')
        )
        self.assertEqual(budget.amount, Decimal('30000.00'))
        self.assertEqual(budget.month, 1)


class AuthenticationAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_login_success(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
    
    def test_login_failure(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TransactionAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.category = Category.objects.create(
            user=self.user,
            name='Groceries',
            type='expense'
        )
    
    def test_create_transaction(self):
        data = {
            'type': 'expense',
            'category': self.category.id,
            'amount': '500.00',
            'date': date.today().isoformat(),
            'description': 'Test transaction'
        }
        response = self.client.post('/api/transactions/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_list_transactions(self):
        Transaction.objects.create(
            user=self.user,
            category=self.category,
            type='expense',
            amount=Decimal('500.00'),
            date=date.today()
        )
        response = self.client.get('/api/transactions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class BudgetAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_create_budget(self):
        data = {
            'month': 1,
            'year': 2024,
            'amount': '30000.00'
        }
        response = self.client.post('/api/budgets/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_get_current_month_budget(self):
        today = date.today()
        Budget.objects.create(
            user=self.user,
            month=today.month,
            year=today.year,
            amount=Decimal('30000.00')
        )
        response = self.client.get('/api/budgets/current_month/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DashboardAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create test data
        income_cat = Category.objects.create(
            user=self.user,
            name='Salary',
            type='income'
        )
        expense_cat = Category.objects.create(
            user=self.user,
            name='Groceries',
            type='expense'
        )
        
        Transaction.objects.create(
            user=self.user,
            category=income_cat,
            type='income',
            amount=Decimal('50000.00'),
            date=date.today()
        )
        Transaction.objects.create(
            user=self.user,
            category=expense_cat,
            type='expense',
            amount=Decimal('5000.00'),
            date=date.today()
        )
    
    def test_get_dashboard(self):
        response = self.client.get('/api/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_income', response.data)
        self.assertIn('total_expenses', response.data)
        self.assertIn('balance', response.data)