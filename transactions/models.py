from django.db import models


class Transaction(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='transactions')
    plaid_transaction_id = models.CharField(max_length=255, null=True)
    account = models.ForeignKey('plaid_app.BankAccount', on_delete=models.CASCADE, related_name='transactions')
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey('budgets.Category', on_delete=models.CASCADE, related_name='transactions')
    merchant = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    pending = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.description


class RecurringTransaction(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='recurring_transactions')
    account = models.ForeignKey('plaid_app.PlaidAccount', on_delete=models.CASCADE, related_name='recurring_transactions')
    category = models.ForeignKey('budgets.Category', on_delete=models.CASCADE, related_name='recurring_transactions')
    name = models.CharField(max_length=255)
    next_due_date = models.DateField()
    account = models.ForeignKey('plaid_app.BankAccount', on_delete=models.CASCADE, related_name='recurring_transactions')
    merchant = models.CharField(max_length=255)
    notes = models.TextField(null=True)

    FREQUENCY_CHOICES = (
        ('weekly', 'Weekly'),
        ('biweekly', 'Biweekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    )
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.name
    

class Transfer(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='transfers')
    plaid_transfer_id = models.CharField(max_length=255, null=True)
    account = models.ForeignKey('plaid_app.BankAccount', on_delete=models.CASCADE, related_name='transfers')
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    source_account = models.ForeignKey('plaid_app.BankAccount', on_delete=models.CASCADE, related_name='outgoing_transfers')
    destination_account = models.ForeignKey('plaid_app.BankAccount', on_delete=models.CASCADE, related_name='incoming_transfers')
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.description