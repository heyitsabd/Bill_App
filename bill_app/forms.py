# bill_app/forms.py

from django import forms
from .models import User, Expense, Split

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'name', 'mobile_number']

class ExpenseForm(forms.ModelForm):
    split_type = forms.ChoiceField(choices=[
        ('equal', 'Equal'),
        ('exact', 'Exact Amount'),
        ('percentage', 'Percentage'),
    ], required=True)
    
    class Meta:
        model = Expense
        fields = ['amount', 'description', 'split_type']

class SplitForm(forms.ModelForm):
    SPLIT_CHOICES = [
        ('equal', 'Equal'),
        ('exact', 'Exact'),
        ('percentage', 'Percentage'),
    ]
    
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Users'
    )
    amount = forms.DecimalField(decimal_places=2, max_digits=10, label='Amount')
    description = forms.CharField(max_length=200, label='Description')
    split_type = forms.ChoiceField(choices=SPLIT_CHOICES, label='Split Type')
    percentage = forms.JSONField(required=False, label='Percentages')  # For percentage split
    exact_amount = forms.JSONField(required=False, label='Exact Amounts')  # For exact split

    class Meta:
        model = Split
        fields = ['users', 'amount', 'description', 'split_type', 'percentage', 'exact_amount']

    def clean(self):
        cleaned_data = super().clean()
        split_type = cleaned_data.get('split_type')
        
        if split_type == 'exact':
            exact_amounts = cleaned_data.get('exact_amount')
            if not exact_amounts:
                raise forms.ValidationError('Exact amounts are required for exact split.')
        elif split_type == 'percentage':
            percentages = cleaned_data.get('percentage')
            if not percentages:
                raise forms.ValidationError('Percentages are required for percentage split.')
            if sum(percentages.values()) != 100:
                raise forms.ValidationError('Percentages must add up to 100%.')
