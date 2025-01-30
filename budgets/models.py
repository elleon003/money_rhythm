from django.db import models

class Budget(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    owner = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='budgets')
    total_planned = models.DecimalField(max_digits=10, decimal_places=2)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-start_date']


class BudgetItem(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='items')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Category(models.Model):
    name = models.CharField(max_length=255)
    icon = models.CharField(max_length=255)
    color = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_system = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        if not self.is_system:
            super().save(*args, **kwargs)
        else:
            self.is_active = True
            super().save(*args, **kwargs)

