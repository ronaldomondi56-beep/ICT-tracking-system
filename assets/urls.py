from django.urls import path
from . import views

urlpatterns = [

    # ==================== AUTHENTICATION ====================
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # ==================== DASHBOARD ====================
    path('', views.dashboard, name='dashboard'),

    # ==================== ASSET MANAGEMENT ====================
    path('assets/', views.assetlist, name='asset_list'),
    path('add/', views.addasset, name='add_asset'),
    path('asset/<int:pk>/edit/', views.asset_edit, name='asset_edit'),
    path('asset/<int:pk>/delete/', views.asset_delete, name='asset_delete'),

    # ==================== TICKETING SYSTEM ====================
    path('ticket/raise/<int:asset_pk>/', views.raise_ticket, name='raise_ticket'),
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('ticket/<int:pk>/', views.ticket_detail, name='ticket_detail'),

    # ==================== TICKET WORKFLOW ====================
    path('ticket/<int:pk>/assign/', views.assign_technician, name='assign_technician'),
    path('ticket/<int:pk>/start-repair/', views.start_repair, name='start_repair'),          # ← Added
    path('ticket/<int:pk>/request-replacement/', views.request_replacement, name='request_replacement'),
    path('ticket/<int:pk>/resolve/', views.resolve_ticket, name='resolve_ticket'),           # Recommended to add

    # ==================== FINANCE ====================
    path('finance/approvals/', views.finance_approval_list, name='finance_approval_list'),
    path('finance/approval/<int:pk>/', views.finance_approval_detail, name='finance_approval_detail'),

    # ==================== REPORTS & USERS ====================
    path('reports/', views.reports, name='reports'),
    path('users/', views.users_list, name='users'),
]