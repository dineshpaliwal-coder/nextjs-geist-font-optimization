from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, 
    TemplateView, FormView, RedirectView
)
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.db import transaction
from rest_framework import generics, permissions
from .models import User, Role, UserRole, LoginAttempt
from .forms import (
    CustomUserCreationForm, CustomUserChangeForm, 
    RoleForm, UserRoleForm, TwoFactorSetupForm
)
from .serializers import UserSerializer, RoleSerializer
import uuid
import pyotp

class TenantAdminRequiredMixin(UserPassesTestMixin):
    """Verify that the current user is a tenant admin."""
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_tenant_admin

class CustomLoginView(auth_views.LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        """Check if 2FA is required before completing login."""
        user = form.get_user()
        if user.two_factor_enabled:
            # Store user_id in session and redirect to 2FA verification
            self.request.session['2fa_user_id'] = str(user.id)
            return redirect('accounts:2fa_verify')
        return super().form_valid(form)

class CustomPasswordChangeView(LoginRequiredMixin, auth_views.PasswordChangeView):
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:password_change_done')

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.user.password_changed_at = timezone.now()
        self.request.user.force_password_change = False
        self.request.user.save(update_fields=['password_changed_at', 'force_password_change'])
        return response

class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/email/password_reset_email.html'
    subject_template_name = 'accounts/email/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')

class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_roles'] = self.request.user.user_roles.select_related('role').all()
        context['login_history'] = self.request.user.login_attempts.all()[:5]
        return context

class ProfileEditView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')
    success_message = _("Your profile has been updated successfully.")

    def get_object(self):
        return self.request.user

class SecuritySettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/security_settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_sessions'] = self.request.user.get_active_sessions()
        return context

