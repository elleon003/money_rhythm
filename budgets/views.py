from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Budget, Category, BudgetCategory, RecurringExpense, Transaction
from .forms import BudgetForm, CategoryForm, BudgetCategoryForm, RecurringExpenseForm, TransactionForm


class BudgetListView(LoginRequiredMixin, ListView):
    model = Budget
    template_name = 'budgets/budget_list.html'
    context_object_name = 'budgets'

    def get_queryset(self):
        return Budget.objects.filter(
            Q(owner=self.request.user) | 
            Q(shared_with=self.request.user)
        ).distinct()

class BudgetDetailView(LoginRequiredMixin, DetailView):
    model = Budget
    template_name = 'budgets/budget_detail.html'
    context_object_name = 'budget'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = self.object.budget_categories.all()
        context['transactions'] = self.object.transaction_set.all().order_by('-date')[:10]
        return context 

class BudgetCreateView(LoginRequiredMixin, CreateView):
    model = Budget
    form_class = BudgetForm
    template_name = 'budgets/budget_form.html'
    success_url = reverse_lazy('budget-list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Budget created successfully!')
        return super().form_valid(form)

class BudgetUpdateView(LoginRequiredMixin, UpdateView):
    model = Budget
    form_class = BudgetForm
    template_name = 'budgets/budget_form.html'
    success_url = reverse_lazy('budget-list')

    def form_valid(self, form):
        messages.success(self.request, 'Budget updated successfully!')
        return super().form_valid(form)


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'budgets/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(
            Q(owner=self.request.user) | 
            Q(shared_with=self.request.user)
        ).distinct()

class CategoryDetailView(LoginRequiredMixin, DetailView):
    model = Category
    template_name = 'budgets/category_detail.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['budget_categories'] = self.object.budget_categories.all()
        return context

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'budgets/category_form.html'
    success_url = reverse_lazy('category-list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Category created successfully!')
        return super().form_valid(form)

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'budgets/category_form.html'
    success_url = reverse_lazy('category-list')

    def form_valid(self, form):
        messages.success(self.request, 'Category updated successfully!')
        return super().form_valid(form)


class BudgetCategoryListView(LoginRequiredMixin, ListView):
    model = BudgetCategory
    template_name = 'budgets/budgetcategory_list.html'
    context_object_name = 'budget_categories'

    def get_queryset(self):
        return BudgetCategory.objects.filter(
            Q(budget__owner=self.request.user) | 
            Q(budget__shared_with=self.request.user)
        ).distinct()

class BudgetCategoryDetailView(LoginRequiredMixin, DetailView):
    model = BudgetCategory
    template_name = 'budgets/budgetcategory_detail.html'
    context_object_name = 'budget_category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transactions'] = self.object.transaction_set.all().order_by('-date')[:10]
        return context

class BudgetCategoryCreateView(LoginRequiredMixin, CreateView):
    model = BudgetCategory
    form_class = BudgetCategoryForm
    template_name = 'budgets/budgetcategory_form.html'
    success_url = reverse_lazy('budget-list')

    def form_valid(self, form):
        messages.success(self.request, 'Budget category created successfully!')
        return super().form_valid(form)

class BudgetCategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = BudgetCategory
    form_class = BudgetCategoryForm
    template_name = 'budgets/budgetcategory_form.html'
    success_url = reverse_lazy('budget-list')

    def form_valid(self, form):
        messages.success(self.request, 'Budget category updated successfully!')
        return super().form_valid(form)


class RecurringExpenseListView(LoginRequiredMixin, ListView):
    model = RecurringExpense
    template_name = 'budgets/recurringexpense_list.html'
    context_object_name = 'recurring_expenses'

    def get_queryset(self):
        return RecurringExpense.objects.filter(
            Q(owner=self.request.user) | 
            Q(shared_with=self.request.user)
        ).distinct()

class RecurringExpenseDetailView(LoginRequiredMixin, DetailView):
    model = RecurringExpense
    template_name = 'budgets/recurringexpense_detail.html'
    context_object_name = 'recurring_expense'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transactions'] = self.object.transaction_set.all().order_by('-date')[:10]
        return context

class RecurringExpenseCreateView(LoginRequiredMixin, CreateView):
    model = RecurringExpense
    form_class = RecurringExpenseForm
    template_name = 'budgets/recurringexpense_form.html'
    success_url = reverse_lazy('recurring-expense-list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Recurring expense created successfully!')
        return super().form_valid(form)

class RecurringExpenseUpdateView(LoginRequiredMixin, UpdateView):
    model = RecurringExpense
    form_class = RecurringExpenseForm
    template_name = 'budgets/recurringexpense_form.html'
    success_url = reverse_lazy('recurring-expense-list')

    def form_valid(self, form):
        messages.success(self.request, 'Recurring expense updated successfully!')
        return super().form_valid(form)


class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'budgets/transaction_list.html'
    context_object_name = 'transactions'

    def get_queryset(self):
        return Transaction.objects.filter(
            Q(owner=self.request.user) | 
            Q(recurring_expense__owner=self.request.user) | 
            Q(budget_category__budget__owner=self.request.user) | 
            Q(budget_category__budget__shared_with=self.request.user)
        ).distinct()


class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'budgets/transaction_list.html'
    context_object_name = 'transactions'

    def get_queryset(self):
        return Transaction.objects.filter(
            Q(owner=self.request.user) | 
            Q(recurring_expense__owner=self.request.user) | 
            Q(budget_category__budget__owner=self.request.user) | 
            Q(budget_category__budget__shared_with=self.request.user)
        ).distinct()

class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = Transaction
    template_name = 'budgets/transaction_detail.html'
    context_object_name = 'transaction'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transactions'] = self.object.transactions.all()
        return context

class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'budgets/transaction_form.html'
    success_url = reverse_lazy('transaction-list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Transaction created successfully!')
        return super().form_valid(form)

class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'budgets/transaction_form.html'
    success_url = reverse_lazy('transaction-list')

    def form_valid(self, form):
        messages.success(self.request, 'Transaction updated successfully!')
        return super().form_valid(form)
