from django.core.mail import send_mail
from django.conf import settings


def send_deposit_email(user, amount, balance):
    subject = 'Deposit Successful — Vault'
    message = f'''
Hello {user.first_name or user.username},

Your deposit was successful!

Amount Deposited: UGX {amount:,.0f}
New Balance: UGX {balance:,.0f}

Thank you for using Vault.

— The Vault Team
'''
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=True,
    )


def send_withdrawal_email(user, amount, balance):
    subject = 'Withdrawal Successful — Vault'
    message = f'''
Hello {user.first_name or user.username},

Your withdrawal was successful!

Amount Withdrawn: UGX {amount:,.0f}
Remaining Balance: UGX {balance:,.0f}

If you did not make this withdrawal, please contact us immediately.

— The Vault Team
'''
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=True,
    )


def send_transfer_sent_email(user, amount, recipient_username, balance):
    subject = 'Transfer Sent — Vault'
    message = f'''
Hello {user.first_name or user.username},

Your transfer was successful!

Amount Sent: UGX {amount:,.0f}
Sent To: @{recipient_username}
Remaining Balance: UGX {balance:,.0f}

If you did not make this transfer, please contact us immediately.

— The Vault Team
'''
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=True,
    )


def send_transfer_received_email(user, amount, sender_username, balance):
    subject = 'Money Received — Vault'
    message = f'''
Hello {user.first_name or user.username},

You have received money!

Amount Received: UGX {amount:,.0f}
Sent By: @{sender_username}
New Balance: UGX {balance:,.0f}

— The Vault Team
'''
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=True,
    )