from wallet.models import KYCDocument, WithdrawalRequest, FraudFlag

def admin_counts(request):
    if request.user.is_authenticated and request.user.is_staff:
        return {
            'pending_kyc_count': KYCDocument.objects.filter(status='pending').count(),
            'pending_withdrawal_count': WithdrawalRequest.objects.filter(status='pending').count(),
            'active_flag_count': FraudFlag.objects.filter(resolved=False).count(),
        }
    return {}