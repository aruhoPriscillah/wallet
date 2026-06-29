# Vault — Django Digital Wallet

A clean, full-featured digital wallet app built with Django.

## Features
- User registration & login
- Wallet balance tracking
- Deposit funds
- Withdraw funds (with balance validation)
- Transfer money between users (atomic transactions)
- Full transaction history with filtering
- Django admin panel

## Quick Start

```bash
# Install dependencies
pip install django

# Apply migrations
python manage.py migrate

# Load demo data (optional)
python seed.py

# Run server
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`

## Demo Accounts
| Username | Password    | Balance    |
|----------|-------------|------------|
| demo     | demo1234    | UGX1,250.00  |
| alice    | alice1234   | UGX850.00    |

## Admin
Create a superuser to access `/admin/`:
```bash
python manage.py createsuperuser
```

## Project Structure
```
wallet_project/
├── wallet/
│   ├── models.py      # Wallet, Transaction, TransferRequest
│   ├── views.py       # Dashboard, deposit, withdraw, transfer
│   ├── forms.py       # All form classes
│   ├── urls.py        # App URL routing
│   └── admin.py       # Admin registration
├── templates/
│   └── wallet/        # HTML templates
├── wallet_project/
│   ├── settings.py
│   └── urls.py
├── seed.py            # Demo data seeder
└── manage.py
```

## Models
- **Wallet**: OneToOne with User, tracks balance & currency
- **Transaction**: UUID PK, type (deposit/withdrawal/transfer_in/transfer_out), amount, status, description
- **TransferRequest**: Links sender & receiver wallets with amount

## Security Notes
- All balance operations use `db_transaction.atomic()` for data integrity
- Balance checked before any withdrawal or transfer
- CSRF protection on all forms
- Change `SECRET_KEY` and set `DEBUG=False` in production
