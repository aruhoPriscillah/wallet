from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('wallet.urls')),
    path('recipients/', views.recipients, name='recipients'),
path('recipients/delete/<int:recipient_id>/', views.delete_recipient, name='delete_recipient'),
]
