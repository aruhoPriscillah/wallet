from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction as db_transaction
from django.db.models import Sum, Q
from decimal import Decimal
from .models import Wallet, Transaction, TransferRequest
from .forms import RegisterForm, DepositForm, WithdrawForm, TransferForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Wallet.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name}! Your wallet is ready.')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'wallet/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'wallet/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    wallet = request.user.wallet
    recent_txns = wallet.transactions.all()[:5]
    total_in = wallet.transactions.filter(
        transaction_type__in=['deposit', 'transfer_in'], status='completed'
    ).aggregate(t=Sum('amount'))['t'] or 0
    total_out = wallet.transactions.filter(
        transaction_type__in=['withdrawal', 'transfer_out'], status='completed'
    ).aggregate(t=Sum('amount'))['t'] or 0
    return render(request, 'wallet/dashboard.html', {
        'wallet': wallet,
        'recent_txns': recent_txns,
        'total_in': total_in,
        'total_out': total_out,
    })


@login_required
def deposit(request):
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            description = form.cleaned_data.get('description', '') or 'Deposit'
            with db_transaction.atomic():
                wallet = request.user.wallet
                wallet.balance += amount
                wallet.save()
                Transaction.objects.create(
                    wallet=wallet,
                    transaction_type='deposit',
                    amount=amount,
                    description=description,
                    status='completed',
                )
            messages.success(request, f'UGX{amount:,.2f} deposited successfully.')
            return redirect('dashboard')
    else:
        form = DepositForm()
    return render(request, 'wallet/deposit.html', {'form': form})


@login_required
def withdraw(request):
    if request.method == 'POST':
        form = WithdrawForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            description = form.cleaned_data.get('description', '') or 'Withdrawal'
            wallet = request.user.wallet
            if wallet.balance < amount:
                messages.error(request, 'Insufficient balance.')
            else:
                with db_transaction.atomic():
                    wallet.balance -= amount
                    wallet.save()
                    Transaction.objects.create(
                        wallet=wallet,
                        transaction_type='withdrawal',
                        amount=amount,
                        description=description,
                        status='completed',
                    )
                messages.success(request, f'UGX{amount:,.2f} withdrawn successfully.')
                return redirect('dashboard')
    else:
        form = WithdrawForm()
    return render(request, 'wallet/withdraw.html', {'form': form, 'wallet': request.user.wallet})


@login_required
def transfer(request):
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['recipient_username']
            amount = form.cleaned_data['amount']
            note = form.cleaned_data.get('note', '') or 'Transfer'
            sender_wallet = request.user.wallet

            if username == request.user.username:
                messages.error(request, "You can't transfer to yourself.")
            else:
                try:
                    recipient = User.objects.get(username=username)
                    receiver_wallet = recipient.wallet
                    if sender_wallet.balance < amount:
                        messages.error(request, 'Insufficient balance.')
                    else:
                        with db_transaction.atomic():
                            sender_wallet.balance -= amount
                            sender_wallet.save()
                            receiver_wallet.balance += amount
                            receiver_wallet.save()
                            Transaction.objects.create(
                                wallet=sender_wallet,
                                transaction_type='transfer_out',
                                amount=amount,
                                description=f'Transfer to @{username}: {note}',
                                status='completed',
                            )
                            Transaction.objects.create(
                                wallet=receiver_wallet,
                                transaction_type='transfer_in',
                                amount=amount,
                                description=f'Transfer from @{request.user.username}: {note}',
                                status='completed',
                            )
                        messages.success(request, f'UGX {amount:,.0f} sent to @{username}.')
                        return redirect('dashboard')
                except User.DoesNotExist:
                    messages.error(request, f'User "{username}" not found.')
    else:
        initial = {}
        to = request.GET.get('to', '')
        if to:
            initial['recipient_username'] = to
        form = TransferForm(initial=initial)

    return render(request, 'wallet/transfer.html', {'form': form, 'wallet': request.user.wallet})


@login_required
def transactions(request):
    wallet = request.user.wallet
    txn_type = request.GET.get('type', '')
    txns = wallet.transactions.all()
    if txn_type:
        txns = txns.filter(transaction_type=txn_type)
    return render(request, 'wallet/transactions.html', {
        'transactions': txns,
        'wallet': wallet,
        'filter_type': txn_type,
    })


@login_required
def recipients(request):
    wallet = request.user.wallet
    if request.method == 'POST':
        form = RecipientForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            username = form.cleaned_data['username']
            # check the user actually exists
            if not User.objects.filter(username=username).exists():
                messages.error(request, f'No user found with username "{username}".')
            elif username == request.user.username:
                messages.error(request, "You can't add yourself as a recipient.")
            else:
                _, created = Recipient.objects.get_or_create(
                    wallet=wallet, username=username,
                    defaults={'name': name}
                )
                if created:
                    messages.success(request, f'{name} added to your recipients.')
                else:
                    messages.error(request, f'@{username} is already in your recipients.')
    else:
        form = RecipientForm()

    all_recipients = wallet.recipients.all()
    return render(request, 'wallet/recipients.html', {
        'form': form,
        'recipients': all_recipients,
    })


@login_required
def delete_recipient(request, recipient_id):
    wallet = request.user.wallet
    try:
        recipient = wallet.recipients.get(id=recipient_id)
        recipient.delete()
        messages.success(request, 'Recipient removed.')
    except Recipient.DoesNotExist:
        messages.error(request, 'Recipient not found.')
    return redirect('recipients')