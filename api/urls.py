from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'budgets', views.BudgetViewSet, basename='api-budget')
router.register(r'categories', views.CategoryViewSet, basename='api-category')
router.register(r'budget-categories', views.BudgetCategoryViewSet, basename='api-budget-category')
router.register(r'recurring-expenses', views.RecurringExpenseViewSet, basename='api-recurring-expense')
router.register(r'transactions', views.TransactionViewSet, basename='api-transaction')

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
]
