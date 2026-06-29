#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate

# Fix duplicate social apps
python manage.py shell << 'EOF'
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

# Delete all Google apps and recreate one clean one
SocialApp.objects.filter(provider='google').delete()

app = SocialApp.objects.create(
    provider='google',
    name='Google',
    client_id='YOUR_ACTUAL_CLIENT_ID',
    secret='YOUR_ACTUAL_SECRET_KEY',
)

# Link to the correct site
site = Site.objects.get_or_create(
    domain='wallet-dxed.onrender.com',
    defaults={'name': 'wallet-dxed.onrender.com'}
)[0]
app.sites.add(site)
print(f"Created Google app, linked to site ID: {site.id}")
EOF