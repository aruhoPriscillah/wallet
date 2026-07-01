from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta
from wallet.models import (Wallet, Transaction, KYCDocument,
                           WithdrawalRequest, FraudFlag, WalletFreeze)


def admin_required(view_func):
    return staff_member_required(view_func, login_url='/login/')


@admin_required
def admin_dashboard(request):
    now = timezone.now()
    today = now.date()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    # Stats
    total_users = User.objects.count()
    new_users_today = User.objects.filter(date_joined__date=today).count()
    new_users_week = User.objects.filter(date_joined__gte=week_ago).count()

    total_wallets = Wallet.objects.count()
    total_balance = Wallet.objects.aggregate(t=Sum('balance'))['t'] or 0
    frozen_wallets = WalletFreeze.objects.filter(is_active=True).count()

    total_transactions = Transaction.objects.count()
    transactions_today = Transaction.objects.filter(created_at__date=today).count()
    volume_today = Transaction.objects.filter(
        created_at__date=today, status='completed'
    ).aggregate(t=Sum('amount'))['t'] or 0
    volume_month = Transaction.objects.filter(
        created_at__gte=month_ago, status='completed'
    ).aggregate(t=Sum('amount'))['t'] or 0

    pending_kyc = KYCDocument.objects.filter(status='pending').count()
    pending_withdrawals = WithdrawalRequest.objects.filter(status='pending').count()
    active_flags = FraudFlag.objects.filter(resolved=False).count()
    high_flags = FraudFlag.objects.filter(resolved=False, severity='high').count()

    recent_transactions = Transaction.objects.select_related(
        'wallet__user'
    ).all()[:10]

    recent_flags = FraudFlag.objects.filter(
        resolved=False
    ).select_related('wallet__user').order_by('-created_at')[:5]

    # Daily transaction volume for chart (last 7 days)
    chart_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        vol = Transaction.objects.filter(
            created_at__date=day, status='completed'
        ).aggregate(t=Sum('amount'))['t'] or 0
        chart_data.append({'date': day.strftime('%b %d'), 'amount': float(vol)})

    return render(request, 'vadmin/dashboard.html', {
        'total_users': total_users,
        'new_users_today': new_users_today,
        'new_users_week': new_users_week,
        'total_balance': total_balance,
        'frozen_wallets': frozen_wallets,
        'total_transactions': total_transactions,
        'transactions_today': transactions_today,
        'volume_today': volume_today,
        'volume_month': volume_month,
        'pending_kyc': pending_kyc,
        'pending_withdrawals': pending_withdrawals,
        'active_flags': active_flags,
        'high_flags': high_flags,
        'recent_transactions': recent_transactions,
        'recent_flags': recent_flags,
        'chart_data': chart_data,
    })


@admin_required
def manage_users(request):
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')
    users = User.objects.select_related('wallet').order_by('-date_joined')
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
    if status == 'frozen':
        users = users.filter(wallet__freeze__is_active=True)
    elif status == 'active':
        users = users.exclude(wallet__freeze__is_active=True)

    return render(request, 'vadmin/users.html', {
        'users': users, 'query': query, 'status': status
    })


@admin_required
def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    wallet, _ = Wallet.objects.get_or_create(user=user)
    transactions = wallet.transactions.all()[:20]
    try:
        kyc = wallet.kyc
    except KYCDocument.DoesNotExist:
        kyc = None
    try:
        freeze = wallet.freeze
        is_frozen = freeze.is_active
    except WalletFreeze.DoesNotExist:
        freeze = None
        is_frozen = False
    flags = wallet.fraud_flags.all()
    return render(request, 'vadmin/user_detail.html', {
        'viewed_user': user, 'wallet': wallet, 'transactions': transactions,
        'kyc': kyc, 'freeze': freeze, 'is_frozen': is_frozen, 'flags': flags,
    })


@admin_required
def freeze_wallet(request, wallet_id):
    wallet = get_object_or_404(Wallet, id=wallet_id)
    if request.method == 'POST':
        reason = request.POST.get('reason', 'Suspicious activity')
        freeze, created = WalletFreeze.objects.get_or_create(wallet=wallet)
        freeze.reason = reason
        freeze.frozen_by = request.user
        freeze.is_active = True
        freeze.save()
        messages.success(request, f'Wallet for @{wallet.user.username} has been frozen.')
        return redirect('admin_user_detail', user_id=wallet.user.id)
    return redirect('admin_user_detail', user_id=wallet.user.id)


@admin_required
def unfreeze_wallet(request, wallet_id):
    wallet = get_object_or_404(Wallet, id=wallet_id)
    try:
        wallet.freeze.is_active = False
        wallet.freeze.save()
        messages.success(request, f'Wallet for @{wallet.user.username} has been unfrozen.')
    except WalletFreeze.DoesNotExist:
        pass
    return redirect('admin_user_detail', user_id=wallet.user.id)


