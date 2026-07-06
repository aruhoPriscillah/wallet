from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('users/', views.manage_users, name='admin_users'),
    path('users/<int:user_id>/', views.user_detail, name='admin_user_detail'),
    path('users/freeze/<int:wallet_id>/', views.freeze_wallet, name='admin_freeze'),
    path('users/unfreeze/<int:wallet_id>/', views.unfreeze_wallet, name='admin_unfreeze'),
    path('kyc/', views.kyc_list, name='admin_kyc'),
    path('kyc/<int:doc_id>/', views.kyc_review, name='admin_kyc_review'),
    path('withdrawals/', views.withdrawals, name='admin_withdrawals'),
    path('withdrawals/<int:req_id>/', views.withdrawal_review, name='admin_withdrawal_review'),
    path('transactions/', views.transactions, name='admin_transactions'),
    path('fraud/', views.fraud_monitoring, name='admin_fraud'),
    path('fraud/resolve/<int:flag_id>/', views.resolve_flag, name='admin_resolve_flag'),
    path('fraud/flag/<int:wallet_id>/', views.add_fraud_flag, name='admin_add_flag'),
    path('reports/', views.reports, name='admin_reports'),
    path('export/', views.export_report, name='admin_export'),
]