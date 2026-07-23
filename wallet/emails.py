import threading
from django.core.mail import send_mail
from django.conf import settings


def _send_async(subject, message, recipient):
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=True,
        )
    except Exception:
        pass


def send_deposit_email(user, amount, balance):
    if not user.email:
        return
    subject = 'Deposit Successful — Vault'
    message = f'''Hello {user.first_name or user.username},

Your deposit was successful!

Amount Deposited: UGX {amount:,.0f}
New Balance: UGX {balance:,.0f}

— The Vault Team'''
    t = threading.Thread(target=_send_async, args=(subject, message, user.email))
    t.daemon = True
    t.start()


def send_withdrawal_email(user, amount, balance):
    if not user.email:
        return
    subject = 'Withdrawal Successful — Vault'
    message = f'''Hello {user.first_name or user.username},

Your withdrawal was successful!

Amount Withdrawn: UGX {amount:,.0f}
Remaining Balance: UGX {balance:,.0f}

If you did not make this withdrawal, please contact us immediately.

— The Vault Team'''
    t = threading.Thread(target=_send_async, args=(subject, message, user.email))
    t.daemon = True
    t.start()


def send_transfer_sent_email(user, amount, recipient_username, balance):
    if not user.email:
        return
    subject = 'Transfer Sent — Vault'
    message = f'''Hello {user.first_name or user.username},

Your transfer was successful!

Amount Sent: UGX {amount:,.0f}
Sent To: @{recipient_username}
Remaining Balance: UGX {balance:,.0f}

If you did not make this transfer, please contact us immediately.

— The Vault Team'''
    t = threading.Thread(target=_send_async, args=(subject, message, user.email))
    t.daemon = True
    t.start()


def send_transfer_received_email(user, amount, sender_username, balance):
    if not user.email:
        return
    subject = 'Money Received — Vault'
    message = f'''Hello {user.first_name or user.username},

You have received money!

Amount Received: UGX {amount:,.0f}
Sent By: @{sender_username}
New Balance: UGX {balance:,.0f}

— The Vault Team'''
    t = threading.Thread(target=_send_async, args=(subject, message, user.email))
    t.daemon = True
    t.start()