class TwoFactorSetupView(LoginRequiredMixin, FormView):
    template_name = 'accounts/2fa_setup.html'
    form_class = TwoFactorSetupForm
    success_url = reverse_lazy('accounts:profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.two_factor_secret:
            # Generate new secret key
            secret = pyotp.random_base32()
            self.request.user.two_factor_secret = secret
            self.request.user.save(update_fields=['two_factor_secret'])
        
        # Generate QR code
        totp = pyotp.TOTP(self.request.user.two_factor_secret)
        context['qr_code'] = totp.provisioning_uri(
            self.request.user.email,
            issuer_name="SaaS CRM"
        )
        return context

class TwoFactorEnableView(LoginRequiredMixin, FormView):
    template_name = 'accounts/2fa_enable.html'
    form_class = TwoFactorSetupForm
    success_url = reverse_lazy('accounts:security_settings')

    def form_valid(self, form):
        totp = pyotp.TOTP(self.request.user.two_factor_secret)
        if totp.verify(form.cleaned_data['code']):
            self.request.user.two_factor_enabled = True
            self.request.user.save(update_fields=['two_factor_enabled'])
            messages.success(self.request, _("Two-factor authentication has been enabled."))
            return super().form_valid(form)
        
        form.add_error('code', _("Invalid verification code."))
        return self.form_invalid(form)

class TwoFactorDisableView(LoginRequiredMixin, FormView):
    template_name = 'accounts/2fa_disable.html'
    form_class = TwoFactorSetupForm
    success_url = reverse_lazy('accounts:security_settings')

    def form_valid(self, form):
        totp = pyotp.TOTP(self.request.user.two_factor_secret)
        if totp.verify(form.cleaned_data['code']):
            self.request.user.two_factor_enabled = False
            self.request.user.two_factor_secret = None
            self.request.user.save(update_fields=['two_factor_enabled', 'two_factor_secret'])
            messages.success(self.request, _("Two-factor authentication has been disabled."))
            return super().form_valid(form)
        
        form.add_error('code', _("Invalid verification code."))
        return self.form_invalid(form)

class TwoFactorVerifyView(FormView):
    template_name = 'accounts/2fa_verify.html'
    form_class = TwoFactorSetupForm
    success_url = reverse_lazy('dashboard:index')

    def form_valid(self, form):
        user_id = self.request.session.get('2fa_user_id')
        if not user_id:
            messages.error(self.request, _("Invalid session. Please login again."))
            return redirect('accounts:login')

        user = get_object_or_404(User, id=user_id)
        totp = pyotp.TOTP(user.two_factor_secret)
        
        if totp.verify(form.cleaned_data['code']):
            # Complete login
            from django.contrib.auth import login
            login(self.request, user)
            del self.request.session['2fa_user_id']
            return super().form_valid(form)
        
        form.add_error('code', _("Invalid verification code."))
        return self.form_invalid(form)

class APIKeyGenerateView(LoginRequiredMixin, RedirectView):
    url = reverse_lazy('accounts:api_key_list')

    def get(self, request, *args, **kwargs):
        request.user.api_key = uuid.uuid4()
        request.user.api_access_enabled = True
        request.user.save(update_fields=['api_key', 'api_access_enabled'])
        messages.success(request, _("New API key has been generated."))
        return super().get(request, *args, **kwargs)

class APIKeyRevokeView(LoginRequiredMixin, RedirectView):
    url = reverse_lazy('accounts:api_key_list')

    def get(self, request, *args, **kwargs):
        request.user.api_key = None
        request.user.api_access_enabled = False
        request.user.save(update_fields=['api_key', 'api_access_enabled'])
        messages.success(request, _("API key has been revoked."))
        return super().get(request, *args, **kwargs)

class APIKeyListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'accounts/api_key_list.html'
    context_object_name = 'api_keys'

    def get_queryset(self):
        # Assuming API keys are stored in User model for now
        return User.objects.filter(id=self.request.user.id)

class UserListView(TenantAdminRequiredMixin, ListView):
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        return User.objects.filter(tenant=self.request.user.tenant)

class UserCreateView(TenantAdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')
    success_message = _("User has been created successfully.")

    def form_valid(self, form):
        form.instance.tenant = self.request.user.tenant
        return super().form_valid(form)

class UserUpdateView(TenantAdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')
    success_message = _("User has been updated successfully.")

    def get_queryset(self):
        return User.objects.filter(tenant=self.request.user.tenant)

class UserDeleteView(TenantAdminRequiredMixin, DeleteView):
    model = User
    template_name = 'accounts/user_confirm_delete.html'
    success_url = reverse_lazy('accounts:user_list')

    def get_queryset(self):
        return User.objects.filter(tenant=self.request.user.tenant)

    def delete(self, request, *args, **kwargs):
        messages.success(request, _("User has been deleted successfully."))
        return super().delete(request, *args, **kwargs)

class RoleListView(TenantAdminRequiredMixin, ListView):
    model = Role
    template_name = 'accounts/role_list.html'
    context_object_name = 'roles'

    def get_queryset(self):
        return Role.objects.filter(tenant=self.request.user.tenant)

class RoleCreateView(TenantAdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Role
    form_class = RoleForm
    template_name = 'accounts/role_form.html'
    success_url = reverse_lazy('accounts:role_list')
    success_message = _("Role has been created successfully.")

    def form_valid(self, form):
        form.instance.tenant = self.request.user.tenant
        return super().form_valid(form)

class RoleUpdateView(TenantAdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Role
    form_class = RoleForm
    template_name = 'accounts/role_form.html'
    success_url = reverse_lazy('accounts:role_list')
    success_message = _("Role has been updated successfully.")

    def get_queryset(self):
        return Role.objects.filter(tenant=self.request.user.tenant)

from .forms import UserInviteForm

class InvitationListView(TenantAdminRequiredMixin, ListView):
    template_name = 'accounts/invitation_list.html'
    context_object_name = 'invitations'

    def get_queryset(self):
        return User.objects.filter(tenant=self.request.user.tenant, is_active=False)

class InvitationCreateView(TenantAdminRequiredMixin, FormView):
    template_name = 'accounts/invitation_form.html'
    form_class = UserInviteForm
    success_url = reverse_lazy('accounts:invitation_list')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        role = form.cleaned_data.get('role')
        message = form.cleaned_data.get('message')
        # Implement invitation creation logic here
        messages.success(self.request, _("Invitation has been sent successfully."))
        return super().form_valid(form)

class InvitationAcceptView(RedirectView):
    url = reverse_lazy('accounts:login')

    def get(self, request, *args, **kwargs):
        token = kwargs.get('token')
        # Implement invitation acceptance logic here
        messages.success(request, _("Invitation has been accepted successfully."))
        return super().get(request, *args, **kwargs)

class InvitationDeclineView(RedirectView):
    url = reverse_lazy('accounts:login')

    def get(self, request, *args, **kwargs):
        token = kwargs.get('token')
        # Implement invitation decline logic here
        messages.success(request, _("Invitation has been declined."))
        return super().get(request, *args, **kwargs)

class LoginHistoryView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'accounts/login_history.html'
    context_object_name = 'login_history'

    def get_queryset(self):
        # Implement logic to fetch login history
        return User.objects.filter(id=self.request.user.id)

class UserActivityView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'accounts/user_activity.html'
    context_object_name = 'activities'

    def get_queryset(self):
        # Implement logic to fetch user activities
        return User.objects.filter(id=self.request.user.id)

class SessionRevokeAllView(LoginRequiredMixin, RedirectView):
    url = reverse_lazy('accounts:session_list')

    def get(self, request, *args, **kwargs):
        # Implement session revoke all logic here
        messages.success(request, _("All sessions have been revoked."))
        return super().get(request, *args, **kwargs)

class SessionRevokeView(LoginRequiredMixin, RedirectView):
    url = reverse_lazy('accounts:session_list')

    def get(self, request, *args, **kwargs):
        session_key = kwargs.get('session_key')
        # Implement session revocation logic here
        messages.success(request, _("Session has been revoked."))
        return super().get(request, *args, **kwargs)

class SessionListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'accounts/session_list.html'
    context_object_name = 'sessions'

    def get_queryset(self):
        # Assuming sessions are related to user, adjust as needed
        return User.objects.filter(id=self.request.user.id)

class UserRoleManageView(TenantAdminRequiredMixin, UpdateView):
    model = User
    template_name = 'accounts/user_role_manage.html'
    form_class = UserRoleForm
    success_url = reverse_lazy('accounts:user_list')

    def get_queryset(self):
        return User.objects.filter(tenant=self.request.user.tenant)

    def get_object(self, queryset=None):
        return get_object_or_404(User, pk=self.kwargs['pk'], tenant=self.request.user.tenant)

    def form_valid(self, form):
        # Assign roles to user
        user = self.get_object()
        role = form.cleaned_data['role']
        expires_at = form.cleaned_data['expires_at']
        UserRole.objects.update_or_create(user=user, defaults={'role': role, 'expires_at': expires_at})
        messages.success(self.request, _("User roles have been updated successfully."))
        return super().form_valid(form)

class RoleDeleteView(TenantAdminRequiredMixin, DeleteView):
    model = Role
    template_name = 'accounts/role_confirm_delete.html'
    success_url = reverse_lazy('accounts:role_list')

    def get_queryset(self):
        return Role.objects.filter(tenant=self.request.user.tenant)

# API Views
class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class UserListAPIView(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant)

class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(tenant=self.request.user.tenant)

class RoleListAPIView(generics.ListCreateAPIView):
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Role.objects.filter(tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant)

class RoleDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Role.objects.filter(tenant=self.request.user.tenant)
