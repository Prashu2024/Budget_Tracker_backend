
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from budget import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
router.register(r'budgets', views.BudgetViewSet, basename='budget')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/login/', views.login_view, name='login'),
    path('api/auth/logout/', views.logout_view, name='logout'),
    path('api/auth/user/', views.current_user, name='current-user'),
    path('api/dashboard/', views.dashboard_view, name='dashboard'),
    # path('api/budgets/current-month/', views.current_month_budget, name='budget-current-month'),
]