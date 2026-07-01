from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_wallet_for_new_user(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.get_or_create(user=instance)

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, default='UGX')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Wallet — {self.currency} {self.balance}"


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer_in', 'Transfer In'),
        ('transfer_out', 'Transfer Out'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='completed')
    description = models.CharField(max_length=255, blank=True)
    reference = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_type} — {self.amount} ({self.status})"


class TransferRequest(models.Model):
    sender_wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='sent_transfers')
    receiver_wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='received_transfers')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transfer {self.amount} from {self.sender_wallet.user.username} to {self.receiver_wallet.user.username}"

class Recipient(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='recipients')
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['wallet', 'username']

    def __str__(self):
        return f"{self.name} (@{self.username})"


class UtilityPayment(models.Model):
    CATEGORY_CHOICES = [
        ('airtime', 'Airtime'),
        ('internet', 'Internet'),
        ('tv', 'TV Subscription'),
        ('school', 'School Fees'),
        ('electricity', 'Electricity'),
        ('water', 'Water'),
    ]

    PROVIDER_CHOICES = {
        'airtime': ['MTN', 'Airtel', 'Lycamobile'],
        'internet': ['MTN MiFi', 'Airtel 4G', 'Liquid Telecom', 'Roke Telecom'],
        'tv': ['DSTV', 'GOtv', 'Startimes', 'Azam TV'],
        'school': ['Other'],
        'electricity': ['UMEME', 'KPLC'],
        'water': ['NWSC'],
    }

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='utility_payments')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    provider = models.CharField(max_length=50)
    account_number = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=[
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ], default='completed')
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.category} — {self.provider} — UGX {self.amount}"