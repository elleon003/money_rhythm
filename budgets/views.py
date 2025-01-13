from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Sum, Count, DecimalField
from django.db.models.functions import Coalesce, TruncMonth
from django.utils import timezone
from .models import Budget, Category, BudgetCategory, RecurringExpense, Transaction
from .forms import BudgetForm, CategoryForm, BudgetCategoryForm, RecurringExpenseForm, TransactionForm
from decimal import Decimal


class OwnershipRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'budgets/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get active budgets
        active_budgets = Budget.objects.filter(
            Q(owner=self.request.user) | Q(shared_with=self.request.user),
            is_active=True,
            end_date__gte=timezone.now().date()
        ).distinct()

        # Get recent transactions
        recent_transactions = Transaction.objects.filter(
            Q(owner=self.request.user) | 
            Q(budget__owner=self.request.user) |
            Q(budget__shared_with=self.request.user)
        ).order_by('-transaction_date')[:5]

        # Get upcoming recurring expenses
        upcoming_expenses = RecurringExpense.objects.filter(
            Q(end_date__isnull=True) | Q(end_date__gte=timezone.now().date()),
            owner=self.request.user,
            is_active=True
        )  # TODO: Add ordering by next_due_date once the field is added

        # Calculate total monthly spending
        current_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_spending = Transaction.objects.filter(
            Q(owner=self.request.user) | 
            Q(budget__owner=self.request.user) |
            Q(budget__shared_with=self.request.user),
            transaction_date__gte=current_month_start,
            amount__lt=0  # Only expenses
        ).aggregate(total=Sum('amount'))['total'] or 0

        context.update({
            'active_budgets': active_budgets,
            'recent_transactions': recent_transactions,
            'upcoming_expenses': upcoming_expenses,
            'monthly_spending': abs(monthly_spending),
            'total_budgets': active_budgets.count(),
        })
        return context


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
        budget = self.object
        
        # Get categories for this budget
        context['categories'] = self.object.budget_categories.all()
        
        # Get transactions for the budget period and categories
        category_ids = self.object.budget_categories.values_list('category_id', flat=True)
        context['transactions'] = Transaction.objects.filter(
            category_id__in=category_ids,
            transaction_date__gte=budget.start_date,
            transaction_date__lte=budget.end_date
        ).order_by('-transaction_date')[:10]
        
        return context 

