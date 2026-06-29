import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wallet_project.settings')
django.setup()

from django.contrib.auth.models import User
from wallet.models import Wallet, Transaction
from decimal import Decimal

# Create demo user
if not User.objects.filter(username='demo').exists():
    user = User.objects.create_user(
        username='demo', password='demo1234',
        first_name='Demo', last_name='User', email='demo@vault.app'
    )
    w = Wallet.objects.create(user=user, balance=Decimal('1250.00'))
    Transaction.objects.create(wallet=w, transaction_type='deposit', amount=Decimal('2000.00'), description='Initial deposit', status='completed')
    Transaction.objects.create(wallet=w, transaction_type='withdrawal', amount=Decimal('500.00'), description='Rent', status='completed')
    Transaction.objects.create(wallet=w, transaction_type='transfer_out', amount=Decimal('250.00'), description='Transfer to @alice: Dinner split', status='completed')
    print("Demo user created: username=demo, password=demo1234")

# Create second user for transfer demo
if not User.objects.filter(username='alice').exists():
    alice = User.objects.create_user(
        username='alice', password='alice1234',
        first_name='Alice', last_name='Smith', email='alice@vault.app'
    )
    aw = Wallet.objects.create(user=alice, balance=Decimal('850.00'))
    Transaction.objects.create(wallet=aw, transaction_type='transfer_in', amount=Decimal('250.00'), description='Transfer from @demo: Dinner split', status='completed')
    print("Alice user created: username=alice, password=alice1234")

print("\nSeeding done!")
