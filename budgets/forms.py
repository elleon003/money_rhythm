from django import forms
from django.contrib.auth import get_user_model
from .models import Budget, Category, BudgetCategory, RecurringExpense, Transaction
from django.db import models
from django.db.models import Q

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['name', 'start_date', 'end_date', 'shared_with']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Budget Name'
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'shared_with': forms.SelectMultiple(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            })
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Remove user from kwargs before calling super
        super().__init__(*args, **kwargs)
        if self.user:
            # Filter shared_with to exclude the owner and only show active users
            self.fields['shared_with'].queryset = get_user_model().objects.exclude(
                id=self.user.id
            ).filter(is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("End date must be after start date")
        return cleaned_data

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'is_income']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Category Name'
            }),
            'is_income': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500'
            })
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        # Check if category name already exists for this user
        if Category.objects.filter(
            owner=self.instance.owner if self.instance.pk else self.initial.get('owner'),
            name__iexact=name
        ).exclude(pk=self.instance.pk if self.instance.pk else None).exists():
            raise forms.ValidationError("A category with this name already exists.")
        return name


class BudgetCategoryForm(forms.ModelForm):
    class Meta:
        model = BudgetCategory
        fields = ['budget', 'category', 'planned_amount']
        widgets = {
            'budget': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'planned_amount': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01'
            })
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['budget'].queryset = Budget.objects.filter(
                Q(owner=user) | Q(shared_with=user)
            ).distinct()
            self.fields['category'].queryset = Category.objects.filter(owner=user)

class RecurringExpenseForm(forms.ModelForm):
    class Meta:
        model = RecurringExpense
        fields = ['category', 'name', 'amount', 'frequency', 'start_date', 'end_date', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Expense Name'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01'
            }),
            'frequency': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500'
            })
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(owner=user)

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['category', 'amount', 'transaction_date', 'description', 'merchant']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01'
            }),
            'transaction_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'description': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Transaction Description'
            }),
            'merchant': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Merchant Name (Optional)'
            })
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Filter categories and budgets based on user access
            self.fields['category'].queryset = Category.objects.filter(owner=user)
            
            # If budget_id is provided, further filter categories to those in the budget
            if budget_id:
                try:
                    budget = Budget.objects.get(pk=budget_id)
                    category_ids = budget.budget_categories.values_list('category_id', flat=True)
                    self.fields['category'].queryset = self.fields['category'].queryset.filter(
                        id__in=category_ids
                    )
                except Budget.DoesNotExist:
                    pass


    def clean_amount(self):
        """
        Ensure amount is properly formatted and handled based on category type
        """
        amount = self.cleaned_data.get('amount')
        category = self.cleaned_data.get('category')
        
        if not amount:
            raise forms.ValidationError("Amount is required")
        
        if category and category.is_income:
            # Ensure income amounts are positive
            return abs(amount)
        else:
            # Ensure expense amounts are negative
            return -abs(amount)

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('transaction_date')
        category = cleaned_data.get('category')
        amount = cleaned_data.get('amount')

        if category and amount:
            # Ensure amount is positive for income categories and negative for expense categories
            if category.is_income and amount < 0:
                cleaned_data['amount'] = abs(amount)
            elif not category.is_income and amount > 0:
                cleaned_data['amount'] = -abs(amount)
                
        return cleaned_data
