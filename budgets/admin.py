from django.contrib import admin
from .models import Budget, Category, BudgetCategory, RecurringExpense, Transaction

admin.site.register(Budget)
admin.site.register(Category)
admin.site.register(BudgetCategory)
admin.site.register(RecurringExpense)
admin.site.register(Transaction)