from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    TYPE_CHOICES = [
        ('Income', 'Income'),
        ('Expense', 'Expense')
    ]
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    TYPE_CATEGORY_INCOME = [
        ('Salary', 'Salary'),
        ('Business', 'Business'),
        ('Interest', 'Interest'),
        ('Other', 'Other')
    ]
    category_income = models.CharField(max_length=10, choices=TYPE_CATEGORY_INCOME, null=True, blank=True)
    TYPE_CATEGORY_EXPENSE = [
        ('Food', 'Food'),
        ('Transport', 'Transport'),
        ('Health', 'Health'),
        ('Entertainment', 'Entertainment'),
        ('Education', 'Education'),
        ('Clothing', 'Clothing'),
        ('Insurance', 'Insurance'),
        ('Rent', 'Rent'),
        ('Bills', 'Bills'),
        ('Other', 'Other')
    ]
    category_expense = models.CharField(max_length=20, choices=TYPE_CATEGORY_EXPENSE, null=True, blank=True)

    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=100, blank=True)