class BudgetCreateView(LoginRequiredMixin, CreateView):
    model = Budget
    form_class = BudgetForm
    template_name = 'budgets/budget_form.html'
    success_url = reverse_lazy('budgets:budget-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Budget created successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print("Create View Context:", context)
        print("Form instance pk:", context['form'].instance.pk)
        context['view_type'] = 'create'
        return context

class BudgetUpdateView(LoginRequiredMixin, UpdateView):
    model = Budget
    form_class = BudgetForm
    template_name = 'budgets/budget_form.html'
    success_url = reverse_lazy('budgets:budget-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Budget updated successfully!')
        return super().form_valid(form)

    def get_queryset(self):
        return Budget.objects.filter(
            Q(owner=self.request.user) | 
            Q(shared_with=self.request.user)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print("Update View Context:", context)
        print("Form instance pk:", context['form'].instance.pk)
        context['view_type'] = 'update'  # Add this line
        return context

class BudgetDeleteView(LoginRequiredMixin, OwnershipRequiredMixin, DeleteView):
    model = Budget
    success_url = reverse_lazy('budgets:budget-list')
    template_name = 'budgets/budget_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Budget deleted successfully.')
        return super().delete(request, *args, **kwargs)


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'budgets/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        # Start with the base queryset of user's categories
        queryset = Category.objects.filter(owner=self.request.user)

        # Annotate with budget and transaction totals
        return queryset.annotate(
            total_budgeted=Coalesce(
                Sum('budgetcategory__planned_amount', output_field=DecimalField()),
                Decimal('0.00')
            ),
            total_spent=Coalesce(
                Sum('transaction__amount', output_field=DecimalField()),
                Decimal('0.00')
            )
        ).order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add summary statistics
        total_stats = self.get_queryset().aggregate(
            total_income_budgeted=Sum(
                'total_budgeted',
                filter=Q(is_income=True)
            ),
            total_expense_budgeted=Sum(
                'total_budgeted',
                filter=Q(is_income=False)
            ),
            total_income_actual=Sum(
                'total_spent',
                filter=Q(is_income=True)
            ),
            total_expense_actual=Sum(
                'total_spent',
                filter=Q(is_income=False)
            )
        )

        # Replace None values with 0
        for key, value in total_stats.items():
            if value is None:
                total_stats[key] = Decimal('0.00')

        context.update({
            'total_stats': total_stats,
            'category_count': self.get_queryset().count(),
            'income_categories': self.get_queryset().filter(is_income=True).count(),
            'expense_categories': self.get_queryset().filter(is_income=False).count(),
        })
        
        return context

class CategoryDetailView(LoginRequiredMixin, DetailView):
    model = Category
    template_name = 'budgets/category_detail.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.object

        # Get budgets using this category
        budget_categories = category.budget_categories.select_related('budget').order_by('-budget__start_date')

        # Get recent transactions
        recent_transactions = category.transaction_set.select_related('budget').order_by('-date')[:10]

        # Calculate monthly totals for the last 6 months
        monthly_totals = category.transaction_set.annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            total=Sum('amount')
        ).order_by('-month')[:6]

        # Calculate overall statistics
        stats = {
            'total_budgeted': budget_categories.aggregate(
                total=Coalesce(Sum('planned_amount'), Decimal('0.00'))
            )['total'],
            'total_actual': recent_transactions.aggregate(
                total=Coalesce(Sum('amount'), Decimal('0.00'))
            )['total'],
            'total_transactions': category.transaction_set.count(),
            'active_budgets': budget_categories.filter(
                budget__end_date__gte=timezone.now().date()
            ).count()
        }

        context.update({
            'budget_categories': budget_categories,
            'recent_transactions': recent_transactions,
            'monthly_totals': monthly_totals,
            'stats': stats,
        })
        return context

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'budgets/category_form.html'
    success_url = reverse_lazy('budgets:category-list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Category created successfully!')
        return response

class CategoryUpdateView(LoginRequiredMixin, OwnershipRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'budgets/category_form.html'
    success_url = reverse_lazy('budgets:category-list')

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)    

    def form_valid(self, form):
        # Ensure owner is still set during updates
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Category updated successfully!')
        return response

class CategoryDeleteView(LoginRequiredMixin, OwnershipRequiredMixin, DeleteView):
    model = Category
    success_url = reverse_lazy('budgets:category-list')
    template_name = 'budgets/category_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Category deleted successfully.')
        return super().delete(request, *args, **kwargs)


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
        context['transactions'] = self.object.transaction_set.all().order_by('-transaction_date')[:10]
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
        context['transactions'] = self.object.transaction_set.all().order_by('-transaction_date')[:10]
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

class RecurringExpenseDeleteView(LoginRequiredMixin, OwnershipRequiredMixin, DeleteView):
    model = RecurringExpense
    success_url = reverse_lazy('budgets:recurring-expense-list')
    template_name = 'budgets/recurring_expense_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Recurring expense deleted successfully.')
        return super().delete(request, *args, **kwargs)


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

        # Filter by budget if specified
        budget_id = self.request.GET.get('budget')
        if budget_id:
            try:
                budget = Budget.objects.get(pk=budget_id)
                category_ids = budget.budget_categories.values_list('category_id', flat=True)
                queryset = queryset.filter(
                    category_id__in=category_ids,
                    transaction_date__gte=budget.start_date,
                    transaction_date__lte=budget.end_date
                )
            except Budget.DoesNotExist:
                pass

        return queryset.order_by('-transaction_date')

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

class TransactionDeleteView(LoginRequiredMixin, OwnershipRequiredMixin, DeleteView):
    model = Transaction
    template_name = 'budgets/transaction_confirm_delete.html'
    
    def get_success_url(self):
        if 'budget' in self.request.GET:
            return reverse_lazy('budgets:budget-detail', kwargs={'pk': self.request.GET['budget']})
        return reverse_lazy('budgets:transaction-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Transaction deleted successfully.')
        return super().delete(request, *args, **kwargs)