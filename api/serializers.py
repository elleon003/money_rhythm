from rest_framework import serializers
from budgets.models import Budget, Category, Transaction, RecurringExpense, BudgetCategory
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']

class CategorySerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'is_income', 'owner', 'created_at']
        read_only_fields = ['id', 'created_at']

class BudgetCategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    actual_amount = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    remaining_amount = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )

    class Meta:
        model = BudgetCategory
        fields = [
            'id', 
            'budget', 
            'category', 
            'category_name',
            'planned_amount', 
            'actual_amount',
            'remaining_amount'
        ]
        read_only_fields = ['id']

class BudgetSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    budget_categories = BudgetCategorySerializer(many=True, read_only=True)
    total_planned = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    total_actual = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    remaining_budget = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    is_balanced = serializers.BooleanField(read_only=True)

    class Meta:
        model = Budget
        fields = [
            'id', 
            'name', 
            'owner',
            'shared_with',
            'start_date', 
            'end_date', 
            'is_active',
            'budget_categories',
            'total_planned',
            'total_actual',
            'remaining_budget',
            'is_balanced',
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class RecurringExpenseSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = RecurringExpense
        fields = [
            'id',
            'owner',
            'category',
            'category_name',
            'name',
            'amount',
            'frequency',
            'start_date',
            'end_date',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class TransactionSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    budget_name = serializers.CharField(source='budget.name', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id',
            'plaid_transaction_id',
            'owner',
            'category',
            'category_name',
            'budget',
            'budget_name',
            'amount',
            'date',
            'description',
            'merchant_name',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']