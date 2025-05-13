from django.contrib import admin
from django.utils.html import format_html
from .models import Tenant, Domain, TenantSettings

class DomainInline(admin.TabularInline):
    model = Domain
    extra = 1
    fields = ('domain', 'is_primary', 'verified', 'verification_method')
    readonly_fields = ('verified',)

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subscription_plan', 'subscription_status', 
                   'is_active', 'created_at', 'primary_domain', 'logo_preview')
    list_filter = ('is_active', 'subscription_plan', 'subscription_status', 
                  'created_at')
    search_fields = ('name', 'email', 'domains__domain')
    readonly_fields = ('created_at', 'updated_at', 'stripe_customer_id', 
                      'stripe_subscription_id')
    inlines = [DomainInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'email', 'phone', 'address', 'is_active')
        }),
        ('Branding', {
            'fields': ('logo', 'favicon', 'primary_color', 'secondary_color')
        }),
        ('Localization', {
            'fields': ('timezone', 'language', 'currency', 'date_format')
        }),
        ('Subscription', {
            'fields': ('subscription_plan', 'subscription_status', 
                      'subscription_end_date', 'max_users', 'max_storage')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_customer_id', 'stripe_subscription_id'),
            'classes': ('collapse',)
        }),
        ('Email Settings', {
            'fields': ('smtp_host', 'smtp_port', 'smtp_username', 
                      'smtp_password', 'smtp_use_tls'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" height="50"/>', obj.logo.url)
        return "No Logo"
    logo_preview.short_description = 'Logo'

    def primary_domain(self, obj):
        domain = obj.get_primary_domain()
        return domain.domain if domain else '-'
    primary_domain.short_description = 'Primary Domain'

    def save_model(self, request, obj, form, change):
        """
        Override save_model to handle password encryption for SMTP
        """
        if 'smtp_password' in form.changed_data:
            # Here you might want to encrypt the SMTP password
            pass
        super().save_model(request, obj, form, change)

@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('domain', 'tenant', 'is_primary', 'verified', 
                   'verification_method', 'created_at')
    list_filter = ('is_primary', 'verified', 'verification_method', 'created_at')
    search_fields = ('domain', 'tenant__name')
    readonly_fields = ('created_at', 'updated_at', 'verification_token')
    fieldsets = (
        ('Domain Information', {
            'fields': ('tenant', 'domain', 'is_primary', 'verified')
        }),
        ('SSL Configuration', {
            'fields': ('ssl_certificate', 'ssl_key'),
            'classes': ('collapse',)
        }),
        ('Verification', {
            'fields': ('verification_method', 'verification_token')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(TenantSettings)
class TenantSettingsAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'enable_projects', 'enable_tasks', 
                   'enable_invoicing', 'enable_support', 'force_2fa')
    list_filter = ('enable_projects', 'enable_tasks', 'enable_invoicing', 
                  'enable_support', 'force_2fa')
    search_fields = ('tenant__name',)
    fieldsets = (
        ('Tenant', {
            'fields': ('tenant',)
        }),
        ('Feature Flags', {
            'fields': ('enable_projects', 'enable_tasks', 'enable_invoicing',
                      'enable_support', 'enable_knowledge_base', 'enable_api_access')
        }),
        ('Email Notifications', {
            'fields': ('notify_on_new_client', 'notify_on_new_invoice',
                      'notify_on_new_ticket')
        }),
        ('Security', {
            'fields': ('force_2fa', 'password_expiry_days', 'session_timeout_minutes')
        }),
        ('Custom Fields', {
            'fields': ('custom_fields',),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        # Prevent manual creation as settings are auto-created with tenants
        return False
