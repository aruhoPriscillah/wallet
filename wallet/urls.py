from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('deposit/', views.deposit, name='deposit'),
    path('withdraw/', views.withdraw, name='withdraw'),
    path('transfer/', views.transfer, name='transfer'),
    path('transactions/', views.transactions, name='transactions'),
    path('recipients/', views.recipients, name='recipients'),
    path('recipients/delete/<int:recipient_id>/', views.delete_recipient, name='delete_recipient'),
]