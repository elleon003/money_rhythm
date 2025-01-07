from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from decimal import Decimal
import uuid
from django.db.models import Sum
from datetime import datetime



class Budget(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shared_with = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='shared_budgets', blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError('Start date must be before end date')

    class Meta:
        ordering = ['-created_at']

    @property
    def total_planned(self):
        """Calculate total planned spending across all categories"""
        return self.budget_categories.aggregate(total=Sum('planned_amount'))['total'] or Decimal('0.00')

    @property
    def total_actual(self):
        """Calculate total actual spending across all categories"""
        return self.transactions.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    @property
    def total_actual(self):
        """Calculate total actual spending across all categories"""
        return self.transactions.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    @property
    def remaining_budget(self):
        """Calculate remaining budget"""
        return self.total_planned - self.total_actual

    @property
    def is_balanced(self):
        """Check if budget is balanced (total planned equals zero)"""
        income = self.budget_categories.filter(
            category__is_income=True).aggregate(
            total=Sum('planned_amount'))['total'] or Decimal('0.00')
        expenses = self.budget_categories.filter(
            category__is_income=False).aggregate(
            total=Sum('planned_amount'))['total'] or Decimal('0.00')
        return abs(income - expenses) < Decimal('0.01')  # Using small decimal for float comparison

    def get_category_spending(self, category):
        """Get actual spending for a specific category"""
        return self.transaction_set.filter(
            category=category).aggregate(
            total=Sum('amount'))['total'] or Decimal('0.00')

    def transfer_amount(self, from_category, to_category, amount):
        """Transfer amount between budget categories"""
        if amount <= 0:
            raise ValidationError("Transfer amount must be positive")

        from_budget_category = self.budget_categories.get(category=from_category)
        to_budget_category = self.budget_categories.get(category=to_category)

        if from_budget_category.planned_amount < amount:
            raise ValidationError("Insufficient funds in source category")

        from_budget_category.planned_amount -= amount
        to_budget_category.planned_amount += amount

        from_budget_category.save()
        to_budget_category.save()
        


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_income = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']


class BudgetCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='budget_categories')
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    planned_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    class Meta:
        unique_together = ['budget', 'category']
        verbose_name_plural = 'Budget Categories'

    @property
    def actual_amount(self):
        """Calculate actual spending for this category"""
        return self.budget.transaction_set.filter(
            category=self.category).aggregate(
            total=Sum('amount'))['total'] or Decimal('0.00')

    @property
    def remaining_amount(self):
        """Calculate remaining amount in this category"""
        return self.planned_amount - self.actual_amount

    def clean(self):
        super().clean()
        if self.planned_amount < 0 and not self.category.is_income:
            raise ValidationError("Planned amount cannot be negative for expense categories")


class RecurringExpense(models.Model):
    FREQUENCY_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('BIWEEKLY', 'Bi-weekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('YEARLY', 'Yearly'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    start_date = models.DateField()
    next_due_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plaid_transaction_id = models.CharField(max_length=255, null=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    budget = models.ForeignKey(Budget, on_delete=models.SET_NULL, null=True)
    description = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateField()
    description = models.CharField(max_length=255)
    merchant = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-transaction_date']

    def save(self, *args, **kwargs):
        # Ensure transaction amount is positive for income categories
        if self.category and self.category.is_income and self.amount < 0:
            self.amount = abs(self.amount)
        # Ensure transaction amount is negative for expense categories
        elif self.category and not self.category.is_income and self.amount > 0:
            self.amount = -abs(self.amount)
        super().save(*args, **kwargs)