from django.contrib import admin
from .models import Wallet, Transaction, TransferRequest, Recipient, UtilityPayment



@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'currency', 'created_at']
    search_fields = ['user__username', 'user__email']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'transaction_type', 'amount', 'status', 'description', 'created_at']
    list_filter = ['transaction_type', 'status']
    search_fields = ['wallet__user__username', 'description']


@admin.register(TransferRequest)
class TransferRequestAdmin(admin.ModelAdmin):
    list_display = ['sender_wallet', 'receiver_wallet', 'amount', 'created_at']

@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'name', 'username', 'created_at']

    @admin.register(UtilityPayment)
class UtilityPaymentAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'category', 'provider', 'account_number', 'amount', 'status', 'created_at']
    list_filter = ['category', 'status']