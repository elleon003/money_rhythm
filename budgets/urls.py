from django.urls import path
from . import views

app_name = 'budgets'

urlpatterns = [
    # Budget URLs
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('budgets/', views.BudgetListView.as_view(), name='budget-list'),
    path('budget/create/', views.BudgetCreateView.as_view(), name='budget-create'),
    path('budget/<uuid:pk>/', views.BudgetDetailView.as_view(), name='budget-detail'),
    path('budget/<uuid:pk>/update/', views.BudgetUpdateView.as_view(), name='budget-update'),
    path('budget/<uuid:pk>/delete/', views.BudgetDeleteView.as_view(),name='budget-delete'),

    # Category URLs
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('category/create/', views.CategoryCreateView.as_view(), name='category-create'),
    path('category/<uuid:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
    path('category/<uuid:pk>/update/', views.CategoryUpdateView.as_view(), name='category-update'),
    path('category/<uuid:pk>/delete/',
         views.CategoryDeleteView.as_view(),
         name='category-delete'),

    # Budget Category URLs
    path('budget-categories/', views.BudgetCategoryListView.as_view(), name='budget-category-list'),
    path('budget-category/create/', views.BudgetCategoryCreateView.as_view(), name='budget-category-create'),
    path('budget-category/<uuid:pk>/', views.BudgetCategoryDetailView.as_view(), name='budget-category-detail'),
    path('budget-category/<uuid:pk>/update/', views.BudgetCategoryUpdateView.as_view(), name='budget-category-update'),

    # Recurring Expense URLs
    path('recurring-expenses/', views.RecurringExpenseListView.as_view(), name='recurring-expense-list'),
    path('recurring-expense/create/', views.RecurringExpenseCreateView.as_view(), name='recurring-expense-create'),
    path('recurring-expense/<uuid:pk>/', views.RecurringExpenseDetailView.as_view(), name='recurring-expense-detail'),
    path('recurring-expense/<uuid:pk>/update/', views.RecurringExpenseUpdateView.as_view(), name='recurring-expense-update'),
    path('recurring-expense/<uuid:pk>/delete/',
         views.RecurringExpenseDeleteView.as_view(),
         name='recurring-expense-delete'),

    # Transaction URLs
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    path('transaction/create/', views.TransactionCreateView.as_view(), name='transaction-create'),
    path('transaction/<uuid:pk>/', views.TransactionDetailView.as_view(), name='transaction-detail'),
    path('transaction/<uuid:pk>/update/', views.TransactionUpdateView.as_view(), name='transaction-update'),
    path('transaction/<uuid:pk>/delete/',
         views.TransactionDeleteView.as_view(),
         name='transaction-delete'),
]


