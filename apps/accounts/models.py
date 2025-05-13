from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from apps.core.models import TimeStampedModel, Tenant
import uuid

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractUser, TimeStampedModel):
    """Custom User model for multi-tenant SaaS CRM."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None  # Remove username field
    email = models.EmailField(_('email address'), unique=True)
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True
    )
    
    # Personal Information
    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        blank=True
    )
    job_title = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    
    # Security and Access
    is_active = models.BooleanField(default=True)
    is_tenant_admin = models.BooleanField(
        default=False,
        help_text=_('Designates whether this user is an admin for their tenant.')
    )
    force_password_change = models.BooleanField(
        default=False,
        help_text=_('Force user to change password on next login.')
    )
    password_changed_at = models.DateTimeField(null=True, blank=True)
    
    # 2FA Settings
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True)
    
    # Preferences
    language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    date_format = models.CharField(max_length=20, default='Y-m-d')
    time_format = models.CharField(max_length=20, default='H:i')
    
    # API Access
    api_key = models.UUIDField(default=uuid.uuid4, unique=True)
    api_access_enabled = models.BooleanField(default=False)
    
    # Session Management
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_active = models.DateTimeField(null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['email']

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Return the full name."""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def save(self, *args, **kwargs):
        if self.tenant and self.is_superuser:
            # Prevent superusers from being associated with a tenant
            self.tenant = None
        super().save(*args, **kwargs)

class Role(TimeStampedModel):
    """Role model for defining user permissions within a tenant."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='roles')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Module Permissions
    can_manage_users = models.BooleanField(default=False)
    can_manage_roles = models.BooleanField(default=False)
    can_manage_clients = models.BooleanField(default=False)
    can_manage_projects = models.BooleanField(default=False)
    can_manage_invoices = models.BooleanField(default=False)
    can_manage_expenses = models.BooleanField(default=False)
    can_manage_settings = models.BooleanField(default=False)
    
    # Custom permissions stored as JSON
    custom_permissions = models.JSONField(default=dict)

    class Meta:
        unique_together = ('tenant', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.tenant.name})"

class UserRole(TimeStampedModel):
    """
    Through model for assigning roles to users with additional metadata.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_roles')
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='role_assignments'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'role')
        ordering = ['-assigned_at']

    def __str__(self):
        return f"{self.user.email} - {self.role.name}"

class LoginAttempt(TimeStampedModel):
    """
    Model to track user login attempts for security monitoring.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='login_attempts',
        null=True
    )
    email = models.EmailField()  # Store email even for failed attempts
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    successful = models.BooleanField(default=False)
    failure_reason = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        status = 'successful' if self.successful else 'failed'
        return f"{self.email} - {status} login from {self.ip_address}"
