from django.urls import path
from . import views

urlpatterns = [
    # ==================== MAIN PAGES ====================
    path('', views.dashboard, name='dashboard'),
    path('assets/', views.assetlist, name='asset_list'),
    path('add/', views.addasset, name='add_asset'),

    # ==================== ASSET MANAGEMENT ====================
    path('asset/<int:pk>/edit/', views.asset_edit, name='asset_edit'),
    path('asset/<int:pk>/delete/', views.asset_delete, name='asset_delete'),

    # ==================== TICKETING SYSTEM ====================
    path('ticket/raise/<int:asset_pk>/', views.raise_ticket, name='raise_ticket'),
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('ticket/<int:pk>/', views.ticket_detail, name='ticket_detail'),
    path('ticket/<int:pk>/update/', views.ticket_update, name='ticket_update'),

    # ==================== FUTURE FEATURES ====================
    path('reports/', views.reports, name='reports'),
    path('users/', views.users_list, name='users'),
]