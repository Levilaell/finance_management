"""
Companies app URLs
"""
from django.urls import path

from .views import (
    CompanyDetailView,
    CompanyUpdateView,
    SubscriptionPlansView,
    UpgradeSubscriptionView,
    CancelSubscriptionView,
    CompanyUsersView,
    InviteUserView,
    RemoveUserView,
)

app_name = 'companies'

urlpatterns = [
    # Default company profile (same as profile/)
    path('', CompanyDetailView.as_view(), name='company-index'),
    
    # Company management
    path('profile/', CompanyDetailView.as_view(), name='company-detail'),
    path('update/', CompanyUpdateView.as_view(), name='company-update'),
    
    # Subscription management
    path('subscription/plans/', SubscriptionPlansView.as_view(), name='subscription-plans'),
    path('subscription/upgrade/', UpgradeSubscriptionView.as_view(), name='subscription-upgrade'),
    path('subscription/cancel/', CancelSubscriptionView.as_view(), name='subscription-cancel'),
    
    # User management (for Enterprise plans)
    path('users/', CompanyUsersView.as_view(), name='company-users'),
    path('users/invite/', InviteUserView.as_view(), name='invite-user'),
    path('users/<int:user_id>/remove/', RemoveUserView.as_view(), name='remove-user'),
]