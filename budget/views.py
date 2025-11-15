from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q, Sum
from datetime import datetime, timedelta
from decimal import Decimal
from .models import Category, Transaction, Budget
from .serializers import (
    CategorySerializer, TransactionSerializer, 
    BudgetSerializer, DashboardSerializer, UserSerializer
)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Please provide both username and password'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })
    
    return Response(
        {'error': 'Invalid credentials'}, 
        status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    request.user.auth_token.delete()
    return Response({'message': 'Successfully logged out'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    
    def get_queryset(self):
        queryset = Category.objects.filter(user=self.request.user)
        category_type = self.request.query_params.get('type', None)
        if category_type:
            queryset = queryset.filter(type=category_type)
        return queryset


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['description', 'category__name']
    ordering_fields = ['date', 'amount', 'created_at']
    
    def get_queryset(self):
        queryset = Transaction.objects.filter(user=self.request.user)
        
        # Filter by type
        transaction_type = self.request.query_params.get('type', None)
        if transaction_type:
            queryset = queryset.filter(type=transaction_type)
        
        # Filter by category
        category_id = self.request.query_params.get('category', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # Filter by amount range
        min_amount = self.request.query_params.get('min_amount', None)
        max_amount = self.request.query_params.get('max_amount', None)
        
        if min_amount:
            queryset = queryset.filter(amount__gte=min_amount)
        if max_amount:
            queryset = queryset.filter(amount__lte=max_amount)
        
        return queryset


class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'], url_path='current-month')
    def current_month(self, request):
        now = datetime.now()
        try:
            budget = Budget.objects.get(
                user=request.user,
                month=now.month,
                year=now.year
            )
            serializer = self.get_serializer(budget)
            return Response(serializer.data)
        except Budget.DoesNotExist:
            return Response(
                {'detail': 'No budget set for current month'}, 
                status=status.HTTP_404_NOT_FOUND
            )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_view(request):
    user = request.user
    now = datetime.now()
    
    # Get month and year from query params or use current
    month = int(request.query_params.get('month', now.month))
    year = int(request.query_params.get('year', now.year))
    
    # Calculate total income and expenses
    transactions = Transaction.objects.filter(user=user)
    total_income = transactions.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_expenses = transactions.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    balance = total_income - total_expenses
    
    # Get current month budget
    try:
        budget = Budget.objects.get(user=user, month=month, year=year)
        monthly_budget = budget.amount
        month_expenses = transactions.filter(
            type='expense',
            date__month=month,
            date__year=year
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        budget_remaining = monthly_budget - month_expenses
        budget_percentage = float((month_expenses / monthly_budget * 100)) if monthly_budget > 0 else 0
    except Budget.DoesNotExist:
        monthly_budget = None
        budget_remaining = None
        budget_percentage = None
    
    # Income by category
    income_by_category = list(
        transactions.filter(type='income', category__isnull=False)
        .values('category__name')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )
    
    # Expenses by category
    expenses_by_category = list(
        transactions.filter(type='expense', category__isnull=False)
        .values('category__name')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )
    
    # Monthly trend for last 6 months
    monthly_trend = []
    for i in range(5, -1, -1):
        target_date = now - timedelta(days=30 * i)
        month_income = transactions.filter(
            type='income',
            date__month=target_date.month,
            date__year=target_date.year
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        month_expense = transactions.filter(
            type='expense',
            date__month=target_date.month,
            date__year=target_date.year
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        monthly_trend.append({
            'month': target_date.strftime('%b %Y'),
            'income': float(month_income),
            'expenses': float(month_expense)
        })
    
    data = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance,
        'monthly_budget': monthly_budget,
        'budget_remaining': budget_remaining,
        'budget_percentage': budget_percentage,
        'income_by_category': income_by_category,
        'expenses_by_category': expenses_by_category,
        'monthly_trend': monthly_trend
    }
    
    serializer = DashboardSerializer(data)
    return Response(serializer.data)


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def current_month_budget(request):
#     """Get budget for current month"""
#     now = datetime.now()
#     try:
#         budget = Budget.objects.get(
#             user=request.user,
#             month=now.month,
#             year=now.year
#         )
#         serializer = BudgetSerializer(budget)
#         return Response(serializer.data)
#     except Budget.DoesNotExist:
#         return Response(
#             {'detail': 'No budget set for current month'}, 
#             status=status.HTTP_404_NOT_FOUND
#         )