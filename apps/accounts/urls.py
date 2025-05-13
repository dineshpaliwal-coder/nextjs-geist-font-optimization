from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='accounts:login'), name='logout'),
    
    # Password Management
    path('password/change/', views.CustomPasswordChangeView.as_view(), 
         name='password_change'),
    path('password/change/done/', auth_views.PasswordChangeDoneView.as_view(), 
         name='password_change_done'),
    path('password/reset/', views.CustomPasswordResetView.as_view(), 
         name='password_reset'),
    path('password/reset/done/', auth_views.PasswordResetDoneView.as_view(), 
         name='password_reset_done'),
    path('password/reset/<uidb64>/<token>/', 
         views.CustomPasswordResetConfirmView.as_view(), 
         name='password_reset_confirm'),
    path('password/reset/complete/', 
         auth_views.PasswordResetCompleteView.as_view(), 
         name='password_reset_complete'),
    
    # User Profile Management
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('profile/security/', views.SecuritySettingsView.as_view(), 
         name='security_settings'),
    
    # Two-Factor Authentication
    path('2fa/setup/', views.TwoFactorSetupView.as_view(), name='2fa_setup'),
    path('2fa/enable/', views.TwoFactorEnableView.as_view(), name='2fa_enable'),
    path('2fa/disable/', views.TwoFactorDisableView.as_view(), name='2fa_disable'),
    path('2fa/verify/', views.TwoFactorVerifyView.as_view(), name='2fa_verify'),
    
    # API Key Management
    path('api-keys/', views.APIKeyListView.as_view(), name='api_key_list'),
    path('api-keys/generate/', views.APIKeyGenerateView.as_view(), 
         name='api_key_generate'),
    path('api-keys/revoke/', views.APIKeyRevokeView.as_view(), 
         name='api_key_revoke'),
    
    # Role Management (for tenant admins)
    path('roles/', views.RoleListView.as_view(), name='role_list'),
    path('roles/create/', views.RoleCreateView.as_view(), name='role_create'),
    path('roles/<uuid:pk>/edit/', views.RoleUpdateView.as_view(), 
         name='role_edit'),
    path('roles/<uuid:pk>/delete/', views.RoleDeleteView.as_view(), 
         name='role_delete'),
    
    # User Management (for tenant admins)
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/create/', views.UserCreateView.as_view(), name='user_create'),
    path('users/<uuid:pk>/edit/', views.UserUpdateView.as_view(), 
         name='user_edit'),
    path('users/<uuid:pk>/delete/', views.UserDeleteView.as_view(), 
         name='user_delete'),
    path('users/<uuid:pk>/roles/', views.UserRoleManageView.as_view(), 
         name='user_roles'),
    
    # Session Management
    path('sessions/', views.SessionListView.as_view(), name='session_list'),
    path('sessions/revoke/<str:session_key>/', views.SessionRevokeView.as_view(), 
         name='session_revoke'),
    path('sessions/revoke-all/', views.SessionRevokeAllView.as_view(), 
         name='session_revoke_all'),
    
    # Activity Monitoring
    path('activity/', views.UserActivityView.as_view(), name='activity_log'),
    path('login-history/', views.LoginHistoryView.as_view(), name='login_history'),
    
    # Tenant User Invitations
    path('invitations/', views.InvitationListView.as_view(), 
         name='invitation_list'),
    path('invitations/send/', views.InvitationCreateView.as_view(), 
         name='invitation_create'),
    path('invitations/<uuid:token>/accept/', views.InvitationAcceptView.as_view(), 
         name='invitation_accept'),
    path('invitations/<uuid:token>/decline/', 
         views.InvitationDeclineView.as_view(), 
         name='invitation_decline'),
]

# API URLs - these will be included in the main API urls.py
api_urlpatterns = [
    path('profile/', views.UserProfileAPIView.as_view(), name='api_profile'),
    path('users/', views.UserListAPIView.as_view(), name='api_user_list'),
    path('users/<uuid:pk>/', views.UserDetailAPIView.as_view(), 
         name='api_user_detail'),
    path('roles/', views.RoleListAPIView.as_view(), name='api_role_list'),
    path('roles/<uuid:pk>/', views.RoleDetailAPIView.as_view(), 
         name='api_role_detail'),
]
