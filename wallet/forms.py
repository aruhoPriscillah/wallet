from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Transaction


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class DepositForm(forms.Form):
    amount = forms.DecimalField(min_value=1, max_digits=10, decimal_places=2,
                                widget=forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}))
    description = forms.CharField(max_length=255, required=False,
                                   widget=forms.TextInput(attrs={'placeholder': 'e.g. Salary, Freelance...'}))


class WithdrawForm(forms.Form):
    amount = forms.DecimalField(min_value=1, max_digits=10, decimal_places=2,
                                widget=forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}))
    description = forms.CharField(max_length=255, required=False,
                                   widget=forms.TextInput(attrs={'placeholder': 'e.g. Rent, Groceries...'}))


class TransferForm(forms.Form):
    recipient_username = forms.CharField(max_length=150,
                                          widget=forms.TextInput(attrs={'placeholder': 'Enter username'}))
    amount = forms.DecimalField(min_value=1, max_digits=10, decimal_places=2,
                                widget=forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}))
    note = forms.CharField(max_length=255, required=False,
                           widget=forms.TextInput(attrs={'placeholder': 'Optional note...'}))

class RecipientForm(forms.Form):
    name = forms.CharField(max_length=100,
                           widget=forms.TextInput(attrs={'placeholder': 'e.g. Jane Doe'}))
    username = forms.CharField(max_length=150,
                               widget=forms.TextInput(attrs={'placeholder': 'their username'}))


class UtilityPaymentForm(forms.Form):
    CATEGORY_CHOICES = [
        ('', 'Select category...'),
        ('airtime', 'Airtime'),
        ('internet', 'Internet'),
        ('tv', 'TV Subscription'),
        ('school', 'School Fees'),
        ('electricity', 'Electricity'),
        ('water', 'Water'),
    ]

    category = forms.ChoiceField(choices=CATEGORY_CHOICES)
    provider = forms.CharField(max_length=50,
                               widget=forms.TextInput(attrs={'placeholder': 'e.g. MTN, DSTV...'}))
    account_number = forms.CharField(max_length=100,
                                     widget=forms.TextInput(attrs={'placeholder': 'Phone number, account or card number'}))
    amount = forms.DecimalField(min_value=1, max_digits=10, decimal_places=2,
                                widget=forms.NumberInput(attrs={'placeholder': '0', 'step': '1'}))
    note = forms.CharField(max_length=255, required=False,
                           widget=forms.TextInput(attrs={'placeholder': 'Optional note'}))