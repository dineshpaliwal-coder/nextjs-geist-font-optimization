from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import User, Role, UserRole

class CustomUserCreationForm(UserCreationForm):
    """
    A form for creating new users with email as the username field.
    """
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone', 'job_title', 
                 'department', 'is_tenant_admin')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make email required
        self.fields['email'].required = True
        # Add help texts
        self.fields['email'].help_text = _("Required. Enter a valid email address.")
        self.fields['phone'].help_text = _("Enter phone number in international format: +1234567890")
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email is unique within the tenant
            tenant = getattr(self.instance, 'tenant', None)
            if tenant and User.objects.filter(email=email, tenant=tenant).exists():
                raise ValidationError(_("A user with this email already exists in your organization."))
        return email

class CustomUserChangeForm(UserChangeForm):
    """
    A form for updating users.
    """
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone', 'job_title', 
                 'department', 'language', 'timezone', 'date_format', 'time_format')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the password field from the form
        if 'password' in self.fields:
            del self.fields['password']

class RoleForm(forms.ModelForm):
    """
    Form for creating and updating roles.
    """
    class Meta:
        model = Role
        fields = ('name', 'description', 'can_manage_users', 'can_manage_roles',
                 'can_manage_clients', 'can_manage_projects', 'can_manage_invoices',
                 'can_manage_expenses', 'can_manage_settings', 'custom_permissions')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'custom_permissions': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        tenant = getattr(self.instance, 'tenant', None)
        if tenant:
            # Check if role name is unique within the tenant
            exists = Role.objects.filter(
                tenant=tenant,
                name__iexact=name
            ).exclude(pk=self.instance.pk).exists()
            if exists:
                raise ValidationError(_("A role with this name already exists in your organization."))
        return name

class UserRoleForm(forms.ModelForm):
    """
    Form for assigning roles to users.
    """
    class Meta:
        model = UserRole
        fields = ('role', 'expires_at')
        widgets = {
            'expires_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['role'].queryset = Role.objects.filter(tenant=tenant)

class TwoFactorSetupForm(forms.Form):
    """
    Form for setting up two-factor authentication.
    """
    code = forms.CharField(
        label=_("Verification Code"),
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'placeholder': _("Enter 6-digit code"),
            'autocomplete': 'off',
            'pattern': '[0-9]*',
            'inputmode': 'numeric'
        })
    )

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code.isdigit():
            raise ValidationError(_("Code must contain only numbers."))
        return code

class APIKeyGenerateForm(forms.Form):
    """
    Form for generating new API keys.
    """
    confirm = forms.BooleanField(
        label=_("I understand that generating a new API key will invalidate the existing one"),
        required=True
    )

class UserInviteForm(forms.Form):
    """
    Form for inviting new users to the tenant.
    """
    email = forms.EmailField(label=_("Email Address"))
    role = forms.ModelChoiceField(
        queryset=None,
        label=_("Initial Role"),
        required=False
    )
    message = forms.CharField(
        label=_("Personal Message"),
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False
    )

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['role'].queryset = Role.objects.filter(tenant=tenant)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        tenant = getattr(self, 'tenant', None)
        if tenant and User.objects.filter(email=email, tenant=tenant).exists():
            raise ValidationError(
                _("A user with this email already exists in your organization.")
            )
        return email

class UserBulkActionForm(forms.Form):
    """
    Form for performing bulk actions on selected users.
    """
    ACTIONS = (
        ('activate', _("Activate Selected Users")),
        ('deactivate', _("Deactivate Selected Users")),
        ('delete', _("Delete Selected Users")),
        ('force_password_reset', _("Force Password Reset")),
    )
    
    action = forms.ChoiceField(choices=ACTIONS, label=_("Action"))
    selected_users = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.MultipleHiddenInput
    )
    confirm = forms.BooleanField(
        label=_("I understand this action cannot be undone"),
        required=True
    )

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['selected_users'].queryset = User.objects.filter(tenant=tenant)

class UserPreferencesForm(forms.ModelForm):
    """
    Form for updating user preferences.
    """
    class Meta:
        model = User
        fields = ('language', 'timezone', 'date_format', 'time_format')
        widgets = {
            'language': forms.Select(attrs={'class': 'select2'}),
            'timezone': forms.Select(attrs={'class': 'select2'}),
        }

class SessionManagementForm(forms.Form):
    """
    Form for managing user sessions.
    """
    session_key = forms.CharField(widget=forms.HiddenInput)
    action = forms.ChoiceField(
        choices=(
            ('revoke', _("Revoke Session")),
            ('keep', _("Keep Session")),
        ),
        widget=forms.HiddenInput,
        initial='revoke'
    )
