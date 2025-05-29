from django.urls import path

from .views import (
    ChangePasswordView,
    CustomTokenRefreshView,
    EmailVerificationView,
    LoginView,
    LogoutView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    ProfileView,
    RegisterView,
    ResendVerificationView,
    health_check,
    Setup2FAView,
    Enable2FAView,
    Disable2FAView,
    BackupCodesView,
)

app_name = 'authentication'

urlpatterns = [
    # Health check
    path('health/', health_check, name='health'),
    
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    
    # Profile
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    # Password reset
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # Email verification
    path('verify-email/', EmailVerificationView.as_view(), name='verify_email'),
    path('resend-verification/', ResendVerificationView.as_view(), name='resend_verification'),
    
    # 2FA endpoints
    path('2fa/setup/', Setup2FAView.as_view(), name='setup_2fa'),
    path('2fa/enable/', Enable2FAView.as_view(), name='enable_2fa'),
    path('2fa/disable/', Disable2FAView.as_view(), name='disable_2fa'),
    path('2fa/backup-codes/', BackupCodesView.as_view(), name='backup_codes'),
]