@admin_required
def kyc_list(request):
    status = request.GET.get('status', 'pending')
    docs = KYCDocument.objects.select_related(
        'wallet__user'
    ).filter(status=status).order_by('-submitted_at')
    return render(request, 'vadmin/kyc.html', {'docs': docs, 'status': status})


@admin_required
def kyc_review(request, doc_id):
    doc = get_object_or_404(KYCDocument, id=doc_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        doc.notes = notes
        doc.reviewed_at = timezone.now()
        if action == 'approve':
            doc.status = 'approved'
            messages.success(request, f'KYC approved for @{doc.wallet.user.username}.')
        elif action == 'reject':
            doc.status = 'rejected'
            messages.warning(request, f'KYC rejected for @{doc.wallet.user.username}.')
        doc.save()
        return redirect('admin_kyc')
    return render(request, 'vadmin/kyc_review.html', {'doc': doc})


@admin_required
def withdrawals(request):
    status = request.GET.get('status', 'pending')
    reqs = WithdrawalRequest.objects.select_related(
        'wallet__user'
    ).filter(status=status).order_by('-requested_at')
    return render(request, 'vadmin/withdrawals.html', {'requests': reqs, 'status': status})


@admin_required
def withdrawal_review(request, req_id):
    req = get_object_or_404(WithdrawalRequest, id=req_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('admin_notes', '')
        req.admin_notes = notes
        req.reviewed_at = timezone.now()
        if action == 'approve':
            req.status = 'approved'
            messages.success(request, f'Withdrawal of UGX {req.amount:,.0f} approved.')
        elif action == 'reject':
            req.status = 'rejected'
            req.wallet.balance += req.amount
            req.wallet.save()
            messages.warning(request, f'Withdrawal rejected. Balance refunded.')
        req.save()
        return redirect('admin_withdrawals')
    return render(request, 'vadmin/withdrawal_review.html', {'req': req})


@admin_required
def all_transactions(request):
    txn_type = request.GET.get('type', '')
    query = request.GET.get('q', '')
    txns = Transaction.objects.select_related('wallet__user').order_by('-created_at')
    if txn_type:
        txns = txns.filter(transaction_type=txn_type)
    if query:
        txns = txns.filter(
            Q(wallet__user__username__icontains=query) |
            Q(description__icontains=query)
        )
    return render(request, 'vadmin/transactions.html', {
        'transactions': txns[:100], 'filter_type': txn_type, 'query': query
    })


@admin_required
def fraud_monitoring(request):
    severity = request.GET.get('severity', '')
    flags = FraudFlag.objects.select_related('wallet__user').filter(resolved=False)
    if severity:
        flags = flags.filter(severity=severity)
    flags = flags.order_by('-created_at')
    return render(request, 'vadmin/fraud.html', {'flags': flags, 'severity': severity})


@admin_required
def resolve_flag(request, flag_id):
    flag = get_object_or_404(FraudFlag, id=flag_id)
    flag.resolved = True
    flag.save()
    messages.success(request, 'Fraud flag resolved.')
    return redirect('admin_fraud')


@admin_required
def add_fraud_flag(request, wallet_id):
    wallet = get_object_or_404(Wallet, id=wallet_id)
    if request.method == 'POST':
        reason = request.POST.get('reason')
        severity = request.POST.get('severity', 'low')
        FraudFlag.objects.create(wallet=wallet, reason=reason, severity=severity)
        messages.success(request, f'Fraud flag added for @{wallet.user.username}.')
    return redirect('admin_user_detail', user_id=wallet.user.id)


@admin_required
def reports(request):
    from django.utils import timezone
    now = timezone.now()
    month_ago = now - timedelta(days=30)

    top_users = Wallet.objects.annotate(
        txn_count=Count('transactions'),
        txn_volume=Sum('transactions__amount')
    ).order_by('-txn_volume')[:10]

    deposit_total = Transaction.objects.filter(
        transaction_type='deposit', status='completed',
        created_at__gte=month_ago
    ).aggregate(t=Sum('amount'))['t'] or 0

    withdrawal_total = Transaction.objects.filter(
        transaction_type='withdrawal', status='completed',
        created_at__gte=month_ago
    ).aggregate(t=Sum('amount'))['t'] or 0

    transfer_total = Transaction.objects.filter(
        transaction_type='transfer_out', status='completed',
        created_at__gte=month_ago
    ).aggregate(t=Sum('amount'))['t'] or 0

    return render(request, 'vadmin/reports.html', {
        'top_users': top_users,
        'deposit_total': deposit_total,
        'withdrawal_total': withdrawal_total,
        'transfer_total': transfer_total,
    })