from django import forms
from .models import Transaction

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'category_income', 'category_expense', 'date', 'amount', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'category_income': forms.Select(attrs={'required': False}),
            'category_expense': forms.Select(attrs={'required': False}),
        }

    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')
        category_income = cleaned_data.get('category_income')
        category_expense = cleaned_data.get('category_expense')

        if transaction_type == 'Income' and not category_income:
            raise forms.ValidationError('Please select an income category')
        if transaction_type == 'Expense' and not category_expense:
            raise forms.ValidationError('Please select an expense category')

        return cleaned_data