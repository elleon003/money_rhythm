from django.db import models


class PlaidItem(models.Model):
    access_token = models.CharField(max_length=255)
    item_id = models.CharField(max_length=255)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='plaid_items')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.item_id
    
    class Meta:
        verbose_name = 'Plaid Item'
        verbose_name_plural = 'Plaid Items'


class BankAccount(models.Model):
    account_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    available_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_synced_at = models.DateTimeField(auto_now=True)

    ACCOUNT_TYPES = (
        ('checking', 'Checking'),
        ('savings', 'Savings'),
        ('credit_card', 'Credit Card'),
        ('loan', 'Loan')
    )

    type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    plaid_item = models.ForeignKey(PlaidItem, on_delete=models.CASCADE, related_name='bank_accounts', null=True, blank=True)

    def __str__(self):
        return self.name
