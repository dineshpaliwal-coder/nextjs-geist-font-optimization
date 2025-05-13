from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
import uuid

class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    'created' and 'modified' fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class Tenant(TimeStampedModel):
    """
    The main tenant model for multi-tenancy support.
    Each tenant represents a separate organization/company.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100)
    is_active = models.BooleanField(default=True)
    
    # Branding
    logo = models.ImageField(upload_to='tenants/logos/', null=True, blank=True)
    favicon = models.ImageField(upload_to='tenants/favicons/', null=True, blank=True)
    primary_color = models.CharField(max_length=7, null=True, blank=True)
    secondary_color = models.CharField(max_length=7, null=True, blank=True)
    
    # Contact Information
    email = models.EmailField()
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    
    # Localization
    timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=10, choices=settings.LANGUAGES, default='en')
    currency = models.CharField(max_length=3, default='USD')
    date_format = models.CharField(max_length=20, default='Y-m-d')
    
    # Subscription and Limits
    subscription_plan = models.CharField(max_length=50, default='free')
    subscription_status = models.CharField(max_length=20, default='active')
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    max_users = models.IntegerField(default=5)
    max_storage = models.BigIntegerField(default=5 * 1024 * 1024 * 1024)  # 5GB in bytes
    
    # Integration Settings
    stripe_customer_id = models.CharField(max_length=100, null=True, blank=True)
    stripe_subscription_id = models.CharField(max_length=100, null=True, blank=True)
    
    # Email Settings
    smtp_host = models.CharField(max_length=255, null=True, blank=True)
    smtp_port = models.IntegerField(null=True, blank=True)
    smtp_username = models.CharField(max_length=255, null=True, blank=True)
    smtp_password = models.CharField(max_length=255, null=True, blank=True)
    smtp_use_tls = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Tenant'
        verbose_name_plural = 'Tenants'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_primary_domain(self):
        return self.domains.filter(is_primary=True).first()

    @property
    def domain(self):
        primary_domain = self.get_primary_domain()
        return primary_domain.domain if primary_domain else None

class Domain(TimeStampedModel):
    """
    Domain model for handling multiple domains per tenant.
    Allows for white-labeling and multiple access points to the same tenant.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='domains')
    domain = models.CharField(
        max_length=253,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$',
                message='Enter a valid domain name.',
            ),
        ]
    )
    is_primary = models.BooleanField(default=False)
    ssl_certificate = models.TextField(null=True, blank=True)
    ssl_key = models.TextField(null=True, blank=True)
    verified = models.BooleanField(default=False)
    verification_method = models.CharField(
        max_length=20,
        choices=[
            ('dns', 'DNS Record'),
            ('file', 'File Upload'),
        ],
        default='dns'
    )
    verification_token = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'Domain'
        verbose_name_plural = 'Domains'
        ordering = ['-is_primary', 'domain']

    def __str__(self):
        return self.domain

    def save(self, *args, **kwargs):
        # Ensure only one primary domain per tenant
        if self.is_primary:
            self.__class__.objects.filter(
                tenant=self.tenant,
                is_primary=True
            ).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs)

class TenantSettings(TimeStampedModel):
    """
    Additional settings specific to each tenant that might change frequently.
    Separated from the main Tenant model for performance reasons.
    """
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name='settings')
    
    # Feature Flags
    enable_projects = models.BooleanField(default=True)
    enable_tasks = models.BooleanField(default=True)
    enable_invoicing = models.BooleanField(default=True)
    enable_support = models.BooleanField(default=True)
    enable_knowledge_base = models.BooleanField(default=True)
    enable_api_access = models.BooleanField(default=False)
    
    # Email Notifications
    notify_on_new_client = models.BooleanField(default=True)
    notify_on_new_invoice = models.BooleanField(default=True)
    notify_on_new_ticket = models.BooleanField(default=True)
    
    # Security Settings
    force_2fa = models.BooleanField(default=False)
    password_expiry_days = models.IntegerField(default=90)
    session_timeout_minutes = models.IntegerField(default=60)
    
    # Custom Fields Configuration
    custom_fields = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = 'Tenant Settings'
        verbose_name_plural = 'Tenant Settings'

    def __str__(self):
        return f"Settings for {self.tenant.name}"
