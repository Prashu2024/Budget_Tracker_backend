from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Transaction, Budget
from datetime import datetime

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'type', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'category', 'category_name', 'type', 'amount', 'description', 'date', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_category(self, value):
        if value and value.user != self.context['request'].user:
            raise serializers.ValidationError("Invalid category.")
        return value
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ['id', 'month', 'year', 'amount', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, data):
        month = data.get('month')
        year = data.get('year')
        
        if month < 1 or month > 12:
            raise serializers.ValidationError("Month must be between 1 and 12")
        
        current_year = datetime.now().year
        if year < 2000 or year > current_year + 10:
            raise serializers.ValidationError(f"Year must be between 2000 and {current_year + 10}")
        
        return data
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class DashboardSerializer(serializers.Serializer):
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    monthly_budget = serializers.DecimalField(max_digits=12, decimal_places=2, allow_null=True)
    budget_remaining = serializers.DecimalField(max_digits=12, decimal_places=2, allow_null=True)
    budget_percentage = serializers.FloatField(allow_null=True)
    income_by_category = serializers.ListField()
    expenses_by_category = serializers.ListField()
    monthly_trend = serializers.ListField()