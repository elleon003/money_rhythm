# api/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from budgets.models import Budget, Category, BudgetCategory, RecurringExpense, Transaction
from .serializers import (
    BudgetSerializer,
    CategorySerializer,
    BudgetCategorySerializer,
    RecurringExpenseSerializer,
    TransactionSerializer
)

class IsOwnerOrShared(permissions.BasePermission):
    """
    Custom permission to only allow owners or shared users of an object to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if user is owner
        if hasattr(obj, 'owner'):
            if obj.owner == request.user:
                return True
        
        # Check if user has shared access
        if hasattr(obj, 'shared_with'):
            if request.user in obj.shared_with.all():
                return True
            
        return False

class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrShared]

    def get_queryset(self):
        return Budget.objects.filter(
            Q(owner=self.request.user) | 
            Q(shared_with=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def transfer(self, request, pk=None):
        budget = self.get_object()
        try:
            from_category_id = request.data.get('from_category')
            to_category_id = request.data.get('to_category')
            amount = Decimal(request.data.get('amount', '0'))

            from_category = Category.objects.get(id=from_category_id)
            to_category = Category.objects.get(id=to_category_id)

            budget.transfer_amount(from_category, to_category, amount)
            return Response({'status': 'transfer successful'})
        except (Category.DoesNotExist, ValueError, ValidationError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrShared]

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class BudgetCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetCategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrShared]

    def get_queryset(self):
        return BudgetCategory.objects.filter(
            Q(budget__owner=self.request.user) | 
            Q(budget__shared_with=self.request.user)
        ).distinct()

# api/views.py (continued)

class RecurringExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = RecurringExpenseSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrShared]

    def get_queryset(self):
        return RecurringExpense.objects.filter(
            Q(owner=self.request.user) | 
            Q(budget__shared_with=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        recurring_expense = self.get_object()
        recurring_expense.is_active = not recurring_expense.is_active
        recurring_expense.save()
        return Response({
            'status': 'success',
            'is_active': recurring_expense.is_active
        })

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrShared]

    def get_queryset(self):
        return Transaction.objects.filter(
            Q(owner=self.request.user) | 
            Q(budget__owner=self.request.user) |
            Q(budget__shared_with=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Return the most recent transactions"""
        recent_transactions = self.get_queryset().order_by('-date')[:10]
        serializer = self.get_serializer(recent_transactions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Return transactions grouped by category"""
        category_id = request.query_params.get('category_id')
        if not category_id:
            return Response(
                {'error': 'category_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        transactions = self.get_queryset().filter(category_id=category_id)
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_date_range(self, request):
        """Return transactions within a date range"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            return Response(
                {'error': 'start_date and end_date are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        transactions = self.get_queryset().filter(
            date__range=[start_date, end_date]
        ).order_by('-date')
        
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)
